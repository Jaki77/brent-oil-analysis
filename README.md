# Brent Oil Price Analysis: Geopolitical Event Impact Study

## Project Overview
This project analyzes how major geopolitical events, OPEC decisions, and economic shocks affect Brent crude oil prices using Bayesian change point detection models. The analysis spans from 1987 to 2022 and provides data-driven insights for investors, policymakers, and energy companies.

## Business Context
Birhan Energies specializes in providing data-driven insights to energy sector stakeholders. This analysis helps:
- **Investors**: Make informed decisions and manage risks
- **Policymakers**: Develop strategies for economic stability and energy security
- **Energy Companies**: Plan operations and secure supply chains

## Key Objectives
1. Identify key events significantly impacting Brent oil prices
2. Quantify event impacts using statistical methods
3. Provide clear, data-driven insights for strategic decision-making

## Data Sources
1. **Brent Oil Prices**: Daily prices from May 20, 1987 to September 30, 2022
2. **Historical Events**: 15+ geopolitical and economic events compiled from reliable sources

## Repository Structure
```bash
brent-oil-analysis/
├── data/ # Raw and processed data
├── notebooks/ # Jupyter notebooks for analysis
├── src/ # Source code modules
├── docs/ # Documentation
├── config/ # Configuration files
├── requirements.txt # Python dependencies
└── README.md # This file
```

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Jaki77/brent-oil-analysis.git
cd brent-oil-analysis
```
### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Analysis Workflow
1. **Data Loading & Preprocessing**: Clean and prepare time series data
2. **Exploratory Analysis**: Visualize trends, test stationarity, analyze volatility
3. **Event Research**: Compile and integrate historical events
4. **Bayesian Modeling**: Implement change point detection using PyMC
5. **Impact Quantification**: Correlate change points with events
6. **Insight Generation**: Create visualizations and actionable insights

## Key Deliverables
- Interactive dashboard for exploring change points
- Technical report with detailed methodology
- Executive summary for stakeholders
- Model validation and comparison results

