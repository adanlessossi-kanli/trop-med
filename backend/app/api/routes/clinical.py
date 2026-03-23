from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import RoleRequired
from app.fhir.mappers import FHIR_MAPPERS
from app.models.schemas import ConditionCreate, EncounterCreate, MedicationCreate, ObservationCreate
from app.services import clinical_service

router = APIRouter(prefix="/fhir", tags=["fhir"])

clinician = RoleRequired("admin", "doctor", "nurse")

RESOURCE_MAP = {
    "Encounter": ("encounters", EncounterCreate),
    "Observation": ("observations", ObservationCreate),
    "Condition": ("conditions", ConditionCreate),
    "MedicationRequest": ("medications", MedicationCreate),
}


@router.get("/{resource_type}")
async def list_fhir(resource_type: str, user: Annotated[dict, Depends(clinician)], patient_id: str = ""):
    if resource_type not in RESOURCE_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported resource: {resource_type}")
    collection = RESOURCE_MAP[resource_type][0]
    docs = await clinical_service.list_resources(collection, patient_id)
    mapper = FHIR_MAPPERS.get(collection)
    return [mapper(d) for d in docs] if mapper else docs


@router.post("/{resource_type}")
async def create_fhir(resource_type: str, data: dict, user: Annotated[dict, Depends(clinician)]):
    if resource_type not in RESOURCE_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported resource: {resource_type}")
    collection, model_cls = RESOURCE_MAP[resource_type]
    validated = model_cls(**data)
    create_fn = getattr(clinical_service, f"create_{collection[:-1] if collection.endswith('s') else collection}")
    return await create_fn(validated)


@router.get("/{resource_type}/{resource_id}")
async def get_fhir(resource_type: str, resource_id: str, user: Annotated[dict, Depends(clinician)]):
    if resource_type not in RESOURCE_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported resource: {resource_type}")
    result = await clinical_service.get_resource(RESOURCE_MAP[resource_type][0], resource_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    mapper = FHIR_MAPPERS.get(RESOURCE_MAP[resource_type][0])
    return mapper(result) if mapper else result


@router.put("/{resource_type}/{resource_id}")
async def update_fhir(resource_type: str, resource_id: str, data: dict, user: Annotated[dict, Depends(clinician)]):
    if resource_type not in RESOURCE_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported resource: {resource_type}")
    result = await clinical_service.update_resource(RESOURCE_MAP[resource_type][0], resource_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    return result
