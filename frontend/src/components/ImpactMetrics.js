import React from 'react';
import { Table, Badge, ProgressBar } from 'react-bootstrap';
import moment from 'moment';

const ImpactMetrics = ({ events, changePoints, highlightedEvent }) => {
  
  const getImpactColor = (percentChange) => {
    if (percentChange > 20) return 'success';
    if (percentChange > 5) return 'info';
    if (percentChange < -20) return 'danger';
    if (percentChange < -5) return 'warning';
    return 'secondary';
  };

  const getImpactIcon = (direction) => {
    if (direction === 'positive') return '▲';
    if (direction === 'negative') return '▼';
    return '◆';
  };

  // Merge events with change point detection
  const impactData = events
    .filter(event => event.impact)
    .map(event => {
      const associatedCP = changePoints.find(
        cp => Math.abs(moment(cp.date).diff(moment(event.date), 'days')) <= 30
      );
      
      return {
        ...event,
        changePointDetected: !!associatedCP,
        changePointProbability: associatedCP?.probability || null,
        impactMagnitude: event.impact?.percent_change || 0,
        impactAbs: event.impact?.price_change || 0,
        volatilityChange: event.impact?.volatility_after - event.impact?.volatility_before || 0
      };
    })
    .sort((a, b) => Math.abs(b.impactMagnitude) - Math.abs(a.impactMagnitude));

  return (
    <div className="impact-metrics">
      <Table hover responsive>
        <thead>
          <tr>
            <th>Event Date</th>
            <th>Event Name</th>
            <th>Type</th>
            <th>Price Impact</th>
            <th>% Change</th>
            <th>Volatility Impact</th>
            <th>Change Point</th>
          </tr>
        </thead>
        <tbody>
          {impactData.map((event, index) => (
            <tr 
              key={index}
              className={highlightedEvent?.date === event.date ? 'table-primary' : ''}
              style={{ cursor: 'pointer' }}
              onClick={() => window.dispatchEvent(new CustomEvent('highlightEvent', { detail: event }))}
            >
              <td>{moment(event.date).format('MMM DD, YYYY')}</td>
              <td>
                <strong>{event.name}</strong>
                <br />
                <small className="text-muted">{event.region}</small>
              </td>
              <td>
                <Badge bg="secondary">{event.type}</Badge>
              </td>
              <td>
                <span className={event.impact?.price_change > 0 ? 'text-success' : 'text-danger'}>
                  {getImpactIcon(event.impact_direction)}
                  {' '}${Math.abs(event.impact?.price_change || 0).toFixed(2)}
                </span>
                <br />
                <small>
                  ${event.impact?.price_before.toFixed(2)} → ${event.impact?.price_after.toFixed(2)}
                </small>
              </td>
              <td>
                <Badge bg={getImpactColor(event.impactMagnitude)}>
                  {event.impactMagnitude > 0 ? '+' : ''}{event.impactMagnitude.toFixed(1)}%
                </Badge>
                <ProgressBar 
                  now={Math.min(Math.abs(event.impactMagnitude), 100)} 
                  variant={getImpactColor(event.impactMagnitude)}
                  style={{ height: '4px', marginTop: '4px' }}
                />
              </td>
              <td>
                <span className={event.volatilityChange > 0 ? 'text-warning' : 'text-info'}>
                  {event.volatilityChange > 0 ? '▲' : '▼'}
                  {' '}{(Math.abs(event.volatilityChange) * 100).toFixed(1)}%
                </span>
              </td>
              <td>
                {event.changePointDetected ? (
                  <Badge bg="success">
                    ✓ {event.changePointProbability ? `${(event.changePointProbability * 100).toFixed(0)}%` : ''}
                  </Badge>
                ) : (
                  <Badge bg="light" text="dark">No</Badge>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      
      {impactData.length === 0 && (
        <div className="text-center text-muted p-4">
          No impact data available for the selected filters.
        </div>
      )}
    </div>
  );
};

export default ImpactMetrics;