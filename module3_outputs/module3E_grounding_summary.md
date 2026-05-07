# Module 3E Grounding Summary

- Analysis source: `api_llm_output`
- Evaluated file: `module3_outputs\module3D_llm_analysis.json`
- Overall grounding status: **pass_with_warnings**
- Required sections passed: true
- Exact keyword coverage rate: 0.667
- Relaxed keyword coverage rate: 0.833
- Classifier coverage rate: 0.500
- Normalization coverage rate: 0.750

## Check Table
| check_name | status | severity | details |
| --- | --- | --- | --- |
| required_sections | pass | info | All required sections are present. |
| forbidden_claims | pass | info | [{"term": "biomarker", "sentence": "No external datasets, genes, or biomarkers were introduced", "severity": "info"}, {"term": "biological mechanism", "sentence": "No biological mechanisms were inferred from the data", "severity": "info"}] |
| exact_keyword_coverage | warning | warning | rate=0.667; missing=['batch_sensitive', 'moderately_sensitive', 'late_spike_driven', 'gradual_degradation'] |
| relaxed_keyword_coverage | pass | info | rate=0.833; missing=['moderately_sensitive', 'gradual_degradation'] |
| classifier_coverage | warning | warning | rate=0.500; missing=['lasso', 'rf', 'xgb'] |
| normalization_coverage | pass | info | rate=0.750; missing=['mn'] |
| top_sensitive_pair_coverage | pass | info | {"covered": [{"classifier": "knn", "normalization": "vsn", "match_type": "partial"}, {"classifier": "knn", "normalization": "mn", "match_type": "partial"}, {"classifier": "knn", "normalization": "qn", "match_type": "partial"}], "missing": [], "coverage_count": 3, "coverage_rate": 1.0} |
| top_stable_pair_coverage | pass | info | {"covered": [{"classifier": "svm", "normalization": "non", "match_type": "partial"}, {"classifier": "pam", "normalization": "qn", "match_type": "partial"}, {"classifier": "rf", "normalization": "non", "match_type": "exact"}], "missing": [], "coverage_count": 3, "coverage_rate": 1.0} |
| section_length_sanity | pass | info | All checked text sections have reasonable length. |
