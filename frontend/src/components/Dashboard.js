import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert } from 'react-bootstrap';
import { 
  priceAPI, 
  eventAPI, 
  changePointAPI, 
  summaryAPI, 
  volatilityAPI 
} from '../services/api';
import PriceChart from './PriceChart';
import ChangePointChart from './ChangePointChart';
import EventTimeline from './EventTimeline';
import VolatilityChart from './VolatilityChart';
import ImpactMetrics from './ImpactMetrics';
import DateRangePicker from './DateRangePicker';
import EventFilter from './EventFilter';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/dashboard.css';

const Dashboard = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [priceData, setPriceData] = useState(null);
  const [events, setEvents] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [summary, setSummary] = useState(null);
  const [volatilityData, setVolatilityData] = useState(null);
  const [eventTypes, setEventTypes] = useState([]);
  
  // Filter states
  const [dateRange, setDateRange] = useState({
    start: '1987-05-20',
    end: '2022-09-30'
  });
  const [selectedEventType, setSelectedEventType] = useState('all');
  const [minProbability, setMinProbability] = useState(0.8);
  const [highlightedEvent, setHighlightedEvent] = useState(null);

  // Load initial data
  useEffect(() => {
    fetchAllData();
  }, []);

  // Fetch data when filters change
  useEffect(() => {
    fetchFilteredData();
  }, [dateRange, selectedEventType, minProbability]);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [
        summaryRes,
        eventTypesRes,
        initialPriceRes,
        initialEventsRes,
        initialChangePointsRes,
        volatilityRes
      ] = await Promise.all([
        summaryAPI.getSummary(),
        eventAPI.getEventTypes(),
        priceAPI.getPrices(dateRange.start, dateRange.end),
        eventAPI.getEvents(selectedEventType, dateRange.start, dateRange.end),
        changePointAPI.getChangePoints(minProbability),
        volatilityAPI.getVolatility()
      ]);

      setSummary(summaryRes);
      setEventTypes(eventTypesRes.types || []);
      setPriceData(initialPriceRes);
      setEvents(initialEventsRes.events || []);
      setChangePoints(initialChangePointsRes.change_points || []);
      setVolatilityData(volatilityRes);
      
    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFilteredData = async () => {
    try {
      const [priceRes, eventsRes, changePointsRes] = await Promise.all([
        priceAPI.getPrices(dateRange.start, dateRange.end),
        eventAPI.getEvents(selectedEventType, dateRange.start, dateRange.end),
        changePointAPI.getChangePoints(minProbability)
      ]);

      setPriceData(priceRes);
      setEvents(eventsRes.events || []);
      setChangePoints(changePointsRes.change_points || []);
    } catch (err) {
      console.error('Error fetching filtered data:', err);
    }
  };

  const handleDateRangeChange = (start, end) => {
    setDateRange({ start, end });
  };

  const handleEventTypeChange = (type) => {
    setSelectedEventType(type);
  };

  const handleEventHighlight = (event) => {
    setHighlightedEvent(event);
  };

  if (loading) {
    return (
      <Container className="dashboard-loading">
        <Spinner animation="border" variant="primary" />
        <h3>Loading Brent Oil Price Analysis...</h3>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="dashboard-error">
        <Alert variant="danger">
          <Alert.Heading>Error Loading Dashboard</Alert.Heading>
          <p>{error}</p>
        </Alert>
      </Container>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <Container>
          <h1>Brent Oil Price Analysis Dashboard</h1>
          <p className="subtitle">
            Bayesian Change Point Detection & Event Impact Analysis
          </p>
        </Container>
      </div>

      <Container fluid className="dashboard-content">
        {/* Key Metrics Row */}
        {summary && (
          <Row className="metrics-row">
            <Col md={3}>
              <Card className="metric-card">
                <Card.Body>
                  <h6>Current Price</h6>
                  <h2>${summary.latest?.price?.toFixed(2) || 'N/A'}</h2>
                  <span className={`trend ${summary.latest?.return_1d > 0 ? 'positive' : 'negative'}`}>
                    {summary.latest?.return_1d > 0 ? '▲' : '▼'} 
                    {Math.abs(summary.latest?.return_1d || 0).toFixed(2)}%
                  </span>
                  <small>vs yesterday</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="metric-card">
                <Card.Body>
                  <h6>Volatility Regime</h6>
                  <h2 className={summary.volatility_regime?.regime?.toLowerCase()}>
                    {summary.volatility_regime?.regime || 'N/A'}
                  </h2>
                  <span>Current: {(summary.volatility_regime?.current * 100)?.toFixed(1)}%</span>
                  <small>vs {(summary.volatility_regime?.historical_avg * 100)?.toFixed(1)}% avg</small>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="metric-card">
                <Card.Body>
                  <h6>Total Events</h6>
                  <h2>{summary.total_events || 0}</h2>
                  <span>{summary.detected_change_points || 0} detected change points</span>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="metric-card">
                <Card.Body>
                  <h6>Date Range</h6>
                  <h6 style={{ fontSize: '1.1rem' }}>
                    {summary.date_range?.start} <br />
                    to {summary.date_range?.end}
                  </h6>
                  <span>{summary.total_days?.toLocaleString()} trading days</span>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}

        {/* Filters Row */}
        <Row className="filters-row">
          <Col md={6}>
            <DateRangePicker 
              onDateRangeChange={handleDateRangeChange}
              initialStart={dateRange.start}
              initialEnd={dateRange.end}
            />
          </Col>
          <Col md={6}>
            <EventFilter 
              eventTypes={eventTypes}
              selectedType={selectedEventType}
              onTypeChange={handleEventTypeChange}
              minProbability={minProbability}
              onProbabilityChange={setMinProbability}
            />
          </Col>
        </Row>

        {/* Main Charts Row */}
        <Row className="charts-row">
          <Col lg={8}>
            <Card className="chart-card">
              <Card.Header>
                <h5>Brent Oil Price with Change Points</h5>
              </Card.Header>
              <Card.Body>
                <PriceChart 
                  data={priceData}
                  changePoints={changePoints}
                  events={events}
                  highlightedEvent={highlightedEvent}
                  onEventClick={handleEventHighlight}
                />
              </Card.Body>
            </Card>
          </Col>
          <Col lg={4}>
            <Card className="chart-card">
              <Card.Header>
                <h5>Detected Change Points</h5>
              </Card.Header>
              <Card.Body>
                <ChangePointChart 
                  changePoints={changePoints}
                  onSelect={handleEventHighlight}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Secondary Charts Row */}
        <Row className="charts-row">
          <Col lg={6}>
            <Card className="chart-card">
              <Card.Header>
                <h5>Event Timeline & Impact</h5>
              </Card.Header>
              <Card.Body>
                <EventTimeline 
                  events={events}
                  changePoints={changePoints}
                  onEventSelect={handleEventHighlight}
                />
              </Card.Body>
            </Card>
          </Col>
          <Col lg={6}>
            <Card className="chart-card">
              <Card.Header>
                <h5>Volatility Analysis</h5>
              </Card.Header>
              <Card.Body>
                <VolatilityChart 
                  volatilityData={volatilityData}
                  events={events}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Impact Analysis Row */}
        <Row className="impact-row">
          <Col lg={12}>
            <Card className="impact-card">
              <Card.Header>
                <h5>Event Impact Analysis</h5>
              </Card.Header>
              <Card.Body>
                <ImpactMetrics 
                  events={events}
                  changePoints={changePoints}
                  highlightedEvent={highlightedEvent}
                />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Footer */}
      <div className="dashboard-footer">
        <Container>
          <Row>
            <Col md={6}>
              <p>© 2026 Birhan Energies Consulting</p>
            </Col>
            <Col md={6} className="text-end">
              <p>Data Source: Brent Crude Oil Historical Prices</p>
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default Dashboard;