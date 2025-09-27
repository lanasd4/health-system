from rest_framework import serializers
from .models import (
    Patient, PatientIdentifier, Appointment, Encounter, Observation, Medication, DocumentRef,
    Condition, Consent, ConditionDictionary, ObservationDictionary, MedicationDictionary, Allergy
)


# ----- Patients -----
class PatientIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientIdentifier
        fields = ("id", "type", "value", "is_primary")

class PatientSerializer(serializers.ModelSerializer):
    identifiers = PatientIdentifierSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = (
            "id", "name", "date_of_birth", "gender",
            "phone", "email", "address", "blood_type",
            "identifiers",
        )

# ----- Appointments -----
class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    practitioner_name = serializers.CharField(source="practitioner.username", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient", "patient_name",
            "practitioner", "practitioner_name",
            "start_at", "end_at",
            "reason", "location",
            "status", "encounter",
            "created_at",
        )

# ----- Encounters -----
class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = ("id", "patient", "start_at", "end_at", "type", "reason")

# ----- Observations -----
class ObservationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = Observation
        fields = (
            "id", "patient", "patient_name",
            "encounter", "code", "value", "unit", "observed_at",
        )

# ----- Medications -----
class MedicationSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = Medication
        # ✅ عدلنا "name" → "local_name" ليتوافق مع الموديل
        fields = (
            "id", "patient", "patient_name",
            "encounter", "code", "local_name", "dose", "frequency",
            "start_date", "end_date", "status",
        )

# ----- Documents -----
class DocumentRefSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = DocumentRef
        fields = (
            "id", "patient", "patient_name",
            "encounter", "doc_type", "title",
            "file", "uploaded_at",
        )

# ----- Conditions -----
class ConditionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    code_name = serializers.CharField(source="code.name", read_only=True)  # ✅ إظهار اسم التشخيص من الـ Dictionary

    class Meta:
        model = Condition
        # ✅ عدلنا "name" → "code" + ضفنا code_name للعرض
        fields = (
            "id", "patient", "patient_name",
            "code", "code_name", "status", "onset_date",
        )

# ----- Consents -----
class ConsentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = Consent
        fields = (
            "id", "patient", "patient_name",
            "status", "valid_from", "valid_to", "purpose",
        )


# ----- Reference Dictionaries (Autocomplete) -----
class ConditionDictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionDictionary
        fields = ("id", "code", "name")

class ObservationDictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationDictionary
        fields = ("id", "code", "name")

class MedicationDictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationDictionary
        fields = ("id", "code", "name")

# ----- Allergies -----
class AllergySerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = Allergy
        fields = (
            "id", "patient", "patient_name",
            "substance", "reaction", "severity", "recorded_date",
        )
