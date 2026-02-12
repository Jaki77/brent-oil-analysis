import React from 'react';
import Select from 'react-select';
import { Form } from 'react-bootstrap';

const EventFilter = ({ 
  eventTypes, 
  selectedType, 
  onTypeChange,
  minProbability,
  onProbabilityChange
}) => {
  
  const typeOptions = [
    { value: 'all', label: 'All Event Types' },
    ...eventTypes.map(type => ({
      value: type.name,
      label: `${type.name} (${type.count})`
    }))
  ];

  const handleTypeChange = (selected) => {
    onTypeChange(selected?.value || 'all');
  };

  const probabilityOptions = [
    { value: 0.5, label: '≥ 50%' },
    { value: 0.8, label: '≥ 80%' },
    { value: 0.9, label: '≥ 90%' },
    { value: 0.95, label: '≥ 95%' }
  ];

  return (
    <div className="event-filter">
      <Form.Group>
        <Form.Label>Event Type</Form.Label>
        <Select
          options={typeOptions}
          value={typeOptions.find(opt => opt.value === selectedType)}
          onChange={handleTypeChange}
          isClearable={false}
          className="event-type-select"
        />
      </Form.Group>
      
      <Form.Group className="mt-2">
        <Form.Label>Change Point Probability</Form.Label>
        <Select
          options={probabilityOptions}
          value={probabilityOptions.find(opt => opt.value === minProbability)}
          onChange={(selected) => onProbabilityChange(selected.value)}
          isClearable={false}
          className="probability-select"
        />
      </Form.Group>
      
      <div className="mt-2 text-muted small">
        <span>Showing events with change point probability ≥ {(minProbability * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
};

export default EventFilter;