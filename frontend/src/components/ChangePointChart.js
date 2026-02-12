import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList
} from 'recharts';
import { Card, Badge, ListGroup } from 'react-bootstrap';
import moment from 'moment';

const ChangePointChart = ({ changePoints, onSelect }) => {
  const [chartData, setChartData] = useState([]);
  const [selectedCP, setSelectedCP] = useState(null);

  useEffect(() => {
    if (changePoints && changePoints.length > 0) {
      // Sort by probability and take top 10
      const sorted = [...changePoints]
        .sort((a, b) => b.probability - a.probability)
        .slice(0, 10)
        .map((cp, index) => ({
          ...cp,
          displayDate: moment(cp.date).format('MMM YYYY'),
          shortDate: moment(cp.date).format('YYYY-MM-DD'),
          formattedDate: moment(cp.date).format('MMMM DD, YYYY'),
          probabilityValue: (cp.probability * 100).toFixed(1),
          impactColor: cp.impact_pct > 0 ? '#28a745' : '#dc3545',
          index: index + 1
        }));
      setChartData(sorted);
    }
  }, [changePoints]);

  const handleBarClick = (data) => {
    setSelectedCP(data);
    onSelect(data);
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="change-point-tooltip">
          <h6>{data.formattedDate}</h6>
          <div className="tooltip-content">
            <p>
              <strong>Probability:</strong>{' '}
              <span style={{ color: '#4C72B0' }}>{data.probabilityValue}%</span>
            </p>
            {data.mean_before && (
              <p>
                <strong>Mean Price Before:</strong> ${data.mean_before.toFixed(2)}
              </p>
            )}
            {data.mean_after && (
              <p>
                <strong>Mean Price After:</strong> ${data.mean_after.toFixed(2)}
              </p>
            )}
            {data.impact_pct && (
              <p>
                <strong>Impact:</strong>{' '}
                <span style={{ color: data.impactColor }}>
                  {data.impact_pct > 0 ? '+' : ''}{data.impact_pct.toFixed(1)}%
                </span>
              </p>
            )}
            {data.correlated_event && (
              <p>
                <strong>Associated Event:</strong> {data.correlated_event}
                {data.correlation_days && (
                  <span className="text-muted">
                    {' '}
                    ({Math.abs(data.correlation_days)} days{' '}
                    {data.correlation_days > 0 ? 'after' : 'before'})
                  </span>
                )}
              </p>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const getBarColor = (entry) => {
    if (selectedCP?.date === entry.date) {
      return '#C44E52'; // Highlighted
    }
    if (entry.impact_pct > 20) return '#28a745'; // Strong positive
    if (entry.impact_pct > 5) return '#5cb85c'; // Positive
    if (entry.impact_pct < -20) return '#dc3545'; // Strong negative
    if (entry.impact_pct < -5) return '#f0ad4e'; // Negative
    return '#6c757d'; // Neutral
  };

  return (
    <div className="change-point-chart">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 60, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis 
            type="number" 
            domain={[0, 100]} 
            tickFormatter={(value) => `${value}%`}
          />
          <YAxis 
            type="category" 
            dataKey="displayDate" 
            width={80}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="probabilityValue" 
            onClick={handleBarClick}
            radius={[0, 4, 4, 0]}
            cursor="pointer"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={getBarColor(entry)}
                stroke={selectedCP?.date === entry.date ? '#000' : 'none'}
                strokeWidth={2}
              />
            ))}
            <LabelList 
              dataKey="probabilityValue" 
              position="right" 
              formatter={(value) => `${value}%`}
              style={{ fontSize: 11, fill: '#495057' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Change Point Details */}
      <div className="change-point-details mt-3">
        <h6 className="section-title">Detected Change Points</h6>
        <ListGroup variant="flush">
          {changePoints && changePoints.slice(0, 5).map((cp, idx) => (
            <ListGroup.Item 
              key={idx}
              className={`change-point-item ${selectedCP?.date === cp.date ? 'active' : ''}`}
              onClick={() => handleBarClick(cp)}
              action
            >
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <strong>{moment(cp.date).format('MMM DD, YYYY')}</strong>
                  <br />
                  <small className="text-muted">
                    {cp.correlated_event || 'No direct event correlation'}
                  </small>
                </div>
                <div className="text-end">
                  <Badge 
                    bg={cp.probability > 0.9 ? 'success' : cp.probability > 0.8 ? 'warning' : 'secondary'}
                    className="mb-1"
                  >
                    {(cp.probability * 100).toFixed(0)}% confidence
                  </Badge>
                  <br />
                  <span 
                    className="impact-badge"
                    style={{ 
                      color: cp.impact_pct > 0 ? '#28a745' : '#dc3545',
                      fontWeight: 'bold'
                    }}
                  >
                    {cp.impact_pct > 0 ? '▲' : '▼'} {Math.abs(cp.impact_pct || 0).toFixed(1)}%
                  </span>
                </div>
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </div>

      {/* Summary Statistics */}
      {changePoints && changePoints.length > 0 && (
        <div className="change-point-summary mt-3 p-2 bg-light rounded">
          <div className="d-flex justify-content-between">
            <span>
              <strong>Total Detected:</strong> {changePoints.length}
            </span>
            <span>
              <strong>High Confidence (≥90%):</strong>{' '}
              {changePoints.filter(cp => cp.probability >= 0.9).length}
            </span>
            <span>
              <strong>Event Correlation:</strong>{' '}
              {changePoints.filter(cp => cp.correlated_event).length}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChangePointChart;