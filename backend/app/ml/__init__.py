"""
SIF classification ML pipeline (SIH26165 — Phase 4).

Design intent, per the brief: don't jump straight to an LLM-based
classifier. Start with a benchmarkable baseline (TF-IDF + Logistic
Regression / XGBoost), track real metrics (precision/recall/F1/PR-AUC/SIF
recall — never plain accuracy on an imbalanced label), and keep the model
swappable behind a stable interface so a transformer or embedding-based
model can replace the baseline later without touching calling code.
"""
