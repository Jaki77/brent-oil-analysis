import React, { useState, useEffect } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  ReferenceLine,
  Label
} from 'recharts';
import { Badge, ButtonGroup, ToggleButton } from 'react-bootstrap';
import moment from 'moment';

const EventTimeline = ({ events, changePoints, onEventSelect }) => {
  const [timelineData, setTimelineData] = useState([]);
  const [viewMode, setViewMode] = useState('impact'); // 'impact' or 'volatility'
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    if (events && events.length > 0) {
      // Process events for timeline visualization
      const processed = events
        .filter(event => event.impact) // Only events with impact data
        .map((event, index) => {
          const magnitude = Math.abs(event.impact?.percent_change || 0);
          const size = Math.min(Math.max(magnitude / 5, 10), 50);
          const hasChangePoint = changePoints?.some(
            cp => Math.abs(moment(cp.date).diff(moment(event.date), 'days')) <= 30
          );
          
          return {
            id: index,
            date: event.date,
            timestamp: moment(event.date).valueOf(),
            year: moment(event.date).year(),
            name: event.name,
            type: event.type,
            region: event.region,
            impact: event.impact?.percent_change || 0,
            impactAbs: event.impact?.price_change || 0,
            priceBefore: event.impact?.price_before || 0,
            priceAfter: event.impact?.price_after || 0,
            volatilityBefore: event.impact?.volatility_before || 0,
            volatilityAfter: event.impact?.volatility_after || 0,
            magnitude: magnitude,
            size: size,
            hasChangePoint: hasChangePoint,
            direction: event.impact_direction,
            formattedDate: moment(event.date).format('MMM DD, YYYY')
          };
        })
        .sort((a, b) => a.timestamp - b.timestamp);
      
      setTimelineData(processed);
    }
  }, [events, changePoints]);

  const handleScatterClick = (data) => {
    setSelectedEvent(data);
    onEventSelect(data);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="event-timeline-tooltip">
          <h6>{data.name}</h6>
          <p className="date">{data.formattedDate}</p>
          <p className="type">
            <Badge bg="secondary">{data.type}</Badge>
            {data.hasChangePoint && (
              <Badge bg="success" className="ms-1">Change Point</Badge>
            )}
          </p>
          <div className="impact-details">
            <p>
              <strong>Price Impact:</strong>{' '}
              <span style={{ color: data.impact > 0 ? '#28a745' : '#dc3545' }}>
                {data.impact > 0 ? '+' : ''}{data.impact.toFixed(1)}%
              </span>
            </p>
            <p>
              <strong>Price Change:</strong> ${data.impactAbs.toFixed(2)}
            </p>
            <p>
              <strong>Before → After:</strong> ${data.priceBefore.toFixed(2)} → ${data.priceAfter.toFixed(2)}
            </p>
            <p>
              <strong>Volatility Change:</strong>{' '}
              <span style={{ color: data.volatilityAfter > data.volatilityBefore ? '#f0ad4e' : '#5cb85c' }}>
                {(data.volatilityAfter * 100).toFixed(1)}% vs {(data.volatilityBefore * 100).toFixed(1)}%
              </span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  const getEventColor = (type, direction) => {
    if (direction === 'positive') return '#28a745';
    if (direction === 'negative') return '#dc3545';
    
    // Fallback to type-based coloring
    const colorMap = {
      'Geopolitical Conflict': '#C44E52',
      'Financial Crisis': '#8172B2',
      'Policy Decision': '#4C72B0',
      'Natural Disaster': '#CCB974',
      'Global Health Crisis': '#64B5CD',
      'Sanctions Change': '#55A868'
    };
    return colorMap[type] || '#6c757d';
  };

  // Group events by year for summary
  const eventsByYear = timelineData.reduce((acc, event) => {
    const year = event.year;
    if (!acc[year]) {
      acc[year] = { total: 0, positive: 0, negative: 0, avgImpact: 0 };
    }
    acc[year].total += 1;
    if (event.impact > 0) acc[year].positive += 1;
    if (event.impact < 0) acc[year].negative += 1;
    acc[year].avgImpact = (acc[year].avgImpact * (acc[year].total - 1) + event.impact) / acc[year].total;
    return acc;
  }, {});

  return (
    <div className="event-timeline">
      {/* View Mode Toggle */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <ButtonGroup size="sm">
          <ToggleButton
            id="toggle-impact"
            type="radio"
            variant="outline-primary"
            name="radio"
            value="impact"
            checked={viewMode === 'impact'}
            onChange={(e) => setViewMode('impact')}
          >
            Impact View
          </ToggleButton>
          <ToggleButton
            id="toggle-volatility"
            type="radio"
            variant="outline-primary"
            name="radio"
            value="volatility"
            checked={viewMode === 'volatility'}
            onChange={(e) => setViewMode('volatility')}
          >
            Volatility View
          </ToggleButton>
        </ButtonGroup>
        <span className="text-muted small">
          Bubble size = {viewMode === 'impact' ? 'Impact magnitude' : 'Volatility change'}
        </span>
      </div>

      {/* Timeline Scatter Plot */}
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="timestamp" 
            domain={['dataMin', 'dataMax']}
            tickFormatter={(timestamp) => moment(timestamp).format('YYYY')}
            type="number"
            label={{ value: 'Year', position: 'insideBottom', offset: -10 }}
          />
          <YAxis 
            dataKey={viewMode === 'impact' ? 'impact' : 'volatilityAfter'} 
            tickFormatter={(value) => 
              viewMode === 'impact' 
                ? `${value.toFixed(0)}%` 
                : `${(value * 100).toFixed(0)}%`
            }
            label={{ 
              value: viewMode === 'impact' ? 'Price Impact (%)' : 'Volatility', 
              angle: -90, 
              position: 'insideLeft' 
            }}
          />
          <ZAxis 
            dataKey={viewMode === 'impact' ? 'magnitude' : 'size'} 
            range={[20, 80]} 
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Zero impact reference line */}
          {viewMode === 'impact' && (
            <ReferenceLine y={0} stroke="red" strokeDasharray="3 3">
              <Label value="No Impact" position="right" fill="red" fontSize={10} />
            </ReferenceLine>
          )}
          
          {/* Event bubbles */}
          <Scatter 
            data={timelineData} 
            onClick={handleScatterClick}
            cursor="pointer"
          >
            {timelineData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={getEventColor(entry.type, entry.direction)}
                fillOpacity={selectedEvent?.id === entry.id ? 1 : 0.7}
                stroke={selectedEvent?.id === entry.id ? '#000' : 'none'}
                strokeWidth={2}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      {/* Event Summary by Decade */}
      <div className="event-summary mt-4">
        <h6 className="section-title">Event Impact Summary by Period</h6>
        <div className="decade-grid">
          {[1990, 2000, 2010, 2020].map((decade) => {
            const decadeEvents = timelineData.filter(
              e => e.year >= decade && e.year < decade + 10
            );
            if (decadeEvents.length === 0) return null;
            
            const avgImpact = decadeEvents.reduce((sum, e) => sum + e.impact, 0) / decadeEvents.length;
            const positiveEvents = decadeEvents.filter(e => e.impact > 0).length;
            const negativeEvents = decadeEvents.filter(e => e.impact < 0).length;
            
            return (
              <div key={decade} className="decade-card">
                <h6>{decade}s</h6>
                <div className="stats">
                  <div className="stat">
                    <span className="label">Events:</span>
                    <span className="value">{decadeEvents.length}</span>
                  </div>
                  <div className="stat">
                    <span className="label">Avg Impact:</span>
                    <span className="value" style={{ 
                      color: avgImpact > 0 ? '#28a745' : '#dc3545' 
                    }}>
                      {avgImpact > 0 ? '+' : ''}{avgImpact.toFixed(1)}%
                    </span>
                  </div>
                  <div className="stat">
                    <span className="label">Positive/Negative:</span>
                    <span className="value">
                      <span style={{ color: '#28a745' }}>{positiveEvents}</span>
                      {' / '}
                      <span style={{ color: '#dc3545' }}>{negativeEvents}</span>
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Event Type Legend */}
      <div className="event-legend mt-3">
        <div className="d-flex flex-wrap gap-2">
          {['Geopolitical Conflict', 'Financial Crisis', 'Policy Decision', 
            'Natural Disaster', 'Global Health Crisis', 'Sanctions Change'].map(type => (
            <div key={type} className="legend-item">
              <span 
                className="color-dot" 
                style={{ backgroundColor: getEventColor(type, 'neutral') }}
              />
              <span className="label">{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EventTimeline;