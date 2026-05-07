# Module 3B Evidence Pack

## Project Scope
- Module: Module 3B Evidence Pack Builder
- Scenario: jama_scenario1_3
- Metric: classification error
- Split values: 50, 70, 80, 90, 100
- Interpretation note: Higher split values indicate stronger batch-separated evaluation.
- Analysis scope note: Use only the detected pattern labels and numeric features. Do not infer biological mechanisms.
- Constraints: use only provided evidence; do not infer biological mechanisms; do not claim causality

## Scenario Overview
| n_classifiers | n_normalizations | n_curves | dominant_observation | dominant_failure_mode |
| --- | --- | --- | --- | --- |
| 6 | 4 | 24 | Most classifier-normalization curves show increasing error as split moves from 50 to 100, suggesting reduced robustness under stronger batch-separated evaluation. | The most frequent degradation type is fluctuating. |

Overall pattern counts:
```json
{
  "trend_label": {
    "increasing": 22,
    "flat_or_weak": 2
  },
  "robustness_flag": {
    "batch_sensitive": 16,
    "moderately_sensitive": 8
  },
  "spike_type": {
    "no_major_spike": 16,
    "late_extreme_split_spike": 8
  },
  "curve_shape": {
    "non_monotonic_increase": 8,
    "monotonic_with_spike": 7,
    "gradual_monotonic_increase": 7,
    "mostly_flat": 2
  },
  "pattern_strength": {
    "moderate": 13,
    "weak": 8,
    "strong": 3
  },
  "degradation_type": {
    "fluctuating": 9,
    "late_spike_driven": 8,
    "gradual_degradation": 7
  }
}
```

## Most Sensitive Combinations
| classifier | normalization | delta_100_50 | error_50 | error_100 | robustness_flag | degradation_type | pattern_strength |
| --- | --- | --- | --- | --- | --- | --- | --- |
| knn | vsn | 0.306 | 0.115 | 0.421 | batch_sensitive | late_spike_driven | strong |
| knn | mn | 0.271 | 0.121 | 0.393 | batch_sensitive | late_spike_driven | strong |
| knn | qn | 0.270 | 0.118 | 0.388 | batch_sensitive | late_spike_driven | strong |
| xgb | qn | 0.167 | 0.114 | 0.281 | batch_sensitive | late_spike_driven | moderate |
| lasso | vsn | 0.167 | 0.114 | 0.280 | batch_sensitive | gradual_degradation | moderate |

## Most Stable Combinations
| classifier | normalization | delta_100_50 | error_50 | error_100 | robustness_flag | degradation_type | pattern_strength |
| --- | --- | --- | --- | --- | --- | --- | --- |
| svm | non | 0.033 | 0.161 | 0.194 | moderately_sensitive | fluctuating | weak |
| pam | qn | 0.050 | 0.181 | 0.232 | moderately_sensitive | fluctuating | weak |
| rf | non | 0.059 | 0.134 | 0.193 | moderately_sensitive | fluctuating | weak |
| knn | non | 0.074 | 0.131 | 0.204 | moderately_sensitive | gradual_degradation | weak |
| xgb | non | 0.078 | 0.113 | 0.191 | moderately_sensitive | gradual_degradation | weak |

## Classifier-Level Evidence
| classifier | n_batch_sensitive | n_moderately_sensitive | n_relatively_stable | n_spike_curves | mean_delta_100_50 | dominant_degradation_type | dominant_robustness_flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| knn | 3 | 1 | 0 | 3 | 0.230 | late_spike_driven | batch_sensitive |
| lasso | 3 | 1 | 0 | 0 | 0.121 | gradual_degradation | batch_sensitive |
| pam | 1 | 3 | 0 | 0 | 0.088 | fluctuating | moderately_sensitive |
| rf | 3 | 1 | 0 | 2 | 0.131 | late_spike_driven | batch_sensitive |
| svm | 3 | 1 | 0 | 2 | 0.126 | late_spike_driven | batch_sensitive |
| xgb | 3 | 1 | 0 | 1 | 0.130 | fluctuating | batch_sensitive |

## Normalization-Level Evidence
| normalization | n_curves | n_batch_sensitive | n_moderately_sensitive | n_relatively_stable | n_spike_curves | mean_delta_100_50 | mean_error_50 | mean_error_100 | dominant_degradation_type | dominant_robustness_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mn | 6 | 5 | 1 | 0 | 3 | 0.157 | 0.123 | 0.280 | late_spike_driven | batch_sensitive |
| non | 6 | 1 | 5 | 0 | 0 | 0.077 | 0.142 | 0.219 | fluctuating | moderately_sensitive |
| qn | 6 | 5 | 1 | 0 | 4 | 0.155 | 0.130 | 0.284 | late_spike_driven | batch_sensitive |
| vsn | 6 | 5 | 1 | 0 | 1 | 0.163 | 0.128 | 0.290 | gradual_degradation | batch_sensitive |

## Representative Pattern Sentences
- **top_sensitive** `knn/vsn`: For scenario jama_scenario1_3, knn with vsn normalization shows increasing error from 0.115 at split=50 to 0.421 at split=100. The delta_100_50 is 0.306; robustness_flag=batch_sensitive, pattern_strength=strong, degradation_type=late_spike_driven, and spike_type=late_extreme_split_spike with the largest absolute step change at 90-100.
- **top_sensitive** `knn/mn`: For scenario jama_scenario1_3, knn with mn normalization shows increasing error from 0.121 at split=50 to 0.393 at split=100. The delta_100_50 is 0.271; robustness_flag=batch_sensitive, pattern_strength=strong, degradation_type=late_spike_driven, and spike_type=late_extreme_split_spike with the largest absolute step change at 90-100.
- **top_sensitive** `knn/qn`: For scenario jama_scenario1_3, knn with qn normalization shows increasing error from 0.118 at split=50 to 0.388 at split=100. The delta_100_50 is 0.270; robustness_flag=batch_sensitive, pattern_strength=strong, degradation_type=late_spike_driven, and spike_type=late_extreme_split_spike with the largest absolute step change at 90-100.
- **top_sensitive** `xgb/qn`: For scenario jama_scenario1_3, xgb with qn normalization shows increasing error from 0.114 at split=50 to 0.281 at split=100. The delta_100_50 is 0.167; robustness_flag=batch_sensitive, pattern_strength=moderate, degradation_type=late_spike_driven, and spike_type=late_extreme_split_spike with the largest absolute step change at 90-100.
- **top_sensitive** `lasso/vsn`: For scenario jama_scenario1_3, lasso with vsn normalization shows increasing error from 0.114 at split=50 to 0.280 at split=100. The delta_100_50 is 0.167; robustness_flag=batch_sensitive, pattern_strength=moderate, degradation_type=gradual_degradation, and spike_type=no_major_spike with the largest absolute step change at 90-100.
- **top_stable** `svm/non`: For scenario jama_scenario1_3, svm with non normalization shows flat_or_weak error from 0.161 at split=50 to 0.194 at split=100. The delta_100_50 is 0.033; robustness_flag=moderately_sensitive, pattern_strength=weak, degradation_type=fluctuating, and spike_type=no_major_spike with the largest absolute step change at 90-100.
- **top_stable** `pam/qn`: For scenario jama_scenario1_3, pam with qn normalization shows flat_or_weak error from 0.181 at split=50 to 0.232 at split=100. The delta_100_50 is 0.050; robustness_flag=moderately_sensitive, pattern_strength=weak, degradation_type=fluctuating, and spike_type=no_major_spike with the largest absolute step change at 80-90.
- **top_stable** `rf/non`: For scenario jama_scenario1_3, rf with non normalization shows increasing error from 0.134 at split=50 to 0.193 at split=100. The delta_100_50 is 0.059; robustness_flag=moderately_sensitive, pattern_strength=weak, degradation_type=fluctuating, and spike_type=no_major_spike with the largest absolute step change at 80-90.
- **top_stable** `knn/non`: For scenario jama_scenario1_3, knn with non normalization shows increasing error from 0.131 at split=50 to 0.204 at split=100. The delta_100_50 is 0.074; robustness_flag=moderately_sensitive, pattern_strength=weak, degradation_type=gradual_degradation, and spike_type=no_major_spike with the largest absolute step change at 90-100.
- **top_stable** `xgb/non`: For scenario jama_scenario1_3, xgb with non normalization shows increasing error from 0.113 at split=50 to 0.191 at split=100. The delta_100_50 is 0.078; robustness_flag=moderately_sensitive, pattern_strength=weak, degradation_type=gradual_degradation, and spike_type=no_major_spike with the largest absolute step change at 90-100.
