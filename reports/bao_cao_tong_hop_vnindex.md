# Consolidated Report: VN-Index EDA and Volatility Forecasting

**Sources:** `01_eda.ipynb` and `02_volatility_forecasting.ipynb`\
**Scope:** Summarizes the EDA, the single-split test results, and the
walk-forward evaluation; addresses the questions/comments at the end of
the file and recommends further improvements.\
**Note:** The EDA and single-split test results below come from the
notebooks' saved outputs. This is an educational research project, not
investment advice.

------------------------------------------------------------------------

## 1. Executive Summary

1.  The dataset contains **5,932 price sessions** from **2000-07-31 to
    2024-12-16**, yielding **5,931 log-return observations**. There are
    no unparseable dates, duplicate dates, or missing closing prices.
    Seven volume values are missing, and one observation has a Close
    outside the \[Low, High\] range.
2.  Daily log returns have a mean of **0.000425** (approximately
    0.0425%) and a standard deviation of **0.014439** (1.4439%),
    equivalent to annualized volatility of **22.92%**. The distribution
    is left-skewed and heavy-tailed; the Jarque--Bera test rejects
    normality.
3.  The ACF of \|return\| is positive, large, and decays slowly over 40
    lags, providing clear visual evidence of **volatility
    clustering/persistence**. The return ACF is much weaker, although
    some short lags are significantly correlated.
4.  On the 2020--2024 test period, **base_20** is the best statistical
    baseline by MAE. Both Ridge and Random Forest reduce MAE and RMSE
    relative to base_20; Random Forest performs best among the tested
    models.
5.  In the single-split test evaluation, Random Forest reduces MAE by
    **22.70%** and RMSE by **18.67%** relative to base_20 (R²_oos =
    **0.24671**). A walk-forward evaluation with 5 consecutive windows
    also finds lower Random Forest MAE than base_20 in all 5 windows;
    across the full period, MAE falls by **22.51%** and RMSE by
    **18.27%**. The model may still underestimate volatility in
    high-volatility regimes.
6.  Next steps include investigating the Close outside the High--Low
    range; adding confidence intervals and specialized volatility
    benchmarks; examining regime stability; and measuring feature
    importance with permutation methods/SHAP rather than relying only on
    impurity importance.

------------------------------------------------------------------------

## 2. Notebook 01 --- EDA: Response to A7

### 2.1. Data Quality and Coverage

  -----------------------------------------------------------------------
  Metric                                                          Result
  ------------------------------ ----------------------------------------
  Price rows                                                        5,932

  Date range                                    2000-07-31 -- 2024-12-16

  Log-return observations                                           5,931

  Unparseable dates                                                     0

  Duplicate dates removed                                               0

  Missing Close values removed                                          0

  Missing Volume values                                                 7

  High \< Low                                                           0

  Close outside \[Low, High\]                                           1

  Maximum difference between recalculated %     0.005 percentage points
  change and source data

  Sessions with a difference above 0.05                                 0
  percentage points
  -----------------------------------------------------------------------

No duplicate dates, malformed dates, or missing Close values were
found. The `% change` column closely matches the percentage change
recalculated from Close: the maximum difference is only 0.005
percentage points, and no session exceeds the 0.05-percentage-point
threshold.

The **single Close observation outside \[Low, High\]** should be checked
against the source data. The seven missing Volume values do not directly
affect the current features/models because Volume is not used. Calendar
gaps longer than 7 days occur mainly in January--February and may be
related to extended holidays or the trading calendar; however, they
should be checked against the official trading calendar before drawing
a conclusion. Not every calendar gap should be treated as missing data,
since the market does not trade on weekends and holidays.

### 2.2. RQ1 --- Return Distribution Characteristics

  Statistic                                      Value
  --------------------------------- -------------------
  Observations                                     5,931
  Mean daily log return                         0.000425
  Daily standard deviation                      0.014439
  Annualized volatility (std × √252)  0.229214 = 22.92%
  Minimum                                      -0.076557
  Maximum                                       0.066561
  Skewness                                      -0.395399
  Excess kurtosis                                3.409743
  Jarque--Bera statistic                          3,021.1
  Jarque--Bera p-value                         approximately 0

The daily mean return is small and close to zero relative to volatility.
Negative skewness indicates a left-skewed distribution: large downward
moves are more prominent than comparable upward moves. The large
positive excess kurtosis (3.41) indicates heavier tails than a normal
distribution, meaning extreme movements occur more often than under
the normality assumption.

The near-zero Jarque--Bera p-value rejects the hypothesis that returns
are normally distributed at conventional significance levels. The
histogram overlaid with a normal curve also supports the heavy-tail
observation.

### 2.3. RQ2 --- High-Volatility Periods and Volatility Clustering

The years with notably high annualized volatility include:

  Year    Annualized volatility
  ------ ----------------------
  2001                   54.34%
  2008                   37.16%
  2009                   34.54%
  2006                   32.01%
  2007                   27.22%
  2022                   24.95%
  2020                   22.99%
  2018                   22.34%

2001 has the highest volatility in the table, well above the other
years. Volatility was also high in 2008--2009. The 20-session rolling
plot shows volatility changing in clusters and rising sharply during
some periods rather than fluctuating around a constant level.

The return ACF is generally smaller than the absolute-return ACF. In
contrast, the ACF of \|return\| is large and positive, decays slowly, and
remains above the reference bounds through 40 lags in the plot. This is
clear evidence of volatility clustering: highly volatile sessions tend
to occur alongside other highly volatile periods, as do calm sessions.

**Modeling implication:** Volatility is persistent, so baselines based
on recent volatility, such as 20-session rolling volatility and EWMA,
are strong competitors. ML models must demonstrate added value over
these baselines, not merely over a mean forecast.

### 2.4. Suggested A7 Text for the Notebook

> The dataset contains 5,932 price sessions from 2000-07-31 to
> 2024-12-16, yielding 5,931 log-return observations. There are no
> malformed dates, duplicate dates, or missing Close values; however,
> seven Volume values are missing and one Close observation falls
> outside the Low--High range and should be checked. The source
> percentage-change values closely match those recalculated from Close.
> Daily log returns have a mean of 0.000425, a standard deviation of
> 0.014439, and annualized volatility of approximately 22.92%. Skewness
> of -0.395 indicates left skew, while excess kurtosis of 3.410 indicates
> heavy tails; the Jarque--Bera test (p-value approximately 0) rejects
> normality. Volatility was notably high in 2001 (54.34%), 2008 (37.16%),
> 2009 (34.54%), and 2006 (32.01%). The ACF of \|return\| is large and
> positive and decays slowly through 40 lags, indicating clear
> volatility clustering. Because volatility is persistent, rolling
> volatility and EWMA are difficult baselines to beat; ML models should
> be evaluated based on out-of-sample gains over these baselines.

------------------------------------------------------------------------

## 3. Notebook 02 --- Volatility Forecasting: Response to D5

### 3.1. Design Checks and Data Splits

The task forecasts, at day t, the standard deviation of log returns over
the next 5 sessions (t+1 through t+5), without annualization. A manual
check confirms that the target is aligned correctly; there are exactly
5 NaN values at the end of the series, as expected. The truncation check
also finds no look-ahead in the features or baselines.

  Split       Date range                  Observations
  ----------- --------------------------- -------------
  Train       2000-12-22 -- 2015-07-17          3,514
  Validation  2015-07-27 -- 2020-03-25          1,168
  Test        2020-04-03 -- 2024-12-09          1,174

Purging the final 5 sessions from the training and validation sets
prevents their targets from using returns belonging to the next split.
The results below compare models on the same test dates.

### 3.2. RQ3 --- Best Baseline

On the test set, **base_20** is the best statistical baseline by MAE:

| Baseline | MAE | RMSE | R²_oos |
|:---|---:|---:|---:|
| base_5 | 0.00541 | 0.00757 | -0.23086 |
| **base_20** | **0.00531** | **0.00728** | **-0.13897** |
| base_exp | 0.00723 | 0.00814 | -0.42057 |
| base_ewma | 0.00533 | 0.00692 | -0.02908 |

The negative R²_oos for base_20 (-0.13897) means that, under the
squared-error criterion, this baseline performs worse than a constant
forecast equal to the mean target in train+validation. Base_EWMA has a
lower RMSE than base_20 but a slightly higher MAE; because the notebook
selects the best baseline by MAE, base_20 is used as the comparison
reference.

### 3.3. RQ4 --- Ridge and Random Forest vs. the Best Baseline

| Model | MAE | RMSE | R²_oos | MAE reduction vs. base_20 | RMSE reduction vs. base_20 |
|:---|---:|---:|---:|---:|---:|
| base_20 | 0.00531 | 0.00728 | -0.13897 | 0.00% | 0.00% |
| Ridge | 0.00458 | 0.00683 | -0.00154 | 13.85% | 6.23% |
| Random Forest | 0.00411 | 0.00592 | 0.24671 | 22.70% | 18.67% |

**Both Ridge and Random Forest outperform base_20 on MAE and RMSE.**
Random Forest performs best, reducing MAE by 22.70% and RMSE by 18.67%,
with a positive R²_oos of 0.24671. Ridge also reduces both errors, but
its R²_oos remains slightly negative (-0.00154), nearly matching the
constant benchmark under the squared-error criterion.

Random Forest's MAE improvement appears in every test year in the
table:

| Year | MAE base_20 | MAE Random Forest |
|---:|---:|---:|
| 2020 | 0.00673 | 0.00452 |
| 2021 | 0.00675 | 0.00483 |
| 2022 | 0.00577 | 0.00499 |
| 2023 | 0.00379 | 0.00323 |
| 2024 | 0.00377 | 0.00299 |

Thus, the advantage is not attributable to a single year. However, the
improvement is smaller in 2022 than in 2020--2021, and this annual
breakdown is only descriptive evidence from one test period; it is not
sufficient to establish stability across market cycles.

### 3.4. Walk-Forward Evaluation

To check whether results depend on a particular test segment, the test
period is split into **5 consecutive time windows**, each containing
approximately 234--235 sessions. Ridge and Random Forest are refit on
an expanding history at the start of each window; hyperparameters
selected using the initial validation set are held fixed. The final 5
observations whose labels are not yet observable at forecast time are
excluded from training according to the horizon H = 5. Each window's
R²_oos uses the mean target from that window's training history as its
benchmark.

| Window | Test period | MAE base_20 | MAE Random Forest | R²_oos RF |
|---:|:---|---:|---:|---:|
| 1 | 2020-04-03--2021-03-10 | 0.00795 | 0.00534 | 0.13144 |
| 2 | 2021-03-11--2022-02-17 | 0.00533 | 0.00403 | 0.08730 |
| 3 | 2022-02-18--2023-01-27 | 0.00595 | 0.00506 | 0.32711 |
| 4 | 2023-01-30--2023-12-29 | 0.00357 | 0.00318 | 0.32705 |
| 5 | 2024-01-02--2024-12-09 | 0.00377 | 0.00298 | 0.38306 |

| Overall metric (5 windows combined) | MAE | RMSE | R²_oos |
|:---|---:|---:|---:|
| base_20 | 0.00531 | 0.00728 | -0.13546 |
| Ridge | 0.00451 | 0.00669 | 0.04246 |
| Random Forest | 0.00412 | 0.00595 | 0.24162 |

Random Forest has a lower MAE than base_20 in all 5 windows and also
outperforms Ridge in each window. Across all walk-forward predictions,
MAE falls by approximately **22.51%** and RMSE by **18.27%** relative to
base_20; Random Forest's R²_oos is **0.24162**. This is consistent with
the single-split test result. However, the 5 windows should not be
treated as 5 independent samples: they are consecutive segments of the
same test period, and hyperparameters were not reselected for each
window.

Detailed results are saved in
`reports/results_walk_forward.csv` and
`reports/results_walk_forward_folds.csv`.

### 3.5. Error and Bias Analysis

Using tertile thresholds computed from the training set, the test set
contains 424 low-volatility, 468 mid-volatility, and 282 high-volatility
sessions.

| Regime | MAE base_20 | MAE Ridge | MAE Random Forest | RF bias (predicted - actual) |
|:---|---:|---:|---:|---:|
| Low volatility | 0.00503 | 0.00301 | 0.00300 | +0.00291 |
| Mid volatility | 0.00423 | 0.00299 | 0.00239 | -0.00024 |
| High volatility | 0.00755 | 0.00958 | 0.00863 | -0.00818 |

Random Forest has its largest errors in the **high-volatility regime**
(MAE 0.00863), alongside a clear negative bias (-0.00818), meaning it
underestimates realized volatility. In the low-volatility regime, its
bias is positive (+0.00291), so it tends to overpredict. Bias is close
to zero in the mid-volatility regime.

The largest RF errors cluster around sharp volatility increases, for
example July 21--24, 2020 and January 22--27, 2021. On these dates,
realized volatility rises to approximately 0.034--0.046 while RF
predictions are substantially lower. This is consistent with the
hypothesis that a model based on past features responds slowly to sudden
volatility increases. This is a descriptive association, not a causal
conclusion.

### 3.6. Feature-Importance Interpretation

Based on the saved importance plots:

-   **Random Forest:** `std_10` is the most important feature, followed
    by `std_20`, `abs_ret_5`, `hl_range_5`, and `dist_ma60`. Recent
    short-/medium-term volatility and absolute returns dominate.
-   **Ridge:** The largest standardized coefficient in absolute value
    belongs to `hl_range_5`, followed by `std_20`, `abs_ret`, `std_10`,
    `dist_ma60`, and `abs_ret_5`. `ret_lag1` and `mean_5` have notable
    negative coefficients; several other features have coefficients
    close to zero.

The RF results are consistent with volatility clustering: volatility
over the most recent 10--20 sessions and recent absolute returns may
provide information about volatility over the next 5 sessions.
`hl_range_5` also matters, suggesting that recent High--Low ranges add
information beyond Close-to-Close returns.

Note: Random Forest impurity importance can be biased when features are
correlated or have different distributional properties; Ridge
coefficients depend on scaling and feature correlations. These rankings
should therefore not be interpreted as causal effects.

### 3.7. Limitations

-   Only one index, the VN-Index, is used; results do not automatically
    generalize to individual stocks, other markets, or other assets.
-   The walk-forward evaluation creates 5 consecutive windows within
    the same 2020--2024 test period; no separate out-of-sample period or
    market is available for an independent cycle-stability check.
-   Market regimes change; the model has a clear bias in the
    high-volatility regime and may respond slowly to shocks.
-   The current features mainly comprise lagged/rolling returns,
    volatility, moving-average distances, and High--Low ranges. No
    liquidity/volume features are included; Volume has missing values.
-   The hyperparameter grids are narrow. Ridge selects alpha = 1000 at
    the upper grid boundary, so the optimal region is not yet known. RF
    selects max_depth = 8, also at the upper boundary of the tested
    depth grid.
-   Confidence intervals/statistical significance tests for error
    differences have not been reported.
-   Trading costs and trading strategies have not been evaluated; more
    accurate volatility forecasts do not automatically imply trading
    profits.

------------------------------------------------------------------------

## 4. Further Improvements

### High Priority --- Data Reliability and Evaluation

1.  **Investigate the Close outside \[Low, High\].** Print the specific
    date and compare it with the source CSV/original data provider to
    determine whether it is an input error, an index adjustment, or a
    data convention. Do not change the value before verifying it.
2.  **Check the trading calendar.** Compare long gaps in January--
    February with the official holiday calendar; distinguish valid
    market holidays from missing trading-session data.
3.  **Walk-forward / rolling-origin evaluation completed.** The test
    period is divided into 5 consecutive windows; models are refit on
    expanding histories, and per-window and aggregate results are
    reported. Random Forest beats base_20 by MAE in all 5 windows. The
    next step is to evaluate on an independent data period if available,
    rather than treating adjacent windows as independent samples.
4.  **Quantify uncertainty in model differences.** Use a time-block
    bootstrap or a test appropriate for dependent time series to form
    confidence intervals for MAE/RMSE differences. Avoid independently
    bootstrapping individual days because the 5-session targets
    overlap.
5.  **Preserve the one-use test principle.** New feature or
    hyperparameter choices should be based on train/validation or
    nested/rolling validation; do not tune against the current test
    results.

### High Priority --- Models and Benchmarks

6.  **Expand the Ridge grid.** The best alpha is 1000, at the upper
    boundary of the current grid. Extend the grid on a logarithmic scale
    (for example, adding larger values) and select using validation.
7.  **Expand RF tuning cautiously.** The best depth is 8, also at the
    upper grid boundary. Try greater depths while controlling
    `min_samples_leaf`, `max_features`, and the number of trees using
    time-aware validation.
8.  **Add specialized volatility benchmarks.** Compare against models
    such as GARCH/EGARCH/GJR-GARCH or HAR-RV variants if the data and
    realized-volatility definition are suitable. Retain rolling and
    EWMA baselines for interpretability.
9.  **Evaluate regimes separately.** Report MAE/RMSE/bias for low-,
    mid-, and high-volatility regimes; consider regime-specific models
    or forecast adjustments, but validate them out of sample.
10. **Check tail calibration.** Since the model underestimates
    high-volatility observations, consider losses that penalize
    high-volatility errors, quantile forecasting, or interval forecasts
    rather than only point forecasts. Do not select an approach based
    only on test results.

### Medium Priority --- Features, Interpretation, and Reproducibility

11. **Test well-motivated additional features:** volume/turnover (after
    handling missing values), range-based volatility, downside
    semivolatility, realized measures over multiple windows, and
    calendar features. Each feature must use only data available at
    time t.
12. **Use time-aware permutation importance or SHAP.** Apply these on
    validation data or assess stability across multiple folds; do not
    interpret impurity importance as causal contribution.
13. **Report units clearly.** The target is the daily standard
    deviation of 5-session log returns and is not annualized. State the
    units in tables and plots to distinguish it from annualized
    volatility.
14. **Add automated tests.** In addition to the truncation test, check
    target alignment at multiple positions, the absence of future
    information in features, identical dates when comparing models,
    and no NaN/negative volatility predictions.
15. **Improve reproducibility.** Record library versions, data source
    and download date, CSV checksum, split configuration, random seed,
    selected hyperparameters, and final results in a configuration or
    metadata file. Use relative data paths rather than
    machine-specific paths.

------------------------------------------------------------------------

## 5. Proposed Overall Conclusion

> The EDA shows that VN-Index log returns from 2000--2024 are
> left-skewed, heavy-tailed, and exhibit clear volatility clustering.
> Volatility varies over time, with notable periods including 2001,
> 2008--2009, and 2022. These properties help explain why rolling
> volatility and EWMA are competitive baselines. For forecasting the
> standard deviation of returns over the next 5 sessions, base_20 is the
> best test-set baseline by MAE. Both Ridge and Random Forest improve
> MAE and RMSE; Random Forest performs best, reducing MAE by 22.70% and
> RMSE by 18.67% relative to base_20, with R²_oos = 0.24671. Its MAE
> advantage appears in each test year from 2020 to 2024. The 5-window
> walk-forward evaluation also finds lower Random Forest MAE than
> base_20 in every window; aggregate MAE and RMSE reductions are 22.51%
> and 18.27%, respectively (R²_oos = 0.24162). This adds a stability
> check within the same test period; the 5 windows are not independent
> samples. The model still underestimates volatility in high-volatility
> regimes, especially during sudden volatility spikes. These results
> support the added value of Random Forest in the current sample, but
> confidence intervals, specialized volatility benchmarks, and data
> outside this period are needed before drawing general conclusions.

------------------------------------------------------------------------

## 6. Notes on Conclusions Not Supported by the Available Outputs

-   The notebook does not save exact numerical ACF values; the
    volatility-clustering discussion is based on the saved ACF plot.
-   The feature-importance plots do not include a complete table of
    importance/coefficient values; rankings are interpreted from bar
    lengths and no exact values are assigned.
-   The walk-forward evaluation was run on the source CSV available in
    the workspace. The EDA and single-split test results remain
    summarized from saved notebook outputs and were not fully
    recomputed during this report update.
