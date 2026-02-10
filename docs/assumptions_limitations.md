# Assumptions and Limitations Documentation

## Key Assumptions

### 1. Market Efficiency Assumption
We assume that Brent oil prices reflect all available information at each time point, following the Efficient Market Hypothesis (EMH). This implies:
- Prices adjust quickly to new information
- Historical prices cannot predict future prices beyond what is already reflected
- Market participants are rational and have access to all relevant information

### 2. Data Quality Assumption
We assume the provided daily price data is:
- Accurate and free from systematic measurement errors
- Complete for the entire period (no significant gaps)
- Representative of actual market transactions
- Consistent in calculation methodology over time

### 3. Event Timing Assumption
We assume geopolitical and economic events immediately affect oil prices, typically within:
- 0-3 days for major geopolitical events
- 1-5 days for economic policy announcements
- Longer periods for structural changes (e.g., technology shifts)

### 4. Independence Assumption
While acknowledging potential interactions, we initially assume each event's impact can be analyzed separately. We will:
- Test for event clustering effects
- Consider interaction terms in advanced models
- Use robustness checks to validate independence

### 5. Structural Break Assumption
We assume significant price changes detected by our models represent meaningful market regime shifts rather than:
- Temporary anomalies
- Measurement errors
- Illiquid trading periods

## Critical Limitations

### 1. Correlation vs. Causation Distinction
**This is the most important limitation:**

**What We Can Measure (Correlation):**
- Temporal coincidence between events and price changes
- Statistical significance of price movements around events
- Magnitude of price changes following events

**What We Cannot Prove (Causation):**
- That the event **caused** the price change (could be coincidence)
- That no other factors influenced the price change
- The exact mechanism through which the event affected prices

**Requirements for Causal Inference:**
1. **Temporal Precedence**: Cause must precede effect
2. **Covariation**: Changes in cause associate with changes in effect
3. **Elimination of Alternatives**: No other plausible explanations

Our analysis addresses #1 and #2 but cannot definitively establish #3 without experimental design.

### 2. Confounding Variables
Multiple unmeasured factors influence oil prices simultaneously:
- **Global Economic Conditions**: GDP growth, inflation, interest rates
- **Technological Changes**: Fracking technology, renewable energy adoption
- **Weather Patterns**: Hurricanes, cold spells affecting demand
- **Currency Fluctuations**: USD strength/weakness
- **Alternative Energy**: Solar, wind, nuclear capacity changes

### 3. Model Limitations

#### Bayesian Model Specific:
- **Prior Sensitivity**: Results depend on prior distribution choices
- **Computational Constraints**: MCMC sampling limitations with many change points
- **Convergence Issues**: Potential for poor mixing or non-convergence
- **Model Misspecification**: Wrong likelihood assumptions lead to wrong conclusions

#### Statistical General:
- **Multiple Testing Problem**: Testing many events increases false positive risk
- **Overfitting**: Complex models may fit noise rather than signal
- **Extrapolation Risk**: Historical patterns may not continue

### 4. Data Limitations

#### Frequency Issues:
- **Daily Data**: May miss intraday reactions to events
- **Missing Intraday Volatility**: Important price movements within trading days
- **Weekend Gaps**: Market closure periods create artificial gaps

#### Quality Issues:
- **Historical Consistency**: Calculation methods may have changed over 35 years
- **Liquidity Variations**: Early years may have less liquid trading
- **Benchmark Changes**: Brent crude definition may have evolved

#### Coverage Issues:
- **Single Benchmark**: Only Brent crude, other benchmarks (WTI, Dubai) may differ
- **Regional Focus**: Primarily reflects European/global markets
- **Contract Specifications**: Futures vs. spot price differences

### 5. Interpretation Challenges

#### Statistical vs. Practical Significance:
- **Statistical Significance**: p-values below 0.05
- **Practical Significance**: Economic impact magnitude matters more
- **Context Dependence**: Same statistical effect may have different implications in different contexts

#### Uncertainty Quantification:
- **Parameter Uncertainty**: Estimated with confidence/credible intervals
- **Model Uncertainty**: Different models give different results
- **Scenario Uncertainty**: Future may differ from past patterns

## Mitigation Strategies

### For Correlation vs. Causation:
1. **Granger Causality Tests**: Statistical test for predictive causality
2. **Instrumental Variables**: Use natural experiments when available
3. **Difference-in-Differences**: Compare with control groups
4. **Event Study Methodology**: Well-established in finance literature
5. **Robustness Checks**: Multiple methodological approaches

### For Model Limitations:
1. **Sensitivity Analysis**: Test different priors and model specifications
2. **Model Averaging**: Combine results from multiple models
3. **Cross-Validation**: Validate on out-of-sample data
4. **Expert Judgment**: Combine statistical results with domain knowledge

### For Data Limitations:
1. **Multiple Data Sources**: Cross-validate with other benchmarks
2. **Higher Frequency Data**: Consider intraday data for key periods
3. **Alternative Specifications**: Test different return calculations
4. **Quality Checks**: Manual validation of extreme values

## Recommendations for Users

### Investors:
- Use results as one input among many for decision-making
- Consider statistical uncertainty in risk management
- Monitor model performance over time
- Combine with fundamental and technical analysis

### Policymakers:
- Consider magnitude of effects, not just statistical significance
- Account for uncertainty in policy design
- Use scenario analysis for different assumptions
- Monitor changing market dynamics

### Energy Companies:
- Incorporate uncertainty in planning processes
- Use results for risk assessment, not precise forecasting
- Combine with operational constraints and objectives
- Update models regularly with new data

## Conclusion

This analysis provides valuable insights into the relationship between events and Brent oil prices, but users must understand its limitations. The results should inform decision-making but not replace judgment, especially regarding causal claims. We provide transparency about assumptions and limitations so users can appropriately weight the evidence in their specific contexts.

**Key Takeaway**: We identify *when* and *how much* prices changed, and suggest *why* based on event correlation. Definitive causal claims require additional evidence beyond statistical correlation.