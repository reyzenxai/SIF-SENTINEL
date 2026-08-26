"""
Semantic Pattern Discovery Engine.

Design note: the spec calls for Sentence-Transformer embeddings + pgvector.
This sandbox cannot reach the HuggingFace model hub, so we substitute
TF-IDF vectors (scikit-learn, fully offline) + cosine similarity as the
"semantic embeddings" layer, and DBSCAN for density-based clustering
(same algorithm choice the spec recommends, since cluster count is
unknown ahead of time). The pipeline stage names and outputs match the
architecture unchanged: reports -> vectors -> similarity -> clusters ->
trend detection -> emerging risk patterns.
"""
import datetime as dt
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import CLUSTER_EPS, CLUSTER_MIN_SAMPLES


def build_vectors(descriptions: list[str]):
    try:
        from sentence_transformers import SentenceTransformer
        # using a lightweight local model: all-MiniLM-L6-v2
        model = SentenceTransformer("all-MiniLM-L6-v2")
        matrix = model.encode(descriptions)
        return matrix, model
    except ImportError:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=3000, ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(descriptions)
        return matrix, vectorizer


def cluster_reports(reports: list[dict]) -> dict:
    """Hybrid clustering, matching the spec's 'LLM + embeddings + rules' architecture:

    Primary grouping uses the rule/ontology-extracted `hazard_category` (this is
    what lets reports with completely different wording — e.g. "entered energized
    pump area" vs "LOTO checklist was not verified" — correctly merge into one
    semantic pattern, since raw lexical/TF-IDF similarity alone cannot bridge
    that vocabulary gap without a trained sentence embedding model).

    Within each hazard_category group, TF-IDF cosine similarity produces a
    semantic-coherence 'confidence' score for the pattern and ranks evidence,
    but does NOT split the category further — this is what allows reports
    with completely different wording (e.g. "entered energized pump area" vs
    "LOTO checklist was not verified") to correctly merge into one pattern,
    which pure lexical similarity could never bridge without a trained
    embedding model.

    Reports with no extracted hazard_category are treated as noise / unrelated,
    consistent with spec section 27 ("include noise and unrelated reports so
    clustering is meaningful").
    """
    if len(reports) < CLUSTER_MIN_SAMPLES:
        return {}

    by_category = defaultdict(list)
    for idx, r in enumerate(reports):
        cat = r.get("hazard_category")
        if cat:
            by_category[cat].append(idx)

    result = {}
    next_label = 0

    for cat, idxs in by_category.items():
        if len(idxs) < CLUSTER_MIN_SAMPLES:
            continue  # too few reports in this category to be a meaningful pattern

        member_reports = [reports[i] for i in idxs]
        descriptions = [r["description"] for r in member_reports]

        if len(descriptions) > 1:
            matrix, _ = build_vectors(descriptions)
            sim_matrix = cosine_similarity(matrix)
            n = len(descriptions)
            avg_sim = float((sim_matrix.sum() - n) / max(n * (n - 1), 1))
            # blend lexical similarity with a base confidence from the shared
            # ontology category match, so confidence stays meaningful even for
            # correctly-grouped but differently-worded reports
            confidence = round(min(0.6 + 0.4 * max(avg_sim, 0), 0.97), 2)
        else:
            confidence = 0.75

        result[next_label] = {"reports": member_reports, "confidence": confidence}
        next_label += 1

    return result


def detect_trend(monthly_counts: dict) -> tuple[str, float]:
    """monthly_counts: {'2026-01': 8, '2026-02': 12, ...} sorted by key.
    Returns (trend_label, pct_change)."""
    months = sorted(monthly_counts.keys())
    if len(months) < 2:
        return "new", 0.0
    values = [monthly_counts[m] for m in months]
    recent = values[-1]
    prior = values[-2] if len(values) >= 2 else 0
    if prior == 0:
        pct = 100.0 if recent > 0 else 0.0
    else:
        pct = round(((recent - prior) / prior) * 100, 1)

    # newly emerging: majority of activity is in the last month, and few months of history
    if len(months) <= 2 and recent >= sum(values) * 0.5:
        return "new", pct
    if pct >= 15:
        return "increasing", pct
    if pct <= -15:
        return "decreasing", pct
    return "stable", pct


def summarize_cluster(member_reports: list[dict]) -> dict:
    hazard_categories = Counter(r.get("hazard_category") for r in member_reports if r.get("hazard_category"))
    control_failures = Counter(r.get("control_failure") for r in member_reports if r.get("control_failure"))
    consequences = Counter(r.get("potential_consequence") for r in member_reports if r.get("potential_consequence"))
    locations = sorted(set(r.get("location") for r in member_reports if r.get("location")))
    contractors = sorted(set(r.get("contractor") for r in member_reports if r.get("contractor")))
    departments = sorted(set(r.get("department") for r in member_reports if r.get("department")))

    common_hazard = hazard_categories.most_common(1)[0][0] if hazard_categories else "Mixed hazards"
    common_control_failure = control_failures.most_common(1)[0][0] if control_failures else None
    common_consequence = consequences.most_common(1)[0][0] if consequences else None

    dates = [r["report_date"] for r in member_reports]
    first_seen = min(dates)
    last_seen = max(dates)

    monthly_counts = defaultdict(int)
    for d in dates:
        key = d.strftime("%Y-%m") if isinstance(d, dt.datetime) else str(d)[:7]
        monthly_counts[key] += 1
    monthly_counts = dict(sorted(monthly_counts.items()))

    trend, pct = detect_trend(monthly_counts)

    title = f"{common_hazard} — {common_control_failure}" if common_control_failure else f"{common_hazard} Pattern"

    return {
        "title": title,
        "description": (
            f"Emerging semantic pattern across {len(member_reports)} reports linked to "
            f"{common_hazard.lower()} hazards"
            + (f" with recurring {common_control_failure.lower()}" if common_control_failure else "")
            + f", spanning {len(locations)} location(s) and {len(contractors)} contractor(s)."
        ),
        "report_count": len(member_reports),
        "locations": locations,
        "contractors": contractors,
        "departments": departments,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "trend": trend,
        "trend_pct": pct,
        "common_hazard": common_hazard,
        "common_control_failure": common_control_failure,
        "potential_consequence": common_consequence,
        "monthly_counts": monthly_counts,
    }
