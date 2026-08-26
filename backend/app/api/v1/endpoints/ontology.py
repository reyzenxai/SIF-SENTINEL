from fastapi import APIRouter
from app.services.ontology import SAFETY_ONTOLOGY

router = APIRouter()


@router.get("/hazards")
def get_ontology():
    categories = []
    for cat, data in SAFETY_ONTOLOGY.items():
        categories.append({
            "name": cat,
            "potential_consequence": data["potential_consequence"],
            "subcategories": list(data["subcategories"].keys()),
        })
    return {"categories": categories}
