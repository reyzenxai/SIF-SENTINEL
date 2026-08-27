"""
Baseline model 2: TF-IDF + XGBoost (SIH26165 — Phase 4).

Usually outperforms logistic regression on this kind of sparse text +
tabular-ish problem once there's enough labelled data, at the cost of being
less directly interpretable. xgboost is an optional dependency — if it
isn't installed, this module is still importable and simply reports
unavailable, matching the existing pgvector/sentence-transformers pattern
elsewhere in this codebase (see app/models/database.py).
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from app.ml.base import BaseSIFClassifier

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    XGBClassifier = None
    HAS_XGBOOST = False


class XGBoostSIFClassifier(BaseSIFClassifier):
    model_type = "tfidf_xgboost"

    def _build_pipeline(self) -> Pipeline:
        if not HAS_XGBOOST:
            raise RuntimeError(
                "xgboost is not installed. Run `pip install xgboost` or use "
                "the logreg baseline (model_type='tfidf_logreg') instead."
            )
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=20000,
                ngram_range=(1, 2),
                min_df=2,
                sublinear_tf=True,
            )),
            ("clf", XGBClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.08,
                subsample=0.9,
                colsample_bytree=0.7,
                eval_metric="logloss",
            )),
        ])
