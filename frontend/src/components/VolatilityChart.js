import React, { useState, useEffect } from 'react';
import {
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush
} from 'recharts';
import { Row, Col, Card, Badge, ProgressBar } from 'react-bootstrap';
import moment from 'moment';

const VolatilityChart = ({ volatilityData, events }) => {
  const [chartData, setChartData] = useState([]);
  const [volatilityRegime, setVolatilityRegime] = useState(null);
  const [eventVolatilityImpact, setEventVolatilityImpact] = useState([]);

  useEffect(() => {
    if (volatilityData) {
      // Process yearly volatility data
      if (volatilityData.yearly_volatility) {
        const years = volatilityData.yearly_volatility.years || [];
        const values = volatilityData.yearly_volatility.values || [];
        
        const formatted = years.map((year, index) => ({
          year: year,
          volatility: (values[index] * 100).toFixed(1),
          volatilityValue: values[index],
          // Determine regime
          regime: values[index] > volatilityData.historical_avg_volatility * 1.2 
            ? 'High' 
            : values[index] < volatilityData.historical_avg_volatility * 0.8 
              ? 'Low' 
              : 'Normal'
        }));
        
        setChartData(formatted);
      }

      // Set current regime
      if (volatilityData.current_volatility && volatilityData.historical_avg_volatility) {
        const current = volatilityData.current_volatility;
        const avg = volatilityData.historical_avg_volatility;
        
        setVolatilityRegime({
          current: (current * 100).toFixed(1),
          avg: (avg * 100).toFixed(1),
          ratio: (current / avg).toFixed(2),
          regime: current > avg * 1.2 ? 'High' : current < avg * 0.8 ? 'Low' : 'Normal'
        });
      }

      // Process event volatility impacts
      if (volatilityData.event_volatility) {
        setEventVolatilityImpact(volatilityData.event_volatility);
      }
    }
  }, [volatilityData]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="volatility-tooltip">
          <h6>Year: {label}</h6>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              <strong>{entry.name}:</strong> {entry.value}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const getRegimeColor = (regime) => {
    switch (regime) {
      case 'High': return '#dc3545';
      case 'Low': return '#28a745';
      case 'Normal': return '#ffc107';
      default: return '#6c757d';
    }
  };

  // Add event markers to volatility chart
  const getEventMarkers = () => {
    if (!events || events.length === 0) return [];
    
    return events
      .filter(event => event.date && event.impact)
      .map(event => ({
        date: moment(event.date).year(),
        name: event.name,
        volatilityChange: event.impact?.volatility_after - event.impact?.volatility_before || 0
      }))
      .filter(marker => marker.date >= 1987 && marker.date <= 2022);
  };

  const eventMarkers = getEventMarkers();

  return (
    <div className="volatility-chart">
      {/* Current Volatility Regime Card */}
      {volatilityRegime && (
        <Card className="regime-card mb-3">
          <Card.Body>
            <Row>
              <Col md={6}>
                <h6 className="text-muted">Current Volatility Regime</h6>
                <h3 className={`regime-${volatilityRegime.regime.toLowerCase()}`}>
                  {volatilityRegime.regime}
                </h3>
                <p className="mb-0">
                  Current: <strong>{volatilityRegime.current}%</strong> (annualized)
                </p>
                <p>
                  Historical Avg: <strong>{volatilityRegime.avg}%</strong>
                </p>
              </Col>
              <Col md={6}>
                <div className="regime-indicator">
                  <div className="d-flex justify-content-between mb-1">
                    <span>Relative Volatility</span>
                    <span className="fw-bold">{volatilityRegime.ratio}x</span>
                  </div>
                  <ProgressBar 
                    now={Math.min(parseFloat(volatilityRegime.ratio) * 50, 100)} 
                    variant={
                      volatilityRegime.regime === 'High' ? 'danger' :
                      volatilityRegime.regime === 'Low' ? 'success' : 'warning'
                    }
                    style={{ height: '10px' }}
                  />
                  <div className="d-flex justify-content-between mt-2">
                    <small>Low (0.8x)</small>
                    <small>Normal (1.0x)</small>
                    <small>High (1.2x+)</small>
                  </div>
                </div>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* Volatility Timeline Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <ComposedChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis 
            tickFormatter={(value) => `${value}%`}
            domain={[0, 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Volatility Area */}
          <Area
            type="monotone"
            dataKey="volatility"
            name="Annualized Volatility"
            stroke="#8172B2"
            fill="#8172B2"
            fillOpacity={0.3}
          />
          
          {/* Volatility Line */}
          <Line
            type="monotone"
            dataKey="volatility"
            name="Volatility Trend"
            stroke="#4C72B0"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          
          {/* Regime Reference Lines */}
          {volatilityData?.historical_avg_volatility && (
            <>
              <ReferenceLine 
                y={volatilityData.historical_avg_volatility * 100} 
                stroke="#6c757d" 
                strokeDasharray="3 3"
                label={{ 
                  value: 'Historical Avg', 
                  position: 'right',
                  fill: '#6c757d',
                  fontSize: 11
                }}
              />
              <ReferenceLine 
                y={volatilityData.historical_avg_volatility * 120} 
                stroke="#dc3545" 
                strokeDasharray="3 3"
                label={{ 
                  value: 'High Regime', 
                  position: 'right',
                  fill: '#dc3545',
                  fontSize: 11
                }}
              />
              <ReferenceLine 
                y={volatilityData.historical_avg_volatility * 80} 
                stroke="#28a745" 
                strokeDasharray="3 3"
                label={{ 
                  value: 'Low Regime', 
                  position: 'right',
                  fill: '#28a745',
                  fontSize: 11
                }}
              />
            </>
          )}
          
          {/* Event Markers */}
          {eventMarkers.map((marker, index) => (
            <ReferenceLine
              key={`event-${index}`}
              x={marker.date}
              stroke="#FFA500"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{
                value: '📌',
                position: 'top',
                fontSize: 16
              }}
            />
          ))}
          
          <Brush 
            dataKey="year" 
            height={30} 
            stroke="#8884d8"
            startIndex={Math.max(0, chartData.length - 10)}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Event Volatility Impact Table */}
      {eventVolatilityImpact && eventVolatilityImpact.length > 0 && (
        <div className="event-volatility-impact mt-4">
          <h6 className="section-title">Volatility Impact by Event Type</h6>
          <div className="table-responsive">
            <table className="table table-sm table-hover">
              <thead>
                <tr>
                  <th>Event Type</th>
                  <th>Volatility Before</th>
                  <th>Volatility After</th>
                  <th>Change</th>
                  <th>% Change</th>
                </tr>
              </thead>
              <tbody>
                {eventVolatilityImpact.map((item, idx) => {
                  const change = ((item.volatility_after - item.volatility_before) * 100).toFixed(1);
                  const pctChange = item.percent_change?.toFixed(1);
                  
                  return (
                    <tr key={idx}>
                      <td>
                        <Badge bg="secondary">{item.event_type}</Badge>
                      </td>
                      <td>{(item.volatility_before * 100).toFixed(1)}%</td>
                      <td>{(item.volatility_after * 100).toFixed(1)}%</td>
                      <td>
                        <span style={{ color: change > 0 ? '#dc3545' : '#28a745' }}>
                          {change > 0 ? '▲' : '▼'} {Math.abs(change)}%
                        </span>
                      </td>
                      <td>
                        <span style={{ color: pctChange > 0 ? '#dc3545' : '#28a745' }}>
                          {pctChange > 0 ? '+' : ''}{pctChange}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Volatility Clustering Explanation */}
      <div className="volatility-insights mt-3 p-2 bg-light rounded">
        <small className="text-muted">
          <strong>💡 Volatility Insight:</strong> Oil markets exhibit significant volatility clustering. 
          High volatility periods tend to persist (2008-2009, 2020, 2022), while low volatility regimes 
          indicate market stability. Current regime: <strong className={`regime-${volatilityRegime?.regime?.toLowerCase()}`}>
          {volatilityRegime?.regime}</strong>.
        </small>
      </div>
    </div>
  );
};

export default VolatilityChart;