import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { Button, ButtonGroup } from 'react-bootstrap';
import moment from 'moment';
import 'react-datepicker/dist/react-datepicker.css';

const DateRangePicker = ({ onDateRangeChange, initialStart, initialEnd }) => {
  const [startDate, setStartDate] = useState(moment(initialStart).toDate());
  const [endDate, setEndDate] = useState(moment(initialEnd).toDate());

  const handleApply = () => {
    onDateRangeChange(
      moment(startDate).format('YYYY-MM-DD'),
      moment(endDate).format('YYYY-MM-DD')
    );
  };

  const handlePresetRange = (preset) => {
    const end = new Date();
    let start = new Date();
    
    switch (preset) {
      case '1Y':
        start.setFullYear(end.getFullYear() - 1);
        break;
      case '5Y':
        start.setFullYear(end.getFullYear() - 5);
        break;
      case '10Y':
        start.setFullYear(end.getFullYear() - 10);
        break;
      case 'ALL':
        start = moment('1987-05-20').toDate();
        break;
      default:
        break;
    }
    
    setStartDate(start);
    setEndDate(end);
    onDateRangeChange(moment(start).format('YYYY-MM-DD'), moment(end).format('YYYY-MM-DD'));
  };

  useEffect(() => {
    handleApply();
  }, []);

  return (
    <div className="date-range-picker">
      <div className="d-flex align-items-center">
        <div className="date-inputs">
          <DatePicker
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            className="form-control"
            dateFormat="yyyy-MM-dd"
            placeholderText="Start Date"
          />
          <span className="mx-2">to</span>
          <DatePicker
            selected={endDate}
            onChange={(date) => setEndDate(date)}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            className="form-control"
            dateFormat="yyyy-MM-dd"
            placeholderText="End Date"
          />
        </div>
        
        <ButtonGroup className="preset-buttons">
          <Button variant="outline-secondary" size="sm" onClick={() => handlePresetRange('1Y')}>
            1Y
          </Button>
          <Button variant="outline-secondary" size="sm" onClick={() => handlePresetRange('5Y')}>
            5Y
          </Button>
          <Button variant="outline-secondary" size="sm" onClick={() => handlePresetRange('10Y')}>
            10Y
          </Button>
          <Button variant="outline-secondary" size="sm" onClick={() => handlePresetRange('ALL')}>
            ALL
          </Button>
        </ButtonGroup>
        
        <Button variant="primary" size="sm" onClick={handleApply} className="ms-2">
          Apply
        </Button>
      </div>
    </div>
  );
};

export default DateRangePicker;