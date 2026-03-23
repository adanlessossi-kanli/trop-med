"""
Coverage gap tests for Trop-Med backend.
Validates: Requirements 12.5, 12.6
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.schemas import AIResponse

_settings = get_settings()

# ── Helpers ───────────────────────────────────────────────────────────────────

def _token(role: str) -> str:
    return create_access_token(f"{role}-id", role, "fr", _settings)


MOCK_PATIENT = {
    "_id": "p1", "fhir_id": "f1", "given_name": "Ama", "family_name": "Kofi",
    "name_text": "Ama Kofi", "date_of_birth": "1990-01-01", "gender": "female",
    "phone": "+228 90 00 00 00", "locale": "fr", "status": "active",
}

MOCK_ENCOUNTER = {
    "_id": "enc-1", "patient_id": "p1", "practitioner_id": "doc-1",
    "type": "consultation", "reason": "", "notes": "",
}

MOCK_OBSERVATION = {
    "_id": "obs-1", "patient_id": "p1", "encounter_id": "enc-1",
    "code": "temperature", "value": "37.5", "unit": "C",
}

MOCK_CONDITION = {
    "_id": "cond-1", "patient_id": "p1", "encounter_id": "enc-1",
    "code": "A90", "display": "Dengue fever", "clinical_status": "active",
}

MOCK_MEDICATION = {
    "_id": "med-1", "patient_id": "p1", "encounter_id": "enc-1",
    "code": "J01CA04", "display": "Amoxicillin", "dosage": "500mg", "status": "active",
}


# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

_NOTIF = "app.api.routes.notifications.notification_service"


@pytest.mark.asyncio
async def test_list_notifications(client):
    with patch(f"{_NOTIF}.list_notifications", new_callable=AsyncMock, return_value=[]):
        resp = await client.get(
            "/api/v1/notifications",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_mark_notification_read(client):
    with patch(f"{_NOTIF}.mark_read", new_callable=AsyncMock):
        resp = await client.put(
            "/api/v1/notifications/notif-1/read",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"read": True}


@pytest.mark.asyncio
async def test_mark_all_notifications_read(client):
    with patch(f"{_NOTIF}.mark_all_read", new_callable=AsyncMock):
        resp = await client.put(
            "/api/v1/notifications/read-all",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"read_all": True}


@pytest.mark.asyncio
async def test_notifications_no_token(client):
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# FILES
# ═══════════════════════════════════════════════════════════════════════════════

_FILE_SVC = "app.api.routes.files.file_service"
_AUDIT = "app.api.routes.files.log_audit"

MOCK_FILE_META = {
    "_id": "file-1", "patient_id": "p1", "encounter_id": "enc-1",
    "filename": "test.pdf", "content_type": "application/pdf",
    "size_bytes": 1024, "s3_key": "patients/p1/file-1/test.pdf",
    "uploaded_by": "doctor-id", "deleted": False,
}


@pytest.mark.asyncio
async def test_upload_file_success(client):
    with patch(f"{_FILE_SVC}.upload_file", new_callable=AsyncMock, return_value=MOCK_FILE_META), \
         patch(_AUDIT, new_callable=AsyncMock):
        resp = await client.post(
            "/api/v1/files/upload",
            files={"file": ("test.pdf", b"%PDF-1.4 content", "application/pdf")},
            data={"patient_id": "p1", "encounter_id": "enc-1"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json()["filename"] == "test.pdf"


@pytest.mark.asyncio
async def test_upload_file_invalid_type(client):
    with patch(f"{_FILE_SVC}.upload_file", new_callable=AsyncMock,
               side_effect=ValueError("Unsupported file type: text/plain")):
        resp = await client.post(
            "/api/v1/files/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
            data={"patient_id": "p1"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_file_meta_found(client):
    with patch(f"{_FILE_SVC}.get_file_meta", new_callable=AsyncMock, return_value=MOCK_FILE_META):
        resp = await client.get(
            "/api/v1/files/file-1",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json()["filename"] == "test.pdf"


@pytest.mark.asyncio
async def test_get_file_meta_not_found(client):
    with patch(f"{_FILE_SVC}.get_file_meta", new_callable=AsyncMock, return_value=None):
        resp = await client.get(
            "/api/v1/files/nonexistent",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_file_success(client):
    with patch(f"{_FILE_SVC}.get_download_url", new_callable=AsyncMock,
               return_value="https://s3.example.com/presigned"):
        resp = await client.get(
            "/api/v1/files/file-1/download",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert "download_url" in resp.json()


@pytest.mark.asyncio
async def test_download_file_not_found(client):
    with patch(f"{_FILE_SVC}.get_download_url", new_callable=AsyncMock,
               side_effect=ValueError("File not found")):
        resp = await client.get(
            "/api/v1/files/nonexistent/download",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_file_success(client):
    with patch(f"{_FILE_SVC}.delete_file", new_callable=AsyncMock), \
         patch(_AUDIT, new_callable=AsyncMock):
        resp = await client.delete(
            "/api/v1/files/file-1",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}


@pytest.mark.asyncio
async def test_delete_file_researcher_forbidden(client):
    resp = await client.delete(
        "/api/v1/files/file-1",
        headers={"Authorization": f"Bearer {_token('researcher')}"},
    )
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# GDPR
# ═══════════════════════════════════════════════════════════════════════════════

_CONSENT_SVC = "app.api.routes.gdpr.consent_service"
_GDPR_AUDIT = "app.api.routes.gdpr.log_audit"


@pytest.mark.asyncio
async def test_update_consent(client):
    with patch(f"{_CONSENT_SVC}.update_consent", new_callable=AsyncMock), \
         patch(_GDPR_AUDIT, new_callable=AsyncMock):
        resp = await client.put(
            "/api/v1/patients/p1/consents",
            json={"type": "data_processing", "granted": True, "version": "1.0"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"updated": True}


@pytest.mark.asyncio
async def test_export_patient_data(client):
    export_data = {
        "patient": MOCK_PATIENT, "encounters": [], "observations": [],
        "conditions": [], "medications": [], "files_metadata": [],
        "conversations": [], "consents": None, "exported_at": "2024-01-01T00:00:00+00:00",
    }
    with patch(f"{_CONSENT_SVC}.export_patient_data", new_callable=AsyncMock, return_value=export_data), \
         patch(_GDPR_AUDIT, new_callable=AsyncMock):
        resp = await client.get(
            "/api/v1/patients/p1/export",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert "patient" in resp.json()


@pytest.mark.asyncio
async def test_export_patient_data_nurse_forbidden(client):
    resp = await client.get(
        "/api/v1/patients/p1/export",
        headers={"Authorization": f"Bearer {_token('nurse')}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_consents_returns_empty_when_none(client):
    with patch(f"{_CONSENT_SVC}.get_consents", new_callable=AsyncMock, return_value=None):
        resp = await client.get(
            "/api/v1/patients/p1/consents",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json() == {"patient_id": "p1", "consents": []}


# ═══════════════════════════════════════════════════════════════════════════════
# PATIENTS - missing paths
# ═══════════════════════════════════════════════════════════════════════════════

_PAT_SVC = "app.api.routes.patients.patient_service"
_PAT_AUDIT = "app.api.routes.patients.log_audit"

PATIENT_PAYLOAD = {
    "given_name": "Ama", "family_name": "Kofi", "date_of_birth": "1990-05-15",
    "gender": "female", "phone": "+228 90 00 00 00", "locale": "fr",
}


@pytest.mark.asyncio
async def test_update_patient_not_found(client):
    with patch(f"{_PAT_SVC}.update_patient", new_callable=AsyncMock, return_value=None):
        resp = await client.put(
            "/api/v1/patients/nonexistent",
            json={"phone": "+228 99 99 99 99"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_patient_timeline(client):
    timeline = {"encounters": [], "observations": [], "conditions": [], "medications": []}
    with patch(f"{_PAT_SVC}.get_timeline", new_callable=AsyncMock, return_value=timeline):
        resp = await client.get(
            "/api/v1/patients/p1/timeline",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert "encounters" in resp.json()


@pytest.mark.asyncio
async def test_create_patient_success(client):
    with patch(f"{_PAT_SVC}.create_patient", new_callable=AsyncMock, return_value=MOCK_PATIENT), \
         patch(_PAT_AUDIT, new_callable=AsyncMock):
        resp = await client.post(
            "/api/v1/patients",
            json=PATIENT_PAYLOAD,
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_patient_with_audit(client):
    with patch(f"{_PAT_SVC}.get_patient", new_callable=AsyncMock, return_value=MOCK_PATIENT), \
         patch(_PAT_AUDIT, new_callable=AsyncMock):
        resp = await client.get(
            "/api/v1/patients/p1",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_patient_success(client):
    updated = {**MOCK_PATIENT, "phone": "+228 11 11 11 11"}
    with patch(f"{_PAT_SVC}.update_patient", new_callable=AsyncMock, return_value=updated), \
         patch(_PAT_AUDIT, new_callable=AsyncMock):
        resp = await client.put(
            "/api/v1/patients/p1",
            json={"phone": "+228 11 11 11 11"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_patient_success(client):
    with patch(f"{_PAT_SVC}.delete_patient", new_callable=AsyncMock), \
         patch(_PAT_AUDIT, new_callable=AsyncMock):
        resp = await client.delete(
            "/api/v1/patients/p1",
            headers={"Authorization": f"Bearer {_token('admin')}"},
        )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# CLINICAL - unsupported resource type + CRUD paths
# ═══════════════════════════════════════════════════════════════════════════════

_CLIN_SVC = "app.api.routes.clinical.clinical_service"


@pytest.mark.asyncio
async def test_list_fhir_unsupported_resource(client):
    resp = await client.get(
        "/api/v1/fhir/UnknownResource",
        headers={"Authorization": f"Bearer {_token('doctor')}"},
    )
    assert resp.status_code == 400
    assert "Unsupported resource" in resp.json()["error"]["message"]


@pytest.mark.asyncio
async def test_create_fhir_unsupported_resource(client):
    resp = await client.post(
        "/api/v1/fhir/UnknownResource",
        json={"patient_id": "p1"},
        headers={"Authorization": f"Bearer {_token('doctor')}"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_fhir_resource_found(client):
    with patch(f"{_CLIN_SVC}.get_resource", new_callable=AsyncMock, return_value=MOCK_ENCOUNTER):
        resp = await client.get(
            "/api/v1/fhir/Encounter/enc-1",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_fhir_resource_not_found(client):
    with patch(f"{_CLIN_SVC}.get_resource", new_callable=AsyncMock, return_value=None):
        resp = await client.get(
            "/api/v1/fhir/Encounter/nonexistent",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_fhir_unsupported_resource(client):
    resp = await client.get(
        "/api/v1/fhir/UnknownResource/some-id",
        headers={"Authorization": f"Bearer {_token('doctor')}"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_update_fhir_resource_found(client):
    with patch(f"{_CLIN_SVC}.update_resource", new_callable=AsyncMock, return_value=MOCK_ENCOUNTER):
        resp = await client.put(
            "/api/v1/fhir/Encounter/enc-1",
            json={"notes": "Updated notes"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_fhir_resource_not_found(client):
    with patch(f"{_CLIN_SVC}.update_resource", new_callable=AsyncMock, return_value=None):
        resp = await client.put(
            "/api/v1/fhir/Encounter/nonexistent",
            json={"notes": "Updated notes"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_fhir_unsupported_resource(client):
    resp = await client.put(
        "/api/v1/fhir/UnknownResource/some-id",
        json={"notes": "Updated notes"},
        headers={"Authorization": f"Bearer {_token('doctor')}"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_fhir_encounter(client):
    with patch(f"{_CLIN_SVC}.create_encounter", new_callable=AsyncMock, return_value=MOCK_ENCOUNTER):
        resp = await client.post(
            "/api/v1/fhir/Encounter",
            json={"patient_id": "p1", "practitioner_id": "doc-1", "type": "consultation"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# SURVEILLANCE - trends, alerts, report
# ═══════════════════════════════════════════════════════════════════════════════

_SURV_SVC = "app.api.routes.surveillance.surveillance_service"


@pytest.mark.asyncio
async def test_surveillance_trends(client):
    with patch(f"{_SURV_SVC}.get_trends", new_callable=AsyncMock, return_value=[]):
        resp = await client.get(
            "/api/v1/surveillance/trends?disease_code=A90",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_surveillance_alerts(client):
    with patch(f"{_SURV_SVC}.get_alerts", new_callable=AsyncMock, return_value=[]):
        resp = await client.get(
            "/api/v1/surveillance/alerts",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_surveillance_submit_report(client):
    report_doc = {
        "id": "rep-1", "region": "Lomé", "disease_code": "A90",
        "case_count": 5, "date": "2024-01-01", "reporter_id": "doc-1",
    }
    with patch(f"{_SURV_SVC}.submit_report", new_callable=AsyncMock, return_value=report_doc):
        resp = await client.post(
            "/api/v1/surveillance/report",
            json={"region": "Lomé", "disease_code": "A90", "case_count": 5, "date": "2024-01-01"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert resp.json()["disease_code"] == "A90"


# ═══════════════════════════════════════════════════════════════════════════════
# AI - literature and translate endpoints
# ═══════════════════════════════════════════════════════════════════════════════

_AI_SVC = "app.api.routes.ai.ai_service"
_AI_AUDIT = "app.api.routes.ai.log_audit"

_ai_resp = AIResponse(
    answer="Test", confidence=0.9, sources=[],
    disclaimer="Ceci est généré par l'IA et doit être vérifié par un clinicien.",
    locale="fr",
)


@pytest.mark.asyncio
async def test_ai_literature_researcher_allowed(client):
    with patch(f"{_AI_SVC}.literature", new_callable=AsyncMock, return_value=_ai_resp), \
         patch(_AI_AUDIT, new_callable=AsyncMock):
        resp = await client.post(
            "/api/v1/ai/literature",
            json={"topic": "malaria treatment", "locale": "fr"},
            headers={"Authorization": f"Bearer {_token('researcher')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_translate(client):
    with patch(f"{_AI_SVC}.translate", new_callable=AsyncMock, return_value=_ai_resp):
        resp = await client.post(
            "/api/v1/ai/translate",
            json={"text": "Hello world", "target_locale": "fr"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_differential_with_audit(client):
    with patch(f"{_AI_SVC}.differential", new_callable=AsyncMock, return_value=_ai_resp), \
         patch(_AI_AUDIT, new_callable=AsyncMock):
        resp = await client.post(
            "/api/v1/ai/differential",
            json={"symptoms": ["fever", "chills"], "locale": "fr"},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_query_with_audit(client):
    with patch(f"{_AI_SVC}.query", new_callable=AsyncMock, return_value=_ai_resp), \
         patch(_AI_AUDIT, new_callable=AsyncMock):
        resp = await client.post(
            "/api/v1/ai/query",
            json={"question": "What is dengue?", "context": {"locale": "fr"}},
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# PATIENT FILES route
# ═══════════════════════════════════════════════════════════════════════════════

_PF_SVC = "app.api.routes.patient_files.file_service"


@pytest.mark.asyncio
async def test_patient_files_list(client):
    with patch(f"{_PF_SVC}.list_patient_files", new_callable=AsyncMock, return_value=[MOCK_FILE_META]):
        resp = await client.get(
            "/api/v1/patients/p1/files",
            headers={"Authorization": f"Bearer {_token('doctor')}"},
        )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICES - direct unit tests for uncovered service functions
# ═══════════════════════════════════════════════════════════════════════════════

# ── notification_service ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_notification_service_create():
    from app.services import notification_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.notification_service.db", return_value=mock_db):
        result = await notification_service.create_notification("user-1", "Alert", "Body text")
    assert result["user_id"] == "user-1"
    assert result["title"] == "Alert"
    assert result["read"] is False


@pytest.mark.asyncio
async def test_notification_service_list():
    from app.services import notification_service
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.notification_service.db", return_value=mock_db):
        result = await notification_service.list_notifications("user-1")
    assert result == []


@pytest.mark.asyncio
async def test_notification_service_mark_read():
    from app.services import notification_service
    mock_col = MagicMock()
    mock_col.update_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.notification_service.db", return_value=mock_db):
        await notification_service.mark_read("notif-1")
    mock_col.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_notification_service_mark_all_read():
    from app.services import notification_service
    mock_col = MagicMock()
    mock_col.update_many = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.notification_service.db", return_value=mock_db):
        await notification_service.mark_all_read("user-1")
    mock_col.update_many.assert_called_once()


# ── surveillance_service ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_surveillance_service_get_dashboard():
    from app.services import surveillance_service
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_col = MagicMock()
    mock_col.aggregate = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.surveillance_service.db", return_value=mock_db):
        result = await surveillance_service.get_dashboard("Lomé", "A90", "2024-01-01", "2024-12-31")
    assert "aggregations" in result


@pytest.mark.asyncio
async def test_surveillance_service_get_trends():
    from app.services import surveillance_service
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.surveillance_service.db", return_value=mock_db):
        result = await surveillance_service.get_trends("A90", "day", "2024-01-01", "2024-12-31")
    assert result == []


@pytest.mark.asyncio
async def test_surveillance_service_get_alerts():
    from app.services import surveillance_service
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.surveillance_service.db", return_value=mock_db):
        result = await surveillance_service.get_alerts()
    assert result == []


@pytest.mark.asyncio
async def test_surveillance_service_submit_report():
    from app.models.schemas import SurveillanceReport
    from app.services import surveillance_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    report = SurveillanceReport(region="Lomé", disease_code="A90", case_count=5, date="2024-01-01")
    with patch("app.services.surveillance_service.db", return_value=mock_db):
        result = await surveillance_service.submit_report(report)
    assert result["disease_code"] == "A90"
    assert result["region"] == "Lomé"


# ── clinical_service ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clinical_service_create_encounter():
    from app.models.schemas import EncounterCreate
    from app.services import clinical_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = EncounterCreate(patient_id="p1", practitioner_id="doc-1")
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.create_encounter(data)
    assert result["patient_id"] == "p1"
    assert "_id" in result


@pytest.mark.asyncio
async def test_clinical_service_create_observation():
    from app.models.schemas import ObservationCreate
    from app.services import clinical_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = ObservationCreate(patient_id="p1", code="temperature", value="37.5")
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.create_observation(data)
    assert result["code"] == "temperature"


@pytest.mark.asyncio
async def test_clinical_service_create_condition():
    from app.models.schemas import ConditionCreate
    from app.services import clinical_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = ConditionCreate(patient_id="p1", code="A90", display="Dengue fever")
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.create_condition(data)
    assert result["code"] == "A90"


@pytest.mark.asyncio
async def test_clinical_service_create_medication():
    from app.models.schemas import MedicationCreate
    from app.services import clinical_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = MedicationCreate(patient_id="p1", code="J01CA04", display="Amoxicillin")
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.create_medication(data)
    assert result["code"] == "J01CA04"


@pytest.mark.asyncio
async def test_clinical_service_get_resource():
    from app.services import clinical_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=MOCK_ENCOUNTER)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.get_resource("encounters", "enc-1")
    assert result["_id"] == "enc-1"


@pytest.mark.asyncio
async def test_clinical_service_update_resource():
    from app.services import clinical_service
    updated = {**MOCK_ENCOUNTER, "notes": "Updated"}
    mock_col = MagicMock()
    mock_col.find_one_and_update = AsyncMock(return_value=updated)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.update_resource("encounters", "enc-1", {"notes": "Updated"})
    assert result["notes"] == "Updated"


@pytest.mark.asyncio
async def test_clinical_service_list_resources():
    from app.services import clinical_service
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[MOCK_ENCOUNTER])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.clinical_service.db", return_value=mock_db):
        result = await clinical_service.list_resources("encounters", "p1")
    assert len(result) == 1


# ── consent_service ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_consent_service_get_consents():
    from app.services import consent_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value={"patient_id": "p1", "consents": []})
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.consent_service.db", return_value=mock_db):
        result = await consent_service.get_consents("p1")
    assert result["patient_id"] == "p1"


@pytest.mark.asyncio
async def test_consent_service_update_consent():
    from app.models.schemas import Consent
    from app.services import consent_service
    mock_update_result = MagicMock()
    mock_update_result.matched_count = 1
    mock_col = MagicMock()
    mock_col.update_one = AsyncMock(return_value=mock_update_result)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    consent = Consent(type="data_processing", granted=True)
    with patch("app.services.consent_service.db", return_value=mock_db):
        await consent_service.update_consent("p1", consent)
    assert mock_col.update_one.call_count >= 1


@pytest.mark.asyncio
async def test_consent_service_export_patient_data():
    from app.services import consent_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=MOCK_PATIENT)
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.consent_service.db", return_value=mock_db):
        result = await consent_service.export_patient_data("p1")
    assert "patient" in result
    assert "exported_at" in result


# ── patient_service ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_patient_service_create():
    from app.models.schemas import PatientCreate
    from app.services import patient_service
    mock_col = MagicMock()
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = PatientCreate(given_name="Ama", family_name="Kofi", date_of_birth="1990-01-01", gender="female")
    with patch("app.services.patient_service.db", return_value=mock_db):
        result = await patient_service.create_patient(data)
    assert result["given_name"] == "Ama"
    assert result["name_text"] == "Ama Kofi"


@pytest.mark.asyncio
async def test_patient_service_get():
    from app.services import patient_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=MOCK_PATIENT)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.patient_service.db", return_value=mock_db):
        result = await patient_service.get_patient("p1")
    assert result["_id"] == "p1"


@pytest.mark.asyncio
async def test_patient_service_list():
    from app.services import patient_service
    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[MOCK_PATIENT])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_col.count_documents = AsyncMock(return_value=1)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.patient_service.db", return_value=mock_db):
        result = await patient_service.list_patients("Ama", 1, 20, "active")
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_patient_service_update():
    from app.services import patient_service
    updated = {**MOCK_PATIENT, "phone": "+228 99 99 99 99"}
    mock_col = MagicMock()
    mock_col.find_one_and_update = AsyncMock(return_value=updated)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.patient_service.db", return_value=mock_db):
        result = await patient_service.update_patient("p1", {"phone": "+228 99 99 99 99"})
    assert result["phone"] == "+228 99 99 99 99"


@pytest.mark.asyncio
async def test_patient_service_delete():
    from app.services import patient_service
    mock_col = MagicMock()
    mock_col.update_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.patient_service.db", return_value=mock_db):
        await patient_service.delete_patient("p1")
    mock_col.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_patient_service_get_timeline():
    from app.services import patient_service
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.patient_service.db", return_value=mock_db):
        result = await patient_service.get_timeline("p1")
    assert "encounters" in result
    assert "observations" in result


# ── auth_service ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_auth_service_register():
    from app.models.schemas import UserCreate
    from app.services import auth_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=None)
    mock_col.insert_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = UserCreate(email="new@example.com", password="secret123", full_name="New User")
    with patch("app.services.auth_service.db", return_value=mock_db):
        result = await auth_service.register(data)
    assert result.email == "new@example.com"


@pytest.mark.asyncio
async def test_auth_service_register_duplicate():
    from app.models.schemas import UserCreate
    from app.services import auth_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value={"email": "existing@example.com"})
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    data = UserCreate(email="existing@example.com", password="secret123", full_name="Existing")
    with (
        patch("app.services.auth_service.db", return_value=mock_db),
        pytest.raises(ValueError, match="Email already registered"),
    ):
        await auth_service.register(data)


@pytest.mark.asyncio
async def test_auth_service_login_success():
    from app.core.security import hash_password
    from app.services import auth_service
    user_doc = {
        "_id": "user-1", "email": "doc@example.com",
        "hashed_password": hash_password("correct"), "role": "doctor",
        "locale": "fr", "is_active": True,
    }
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=user_doc)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.auth_service.db", return_value=mock_db):
        result = await auth_service.login("doc@example.com", "correct", _settings)
    assert "access_token" in result


@pytest.mark.asyncio
async def test_auth_service_login_invalid():
    from app.services import auth_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=None)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with (
        patch("app.services.auth_service.db", return_value=mock_db),
        pytest.raises(ValueError, match="Invalid credentials"),
    ):
        await auth_service.login("bad@example.com", "wrong", _settings)


@pytest.mark.asyncio
async def test_auth_service_setup_mfa():
    from app.services import auth_service
    mock_col = MagicMock()
    mock_col.update_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.auth_service.db", return_value=mock_db):
        result = await auth_service.setup_mfa("user-1")
    assert "secret" in result
    assert "uri" in result


@pytest.mark.asyncio
async def test_auth_service_verify_mfa_no_secret():
    from app.services import auth_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value={"_id": "user-1", "mfa_secret": None})
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with (
        patch("app.services.auth_service.db", return_value=mock_db),
        pytest.raises(ValueError, match="MFA not configured"),
    ):
        await auth_service.verify_mfa("user-1", "123456")


# ── ai_service ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ai_service_query():
    from app.models.schemas import AIQueryRequest
    from app.services import ai_service
    raw = {"answer": "Malaria is...", "confidence": 0.9, "sources": []}
    with patch("app.services.ai_service._call_inference", new_callable=AsyncMock, return_value=raw):
        req = AIQueryRequest(question="What is malaria?", context={"locale": "fr"})
        result = await ai_service.query(req)
    assert result.answer == "Malaria is..."
    assert result.confidence == 0.9


@pytest.mark.asyncio
async def test_ai_service_differential():
    from app.models.schemas import AIDifferentialRequest
    from app.services import ai_service
    raw = {"answer": "Differential: dengue", "confidence": 0.85, "sources": []}
    with patch("app.services.ai_service._call_inference", new_callable=AsyncMock, return_value=raw):
        req = AIDifferentialRequest(symptoms=["fever", "headache"], locale="fr")
        result = await ai_service.differential(req)
    assert "dengue" in result.answer


@pytest.mark.asyncio
async def test_ai_service_literature():
    from app.models.schemas import AILiteratureRequest
    from app.services import ai_service
    raw = {"answer": "Literature on malaria...", "confidence": 0.8, "sources": ["pub1"]}
    with patch("app.services.ai_service._call_inference", new_callable=AsyncMock, return_value=raw):
        req = AILiteratureRequest(topic="malaria treatment", locale="fr")
        result = await ai_service.literature(req)
    assert result.sources == ["pub1"]


@pytest.mark.asyncio
async def test_ai_service_translate():
    from app.models.schemas import AITranslateRequest
    from app.services import ai_service
    raw = {"answer": "Bonjour monde", "confidence": 0.99, "sources": []}
    with patch("app.services.ai_service._call_inference", new_callable=AsyncMock, return_value=raw):
        req = AITranslateRequest(text="Hello world", target_locale="fr")
        result = await ai_service.translate(req)
    assert result.answer == "Bonjour monde"


@pytest.mark.asyncio
async def test_ai_service_low_confidence_disclaimer():
    from app.models.schemas import AIQueryRequest
    from app.services import ai_service
    raw = {"answer": "Uncertain answer", "confidence": 0.4, "sources": []}
    with patch("app.services.ai_service._call_inference", new_callable=AsyncMock, return_value=raw):
        req = AIQueryRequest(question="What is X?", context={"locale": "en"})
        result = await ai_service.query(req)
    assert "⚠️" in result.disclaimer
    assert "Low confidence" in result.disclaimer or "Faible confiance" in result.disclaimer


# ── file_service ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_file_service_upload_invalid_type():
    from app.services import file_service
    with pytest.raises(ValueError, match="Unsupported file type"):
        await file_service.upload_file(b"data", "test.exe", "application/x-msdownload", "p1", "", "user-1")


@pytest.mark.asyncio
async def test_file_service_upload_too_large():
    from app.services import file_service
    big_data = b"x" * (51 * 1024 * 1024)
    with pytest.raises(ValueError, match="50 MB"):
        await file_service.upload_file(big_data, "big.pdf", "application/pdf", "p1", "", "user-1")


@pytest.mark.asyncio
async def test_file_service_get_meta():
    from app.services import file_service
    mock_col = MagicMock()
    mock_col.find_one = AsyncMock(return_value=MOCK_FILE_META)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.file_service.db", return_value=mock_db):
        result = await file_service.get_file_meta("file-1")
    assert result["_id"] == "file-1"


@pytest.mark.asyncio
async def test_file_service_delete():
    from app.services import file_service
    mock_col = MagicMock()
    mock_col.update_one = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.file_service.db", return_value=mock_db):
        await file_service.delete_file("file-1")
    mock_col.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_file_service_list_patient_files():
    from app.services import file_service
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[MOCK_FILE_META])
    mock_col = MagicMock()
    mock_col.find = MagicMock(return_value=mock_cursor)
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_col)
    with patch("app.services.file_service.db", return_value=mock_db):
        result = await file_service.list_patient_files("p1")
    assert len(result) == 1
