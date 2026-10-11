import re
from typing import Dict, Any, List, Optional
from app.schemas import ClinicalAnalysisResult, LabMetricItem, MedicationItem, MedicationTiming, ReferenceInterval

# Standard clinical reference database for validation & cross-referencing
CLINICAL_REFERENCE_RANGES: Dict[str, Dict[str, Any]] = {
    "vitamin d": {"min": 30.0, "max": 100.0, "unit": "ng/mL", "category": "Vitamins", "critical_low": 10.0},
    "vitamin d3": {"min": 30.0, "max": 100.0, "unit": "ng/mL", "category": "Vitamins", "critical_low": 10.0},
    "25-hydroxy vitamin d": {"min": 30.0, "max": 100.0, "unit": "ng/mL", "category": "Vitamins", "critical_low": 10.0},
    "vitamin b12": {"min": 200.0, "max": 900.0, "unit": "pg/mL", "category": "Vitamins", "critical_low": 150.0},
    "hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL", "category": "Hematology", "critical_low": 7.0, "critical_high": 20.0},
    "fasting blood sugar": {"min": 70.0, "max": 99.0, "unit": "mg/dL", "category": "Biochemistry", "critical_high": 200.0, "critical_low": 50.0},
    "fasting glucose": {"min": 70.0, "max": 99.0, "unit": "mg/dL", "category": "Biochemistry", "critical_high": 200.0, "critical_low": 50.0},
    "post prandial blood sugar": {"min": 70.0, "max": 140.0, "unit": "mg/dL", "category": "Biochemistry", "critical_high": 250.0},
    "ppbs": {"min": 70.0, "max": 140.0, "unit": "mg/dL", "category": "Biochemistry", "critical_high": 250.0},
    "hba1c": {"min": 4.0, "max": 5.6, "unit": "%", "category": "Biochemistry", "critical_high": 9.0},
    "glycated hemoglobin": {"min": 4.0, "max": 5.6, "unit": "%", "category": "Biochemistry", "critical_high": 9.0},
    "serum creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "category": "Renal Function", "critical_high": 3.0},
    "creatinine": {"min": 0.6, "max": 1.2, "unit": "mg/dL", "category": "Renal Function", "critical_high": 3.0},
    "blood urea": {"min": 15.0, "max": 40.0, "unit": "mg/dL", "category": "Renal Function", "critical_high": 80.0},
    "bun": {"min": 7.0, "max": 20.0, "unit": "mg/dL", "category": "Renal Function", "critical_high": 50.0},
    "platelet count": {"min": 150.0, "max": 450.0, "unit": "10^3/mcL", "category": "Hematology", "critical_low": 50.0, "critical_high": 800.0},
    "total cholesterol": {"min": 125.0, "max": 200.0, "unit": "mg/dL", "category": "Lipid Profile", "critical_high": 300.0},
    "ldl cholesterol": {"min": 0.0, "max": 100.0, "unit": "mg/dL", "category": "Lipid Profile", "critical_high": 190.0},
    "hdl cholesterol": {"min": 40.0, "max": 60.0, "unit": "mg/dL", "category": "Lipid Profile", "critical_low": 30.0},
    "triglycerides": {"min": 0.0, "max": 150.0, "unit": "mg/dL", "category": "Lipid Profile", "critical_high": 400.0},
    "tsh": {"min": 0.4, "max": 4.2, "unit": "uIU/mL", "category": "Thyroid Profile", "critical_low": 0.05, "critical_high": 15.0},
    "total bilirubin": {"min": 0.2, "max": 1.2, "unit": "mg/dL", "category": "Liver Function", "critical_high": 3.0},
    "sgpt": {"min": 7.0, "max": 56.0, "unit": "U/L", "category": "Liver Function", "critical_high": 200.0},
    "alt": {"min": 7.0, "max": 56.0, "unit": "U/L", "category": "Liver Function", "critical_high": 200.0},
    "sgot": {"min": 10.0, "max": 40.0, "unit": "U/L", "category": "Liver Function", "critical_high": 200.0},
    "ast": {"min": 10.0, "max": 40.0, "unit": "U/L", "category": "Liver Function", "critical_high": 200.0},
    "serum potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L", "category": "Electrolytes", "critical_low": 2.8, "critical_high": 6.2},
    "potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L", "category": "Electrolytes", "critical_low": 2.8, "critical_high": 6.2},
    "serum sodium": {"min": 135.0, "max": 145.0, "unit": "mEq/L", "category": "Electrolytes", "critical_low": 125.0, "critical_high": 155.0},
    "sodium": {"min": 135.0, "max": 145.0, "unit": "mEq/L", "category": "Electrolytes", "critical_low": 125.0, "critical_high": 155.0},
    "wbc": {"min": 4.0, "max": 11.0, "unit": "10^3/mcL", "category": "Hematology", "critical_low": 2.0, "critical_high": 25.0},
    "total leucocyte count": {"min": 4000.0, "max": 11000.0, "unit": "/mcL", "category": "Hematology", "critical_low": 2000.0, "critical_high": 25000.0},
    "esr": {"min": 0.0, "max": 20.0, "unit": "mm/hr", "category": "Inflammatory", "critical_high": 60.0},
}

class ClinicalValidator:
    @staticmethod
    def parse_numeric(val: Any) -> Optional[float]:
        """Extracts first valid floating point number from messy OCR strings"""
        if isinstance(val, (int, float)):
            return float(val)
        if not val or not isinstance(val, str):
            return None
        match = re.search(r"[-+]?\d*\.?\d+", val.replace(",", ""))
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                return None
        return None

    @classmethod
    def validate_and_enhance(cls, data: Dict[str, Any]) -> ClinicalAnalysisResult:
        """
        Takes raw output from Qwen-VL (or fallback mock) and:
        1. Normalizes medication schedule timings (1-0-1, OD, BD, TDS, etc.)
        2. Evaluates lab metrics against numeric boundaries
        3. Isolates out-of-range bounds, highlights severe deviations in vibrant red
        4. Synthesizes clinical alerts
        """
        raw_meds = data.get("medications", [])
        validated_meds: List[MedicationItem] = []

        for med in raw_meds:
            if not isinstance(med, dict):
                continue
            
            drug_name = med.get("drug_name") or med.get("name") or "Unnamed Medication"
            dosage = med.get("dosage", "")
            instructions = med.get("instructions", "")
            
            # Extract timing dictionary or parse from instructions (e.g. 1-0-1, BD, TDS)
            raw_timing = med.get("timing", {})
            morning = raw_timing.get("morning", False) if isinstance(raw_timing, dict) else False
            afternoon = raw_timing.get("afternoon", False) if isinstance(raw_timing, dict) else False
            evening = raw_timing.get("evening", False) if isinstance(raw_timing, dict) else False
            night = raw_timing.get("night", False) if isinstance(raw_timing, dict) else False

            # Infer from shorthand notation if timing is all false
            full_text = f"{instructions} {dosage} {drug_name}".lower()
            if not any([morning, afternoon, evening, night]):
                if "1-0-1" in full_text:
                    morning, afternoon, evening, night = True, False, False, True
                elif "1-1-1" in full_text or "tds" in full_text or "tid" in full_text:
                    morning, afternoon, evening, night = True, True, False, True
                elif "0-0-1" in full_text or "bedtime" in full_text or "hs" in full_text:
                    morning, afternoon, evening, night = False, False, False, True
                elif "1-0-0" in full_text or "od morning" in full_text:
                    morning, afternoon, evening, night = True, False, False, False
                elif "0-1-0" in full_text:
                    morning, afternoon, evening, night = False, True, False, False
                elif "bd" in full_text or "bid" in full_text:
                    morning, afternoon, evening, night = True, False, False, True
                elif "qid" in full_text or "1-1-1-1" in full_text:
                    morning, afternoon, evening, night = True, True, True, True

            food_relation = med.get("food_relation", "After Food")
            if "before food" in full_text or "empty stomach" in full_text or "ac" in full_text:
                food_relation = "Before Food"
            elif "after food" in full_text or "pc" in full_text:
                food_relation = "After Food"

            validated_meds.append(MedicationItem(
                drug_name=drug_name,
                generic_name=med.get("generic_name", ""),
                dosage=dosage,
                form=med.get("form", "Tablet"),
                timing=MedicationTiming(
                    morning=morning,
                    afternoon=afternoon,
                    evening=evening,
                    night=night
                ),
                food_relation=food_relation,
                duration=med.get("duration", "As directed"),
                instructions=instructions,
                confidence=med.get("confidence", "high")
            ))

        # Validate lab metrics
        raw_labs = data.get("lab_metrics", [])
        validated_labs: List[LabMetricItem] = []
        extra_alerts: List[str] = list(data.get("critical_alerts", []))

        for lab in raw_labs:
            if not isinstance(lab, dict):
                continue

            test_name = lab.get("test_name", "Diagnostic Test")
            raw_obs = lab.get("observed_value", "")
            obs_num = cls.parse_numeric(raw_obs)
            unit = lab.get("unit", "")
            
            ref_dict = lab.get("reference_interval", {})
            ref_min = None
            ref_max = None
            ref_text = ""
            
            if isinstance(ref_dict, dict):
                ref_min = ref_dict.get("min")
                ref_max = ref_dict.get("max")
                ref_text = ref_dict.get("text", "")
            
            # Lookup in standard clinical dictionary if reference is missing
            std_ref = None
            lower_name = test_name.lower().strip()
            for key, val in CLINICAL_REFERENCE_RANGES.items():
                if key in lower_name or lower_name in key:
                    std_ref = val
                    break

            if std_ref:
                if ref_min is None:
                    ref_min = std_ref.get("min")
                if ref_max is None:
                    ref_max = std_ref.get("max")
                if not unit:
                    unit = std_ref.get("unit", "")
                if not ref_text and ref_min is not None and ref_max is not None:
                    ref_text = f"{ref_min} - {ref_max} {unit}"

            # Boundary evaluation
            is_out = lab.get("is_out_of_range", False)
            status = lab.get("status", "NORMAL").upper()
            risk_level = lab.get("risk_level", "none").lower()

            if obs_num is not None:
                if ref_min is not None and obs_num < ref_min:
                    is_out = True
                    status = "LOW"
                    risk_level = "moderate"
                    if std_ref and "critical_low" in std_ref and obs_num <= std_ref["critical_low"]:
                        status = "CRITICAL_LOW"
                        risk_level = "critical"
                elif ref_max is not None and obs_num > ref_max:
                    is_out = True
                    status = "HIGH"
                    risk_level = "high"
                    if std_ref and "critical_high" in std_ref and obs_num >= std_ref["critical_high"]:
                        status = "CRITICAL_HIGH"
                        risk_level = "critical"
                elif ref_min is not None and ref_max is not None and ref_min <= obs_num <= ref_max:
                    is_out = False
                    status = "NORMAL"
                    risk_level = "none"

            if is_out and risk_level in ["high", "critical"]:
                alert_msg = f"ALERT [{test_name}]: Observed {raw_obs} {unit} is {status.replace('_', ' ')} (Normal: {ref_text or f'{ref_min}-{ref_max}'})"
                if alert_msg not in extra_alerts:
                    extra_alerts.append(alert_msg)

            validated_labs.append(LabMetricItem(
                test_name=test_name,
                category=lab.get("category", std_ref["category"] if std_ref else "Clinical Chemistry"),
                observed_value=raw_obs,
                unit=unit,
                reference_interval=ReferenceInterval(
                    min=ref_min,
                    max=ref_max,
                    text=ref_text or (f"{ref_min} - {ref_max} {unit}" if (ref_min is not None and ref_max is not None) else "See doctor")
                ),
                status=status,
                is_out_of_range=is_out,
                risk_level=risk_level,
                clinical_significance=lab.get("clinical_significance", "")
            ))

        # Assemble full clinical result
        result = ClinicalAnalysisResult(
            document_type=data.get("document_type", "handwritten_prescription"),
            patient_info=data.get("patient_info", {}),
            doctor_hospital_info=data.get("doctor_hospital_info", {}),
            diagnosis_notes=data.get("diagnosis_notes", []),
            medications=validated_meds,
            lab_metrics=validated_labs,
            critical_alerts=extra_alerts,
            transcription_confidence_summary=data.get("transcription_confidence_summary", "Zero-shot extraction performed with high clinical alignment."),
            metadata=data.get("metadata", {})
        )

        return result

