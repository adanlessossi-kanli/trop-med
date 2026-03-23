from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


def utcnow():
    return datetime.now(UTC)


# ── Users ──

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["admin", "doctor", "nurse", "researcher", "patient"] = "patient"
    locale: Literal["fr", "en"] = "fr"


class UserInDB(BaseModel):
    id: str = Field(alias="_id", default="")
    email: str
    hashed_password: str
    full_name: str
    role: str
    locale: str
    mfa_enabled: bool = False
    mfa_secret: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    locale: str
    mfa_enabled: bool = False
    is_active: bool = True


# ── Patients ──

class PatientCreate(BaseModel):
    given_name: str
    family_name: str
    date_of_birth: str
    gender: Literal["male", "female", "other", "unknown"]
    phone: str = ""
    email: str = ""
    address: str = ""
    national_id: str = ""
    locale: Literal["fr", "en"] = "fr"


class PatientInDB(BaseModel):
    id: str = Field(alias="_id", default="")
    fhir_id: str = ""
    given_name: str
    family_name: str
    name_text: str = ""
    date_of_birth: str
    gender: str
    phone: str = ""
    email: str = ""
    address: str = ""
    national_id: str = ""
    locale: str = "fr"
    status: Literal["active", "inactive"] = "active"
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


# ── Clinical ──

class EncounterCreate(BaseModel):
    patient_id: str
    practitioner_id: str
    type: str = "consultation"
    reason: str = ""
    notes: str = ""


class ObservationCreate(BaseModel):
    patient_id: str
    encounter_id: str = ""
    code: str  # e.g. "temperature", "blood_pressure"
    value: str
    unit: str = ""


class ConditionCreate(BaseModel):
    patient_id: str
    encounter_id: str = ""
    code: str  # ICD-10
    display: str
    clinical_status: Literal["active", "resolved", "inactive"] = "active"


class MedicationCreate(BaseModel):
    patient_id: str
    encounter_id: str = ""
    code: str
    display: str
    dosage: str = ""
    status: Literal["active", "completed", "stopped"] = "active"


# ── Conversations ──

class MessageCreate(BaseModel):
    content: str
    locale: Literal["fr", "en"] = "fr"


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    confidence: float | None = None
    sources: list[str] = []
    timestamp: datetime = Field(default_factory=utcnow)


# ── Files ──

class FileMetadata(BaseModel):
    id: str = ""
    patient_id: str = ""
    encounter_id: str = ""
    filename: str
    content_type: str
    size_bytes: int = 0
    s3_key: str = ""
    uploaded_by: str = ""
    created_at: datetime = Field(default_factory=utcnow)
    deleted: bool = False


# ── Surveillance ──

class SurveillanceReport(BaseModel):
    region: str
    disease_code: str
    case_count: int
    date: str
    reporter_id: str = ""


# ── Notifications ──

class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    read: bool = False
    created_at: datetime = Field(default_factory=utcnow)


# ── Consent ──

class Consent(BaseModel):
    type: Literal["data_processing", "ai_analysis", "research_use"]
    granted: bool
    timestamp: datetime = Field(default_factory=utcnow)
    version: str = "1.0"


class PatientConsent(BaseModel):
    patient_id: str
    consents: list[Consent] = []


# ── AI ──

class AIQueryRequest(BaseModel):
    question: str
    context: dict = {}
    max_tokens: int = 1024


class AIDifferentialRequest(BaseModel):
    symptoms: list[str]
    vitals: dict = {}
    demographics: dict = {}
    history: str = ""
    locale: Literal["fr", "en"] = "fr"


class AILiteratureRequest(BaseModel):
    topic: str
    locale: Literal["fr", "en"] = "fr"


class AITranslateRequest(BaseModel):
    text: str
    target_locale: Literal["fr", "en"] = "fr"


class AIResponse(BaseModel):
    answer: str
    confidence: float = 0.0
    sources: list[str] = []
    disclaimer: str = "Ceci est généré par l'IA et doit être vérifié par un clinicien."
    locale: str = "fr"
