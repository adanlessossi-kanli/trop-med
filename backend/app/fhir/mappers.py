from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.dosage import Dosage
from fhir.resources.encounter import Encounter
from fhir.resources.humanname import HumanName
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient
from fhir.resources.reference import Reference


def to_fhir_patient(doc: dict) -> dict:
    return Patient(
        id=doc.get("fhir_id", doc["_id"]),
        name=[HumanName(given=[doc["given_name"]], family=doc["family_name"], text=doc.get("name_text", ""))],
        gender=doc.get("gender", "unknown"),
        birthDate=doc.get("date_of_birth"),
        telecom=[ContactPoint(system="phone", value=doc["phone"])] if doc.get("phone") else [],
        active=doc.get("status") == "active",
    ).model_dump(exclude_none=True)


def to_fhir_encounter(doc: dict) -> dict:
    return Encounter.model_validate({
        "id": doc["_id"],
        "status": "completed",
        "class": [CodeableConcept(
            coding=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code="AMB")],
        )],
        "subject": Reference(reference=f"Patient/{doc['patient_id']}"),
    }).model_dump(exclude_none=True)


def to_fhir_observation(doc: dict) -> dict:
    return Observation(
        id=doc["_id"],
        status="final",
        code=CodeableConcept(coding=[Coding(code=doc["code"], display=doc["code"])]),
        subject=Reference(reference=f"Patient/{doc['patient_id']}"),
        valueString=doc.get("value", ""),
    ).model_dump(exclude_none=True)


def to_fhir_condition(doc: dict) -> dict:
    return Condition(
        id=doc["_id"],
        clinicalStatus=CodeableConcept(coding=[Coding(code=doc.get("clinical_status", "active"))]),
        code=CodeableConcept(coding=[Coding(
            system="http://hl7.org/fhir/sid/icd-10",
            code=doc["code"],
            display=doc.get("display", ""),
        )]),
        subject=Reference(reference=f"Patient/{doc['patient_id']}"),
    ).model_dump(exclude_none=True)


def to_fhir_medication_request(doc: dict) -> dict:
    return MedicationRequest(
        id=doc["_id"],
        status=doc.get("status", "active"),
        intent="order",
        medication=CodeableReference(
            concept=CodeableConcept(coding=[Coding(code=doc["code"], display=doc.get("display", ""))]),
        ),
        subject=Reference(reference=f"Patient/{doc['patient_id']}"),
        dosageInstruction=[Dosage(text=doc.get("dosage", ""))] if doc.get("dosage") else [],
    ).model_dump(exclude_none=True)


FHIR_MAPPERS = {
    "patients": to_fhir_patient,
    "encounters": to_fhir_encounter,
    "observations": to_fhir_observation,
    "conditions": to_fhir_condition,
    "medications": to_fhir_medication_request,
}
