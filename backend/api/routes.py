"""
API routes for Brent Oil Price Analysis Dashboard.
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from .utils import DataLoader, DataProcessor
from config import Config
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Initialize data loader
data_loader = DataLoader(
    Config.DATA_PATH,
    Config.EVENTS_PATH,
    Config.CHANGE_POINTS_PATH
)

# Load data
df = data_loader.load_price_data()
events_df = data_loader.load_event_data()
change_points = data_loader.load_change_points()

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': Config.API_TITLE,
        'version': Config.API_VERSION,
        'timestamp': pd.Timestamp.now().isoformat()
    })


@api_bp.route('/prices', methods=['GET'])
@cross_origin()
def get_prices():
    """Get historical price data with optional filtering."""
    try:
        # Get query parameters
        start_date = request.args.get('start', df['Date'].min().strftime('%Y-%m-%d'))
        end_date = request.args.get('end', df['Date'].max().strftime('%Y-%m-%d'))
        frequency = request.args.get('frequency', 'daily')  # daily, weekly, monthly
        
        # Filter by date range
        filtered_df = DataProcessor.filter_by_date_range(df, start_date, end_date)
        
        # Resample if needed
        if frequency == 'weekly':
            filtered_df = filtered_df.resample('W', on='Date').agg({
                'Price': 'mean',
                'Returns': 'mean',
                'Volatility_30d': 'mean'
            }).reset_index()
        elif frequency == 'monthly':
            filtered_df = filtered_df.resample('M', on='Date').agg({
                'Price': 'mean',
                'Returns': 'mean',
                'Volatility_30d': 'mean'
            }).reset_index()
        
        # Prepare response
        response = {
            'dates': filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'prices': filtered_df['Price'].round(2).tolist(),
            'returns': filtered_df['Returns'].round(3).fillna(0).tolist(),
            'volatility': filtered_df['Volatility_30d'].round(4).fillna(0).tolist(),
            'ma_30d': filtered_df['Price'].rolling(30).mean().round(2).fillna(0).tolist(),
            'metadata': {
                'total_points': len(filtered_df),
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'frequency': frequency
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in get_prices: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/events', methods=['GET'])
@cross_origin()
def get_events():
    """Get historical events with optional filtering."""
    try:
        # Get query parameters
        event_type = request.args.get('type', None)
        start_date = request.args.get('start', None)
        end_date = request.args.get('end', None)
        
        filtered_events = events_df.copy()
        
        # Filter by event type
        if event_type and event_type != 'all':
            filtered_events = filtered_events[filtered_events['event_type'] == event_type]
        
        # Filter by date range
        if start_date:
            filtered_events = filtered_events[filtered_events['event_date'] >= pd.to_datetime(start_date)]
        if end_date:
            filtered_events = filtered_events[filtered_events['event_date'] <= pd.to_datetime(end_date)]
        
        # Calculate impact metrics for each event
        events_list = []
        processor = DataProcessor()
        
        for _, event in filtered_events.iterrows():
            impact = processor.calculate_event_impact(df, event['event_date'])
            events_list.append({
                'id': event.get('id', _),
                'date': event['event_date'].strftime('%Y-%m-%d'),
                'name': event['event_name'],
                'type': event['event_type'],
                'region': event.get('region_org', 'Unknown'),
                'impact': impact,
                'description': event.get('description', ''),
                'expected_impact': event.get('expected_impact', ''),
                'impact_direction': event.get('impact_direction', 'neutral')
            })
        
        # Get unique event types for filters
        event_types = events_df['event_type'].unique().tolist()
        
        return jsonify({
            'events': events_list,
            'total': len(events_list),
            'event_types': event_types,
            'filters': {
                'type': event_type,
                'start': start_date,
                'end': end_date
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_events: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/change-points', methods=['GET'])
@cross_origin()
def get_change_points():
    """Get detected change points from Bayesian analysis."""
    try:
        # Get query parameters
        min_probability = float(request.args.get('min_probability', 0.8))
        
        # Filter by probability threshold
        filtered_cps = [cp for cp in change_points if cp.get('probability', 0) >= min_probability]
        
        # Enhance with event correlation
        enhanced_cps = []
        for cp in filtered_cps:
            cp_date = pd.to_datetime(cp['date'])
            
            # Find closest event
            time_diffs = abs(events_df['event_date'] - cp_date)
            closest_idx = time_diffs.idxmin()
            closest_diff = time_diffs[closest_idx].days
            
            if closest_diff <= 30:
                cp['correlated_event'] = events_df.iloc[closest_idx]['event_name']
                cp['correlation_days'] = closest_diff
            else:
                cp['correlated_event'] = None
                cp['correlation_days'] = None
            
            enhanced_cps.append(cp)
        
        return jsonify({
            'change_points': enhanced_cps,
            'total': len(enhanced_cps),
            'probability_threshold': min_probability
        })
        
    except Exception as e:
        logger.error(f"Error in get_change_points: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/summary', methods=['GET'])
@cross_origin()
def get_summary():
    """Get summary statistics and key metrics."""
    try:
        processor = DataProcessor()
        stats = processor.get_summary_statistics(df)
        
        # Add additional metrics
        stats['total_events'] = len(events_df)
        stats['detected_change_points'] = len(change_points)
        
        # Calculate volatility regime
        current_vol = df['Volatility_30d'].iloc[-1]
        historical_vol = df['Volatility_30d'].mean()
        
        stats['volatility_regime'] = {
            'current': current_vol,
            'historical_avg': historical_vol,
            'relative': current_vol / historical_vol,
            'regime': 'HIGH' if current_vol > historical_vol * 1.2 else \
                     'LOW' if current_vol < historical_vol * 0.8 else 'NORMAL'
        }
        
        # Latest price and trend
        stats['latest'] = {
            'date': df['Date'].iloc[-1].strftime('%Y-%m-%d'),
            'price': float(df['Price'].iloc[-1]),
            'return_1d': float(df['Returns'].iloc[-1]) if not pd.isna(df['Returns'].iloc[-1]) else 0,
            'return_5d': float(df['Returns'].iloc[-5:].sum()) if len(df) >= 5 else 0,
            'return_21d': float(df['Returns'].iloc[-21:].sum()) if len(df) >= 21 else 0
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error in get_summary: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/event-types', methods=['GET'])
@cross_origin()
def get_event_types():
    """Get available event types and counts."""
    try:
        type_counts = events_df['event_type'].value_counts().to_dict()
        
        return jsonify({
            'types': [
                {
                    'name': k,
                    'count': v,
                    'percentage': v / len(events_df) * 100
                }
                for k, v in type_counts.items()
            ],
            'total': len(events_df)
        })
        
    except Exception as e:
        logger.error(f"Error in get_event_types: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/volatility', methods=['GET'])
@cross_origin()
def get_volatility():
    """Get volatility analysis data."""
    try:
        # Calculate volatility by year
        df['Year'] = df['Date'].dt.year
        yearly_vol = df.groupby('Year')['Volatility_30d'].mean().dropna()
        
        # Calculate volatility by event type
        event_volatility = []
        for event_type in events_df['event_type'].unique():
            type_events = events_df[events_df['event_type'] == event_type]
            type_dates = type_events['event_date'].tolist()
            
            # Get volatility around these events
            vol_before = []
            vol_after = []
            
            for date in type_dates:
                mask_before = (df['Date'] >= date - pd.Timedelta(days=30)) & (df['Date'] < date)
                mask_after = (df['Date'] > date) & (df['Date'] <= date + pd.Timedelta(days=30))
                
                if mask_before.any():
                    vol_before.append(df[mask_before]['Volatility_30d'].mean())
                if mask_after.any():
                    vol_after.append(df[mask_after]['Volatility_30d'].mean())
            
            if vol_before and vol_after:
                event_volatility.append({
                    'event_type': event_type,
                    'volatility_before': float(np.mean(vol_before)),
                    'volatility_after': float(np.mean(vol_after)),
                    'change': float(np.mean(vol_after) - np.mean(vol_before)),
                    'percent_change': float((np.mean(vol_after) - np.mean(vol_before)) / np.mean(vol_before) * 100)
                })
        
        return jsonify({
            'yearly_volatility': {
                'years': yearly_vol.index.tolist(),
                'values': yearly_vol.values.tolist()
            },
            'event_volatility': event_volatility,
            'current_volatility': float(df['Volatility_30d'].iloc[-1]),
            'historical_avg_volatility': float(df['Volatility_30d'].mean())
        })
        
    except Exception as e:
        logger.error(f"Error in get_volatility: {e}")
        return jsonify({'error': str(e)}), 500