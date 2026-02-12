import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceDot
} from 'recharts';
import moment from 'moment';

const PriceChart = ({ 
  data, 
  changePoints, 
  events, 
  highlightedEvent,
  onEventClick 
}) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    if (data?.dates && data?.prices) {
      const formatted = data.dates.map((date, index) => ({
        date,
        price: data.prices[index],
        ma30: data.ma_30d?.[index],
        returns: data.returns?.[index],
        formattedDate: moment(date).format('MMM DD, YYYY')
      }));
      setChartData(formatted);
    }
  }, [data]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="date">{moment(label).format('MMMM DD, YYYY')}</p>
          <p className="price">Price: ${payload[0].value.toFixed(2)}</p>
          {payload[1] && (
            <p className="ma">30-day MA: ${payload[1].value.toFixed(2)}</p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="price-chart-container">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => moment(date).format('YYYY')}
            minTickGap={50}
          />
          <YAxis 
            domain={['auto', 'auto']}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Price Line */}
          <Line
            type="monotone"
            dataKey="price"
            stroke="#4C72B0"
            strokeWidth={1.5}
            dot={false}
            name="Brent Oil Price"
          />
          
          {/* Moving Average */}
          <Line
            type="monotone"
            dataKey="ma30"
            stroke="#55A868"
            strokeWidth={1}
            dot={false}
            name="30-day MA"
          />
          
          {/* Change Points */}
          {changePoints?.map((cp, index) => (
            <ReferenceLine
              key={`cp-${index}`}
              x={cp.date}
              stroke="#C44E52"
              strokeDasharray="5 5"
              strokeWidth={2}
              label={{
                value: '⚡',
                position: 'top',
                fill: '#C44E52',
                fontSize: 16
              }}
            />
          ))}
          
          {/* Events */}
          {events?.map((event, index) => {
            const isHighlighted = highlightedEvent?.date === event.date;
            return (
              <ReferenceDot
                key={`event-${index}`}
                x={event.date}
                y={data.prices[data.dates.indexOf(event.date)] || 0}
                r={isHighlighted ? 8 : 6}
                fill={isHighlighted ? '#C44E52' : '#FFA500'}
                stroke={isHighlighted ? '#FFF' : 'none'}
                strokeWidth={2}
                onClick={() => onEventClick(event)}
              >
                <title>{event.name}</title>
              </ReferenceDot>
            );
          })}
        </LineChart>
      </ResponsiveContainer>
      
      {/* Event Legend */}
      <div className="chart-legend">
        <span className="legend-item">
          <span className="dot" style={{ background: '#FFA500' }}></span>
          Events
        </span>
        <span className="legend-item">
          <span className="dot" style={{ background: '#C44E52' }}></span>
          Change Points
        </span>
        <span className="legend-item">
          <span className="dot" style={{ background: '#4C72B0' }}></span>
          Price
        </span>
      </div>
    </div>
  );
};

export default PriceChart;