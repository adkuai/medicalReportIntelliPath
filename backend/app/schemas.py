from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class PatientInfo(BaseModel):
    name: Optional[str] = "Unknown / Not specified"
    age: Optional[str] = "N/A"
    gender: Optional[str] = "N/A"
    date: Optional[str] = "N/A"
    uhid_patient_id: Optional[str] = "N/A"

class DoctorHospitalInfo(BaseModel):
    doctor_name: Optional[str] = "Dr. Unknown"
    clinic_hospital: Optional[str] = "Clinical Practice"
    specialty: Optional[str] = "General Medicine"
    contact: Optional[str] = "N/A"

class MedicationTiming(BaseModel):
    morning: Union[bool, str, int] = False
    afternoon: Union[bool, str, int] = False
    evening: Union[bool, str, int] = False
    night: Union[bool, str, int] = False

class MedicationItem(BaseModel):
    drug_name: str
    generic_name: Optional[str] = ""
    dosage: str = ""
    form: str = "Tablet"
    timing: MedicationTiming = Field(default_factory=MedicationTiming)
    food_relation: str = "After Food"  # "Before Food", "After Food", "With Food", "Empty Stomach"
    duration: str = "As directed"
    instructions: str = ""
    confidence: str = "high"  # "high", "medium", "low"

class ReferenceInterval(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    text: str = ""

class LabMetricItem(BaseModel):
    test_name: str
    category: str = "General Biochemistry"
    observed_value: Union[float, int, str]
    unit: str = ""
    reference_interval: ReferenceInterval = Field(default_factory=ReferenceInterval)
    status: str = "NORMAL"  # "NORMAL", "HIGH", "LOW", "CRITICAL_HIGH", "CRITICAL_LOW", "ABNORMAL"
    is_out_of_range: bool = False
    risk_level: str = "none"  # "none", "moderate", "high", "critical"
    clinical_significance: Optional[str] = ""

class ClinicalAnalysisResult(BaseModel):
    document_type: str = "handwritten_prescription"  # "handwritten_prescription", "laboratory_report", "composite_chart"
    patient_info: PatientInfo = Field(default_factory=PatientInfo)
    doctor_hospital_info: DoctorHospitalInfo = Field(default_factory=DoctorHospitalInfo)
    diagnosis_notes: List[str] = Field(default_factory=list)
    medications: List[MedicationItem] = Field(default_factory=list)
    lab_metrics: List[LabMetricItem] = Field(default_factory=list)
    critical_alerts: List[str] = Field(default_factory=list)
    transcription_confidence_summary: str = "Zero-shot extraction performed with high clinical alignment."
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ColabStatusResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    colab_url: str
    accessible: bool
    model_name: Optional[str] = "Qwen/Qwen2.5-VL-7B-Instruct"
    latency_ms: Optional[float] = None
    message: str

