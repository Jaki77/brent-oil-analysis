# Brent Oil Price Analysis Dashboard

## Interactive Dashboard for Bayesian Change Point Detection and Event Impact Analysis

## Overview

The dashboard visualizes the impact of geopolitical and economic events on Brent crude oil prices using Bayesian change point detection. Built with Flask (backend) and React (frontend), it provides stakeholders with interactive tools to explore historical price data, detected change points, and quantified event impacts.

## Features

### Backend (Flask API)
- ✅ RESTful API for historical price data
- ✅ Event correlation and impact calculation
- ✅ Change point detection results
- ✅ Volatility analysis endpoints
- ✅ Real-time data filtering

### Frontend (React)
- ✅ Interactive price chart with event highlighting
- ✅ Change point visualization with probability scores
- ✅ Event timeline with impact metrics
- ✅ Volatility regime indicator
- ✅ Date range filtering and presets
- ✅ Event type filtering
- ✅ Responsive design (desktop, tablet, mobile)
- ✅ Drill-down capability for detailed insights

## Tech Stack

### Backend
- Flask 2.3.3
- Flask-CORS
- Pandas/NumPy for data processing
- PyMC/ArviZ for model integration
- Gunicorn (production)

### Frontend
- React 18.2
- Recharts for visualization
- React DatePicker
- React Select
- Bootstrap 5
- Axios for API calls

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Clone Repository
```bash
git clone https://github.com/Jaki77/brent-oil-analysis.git
cd brent-oil-analysis
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run Flask development server
python app.py
```

### 3. Frontend Setup
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start React development server
npm start
```