# Stanleaf Machine Learning Layer

This layer hosts machine learning models, training pipelines, and validation infrastructure for Stanleaf.

## Directory Structure

```
ml/
├── models/      # Serialized models, registry manifests, and architecture definitions
├── training/    # Model training pipelines, hyperparameter tuning scripts
└── evaluation/  # Cross-validation, metric tracking, fairness, and explainability (SHAP)
```

## Intended Tooling
- **Scikit-learn**: Baseline regressors, clustering, and preprocessors.
- **XGBoost / LightGBM**: Gradient-boosted decision trees for tabular financial metrics.
- **SHAP**: Kernel / Tree explainers for model interpretability.
