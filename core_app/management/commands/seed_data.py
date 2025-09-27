from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core_app.models import (
    Patient, Appointment, Encounter, Observation, Medication, DocumentRef,
    Condition, Consent, Allergy,
    ConditionDictionary, ObservationDictionary, MedicationDictionary
)
from django.utils.timezone import now, timedelta


class Command(BaseCommand):
    help = "إضافة بيانات تجريبية + قواميس طبية (Seed Data)"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 بدء إضافة البيانات...")

        # -------------------------------
        # 1) إنشاء مجموعات (Roles)
        # -------------------------------
        roles = ["Admin", "Doctor", "Nurse", "Patient"]
        for role in roles:
            Group.objects.get_or_create(name=role)

        # -------------------------------
        # 2) إنشاء مستخدمين
        # -------------------------------
        admin_user, _ = User.objects.get_or_create(username="admin_test", defaults={"email": "admin@example.com"})
        admin_user.set_password("admin12345")
        admin_user.save()
        admin_user.groups.add(Group.objects.get(name="Admin"))

        doctor, _ = User.objects.get_or_create(username="dr_smith", defaults={"email": "dr.smith@example.com"})
        doctor.set_password("doctor12345")
        doctor.save()
        doctor.groups.add(Group.objects.get(name="Doctor"))

        patient_user, _ = User.objects.get_or_create(username="john_doe", defaults={"email": "john.doe@example.com"})
        patient_user.set_password("patient12345")
        patient_user.save()
        patient_user.groups.add(Group.objects.get(name="Patient"))

        # -------------------------------
        # 3) إنشاء مريض
        # -------------------------------
        patient, _ = Patient.objects.get_or_create(
            user=patient_user,
            name="John Doe",
            date_of_birth="1990-05-20",
            gender="M",
            phone="0912123456",
            email="john.doe@example.com",
            address="New York, USA",
            blood_type="O+",
        )

        # -------------------------------
        # 4) Dictionaries (ICD, LOINC, RxNorm)
        # -------------------------------
        conditions = [
            ("J10", "Influenza (Flu)"),
            ("U07.1", "COVID-19"),
        ]
        for code, name in conditions:
            ConditionDictionary.objects.get_or_create(code=code, defaults={"name": name})

        observations = [
            ("8480-6", "Systolic Blood Pressure"),
            ("2345-7", "Glucose [mg/dL]"),
            ("718-7", "Hemoglobin [Mass/volume] in Blood"),
        ]
        for code, name in observations:
            ObservationDictionary.objects.get_or_create(code=code, defaults={"name": name})

        medications = [
            ("1049630", "Paracetamol 500mg Oral Tablet"),
            ("197361", "Amoxicillin 500mg Capsule"),
            ("860975", "Metformin 500mg Tablet"),
        ]
        for code, name in medications:
            MedicationDictionary.objects.get_or_create(code=code, defaults={"name": name})

        # -------------------------------
        # 5) إنشاء Encounter (زيارة)
        # -------------------------------
        encounter = Encounter.objects.create(
            patient=patient,
            start_at=now(),
            end_at=now() + timedelta(hours=1),
            type="OUTPATIENT",
            reason="Follow-up for flu",
        )

        # -------------------------------
        # 6) ملاحظات (Observations)
        # -------------------------------
        Observation.objects.create(
            patient=patient,
            encounter=encounter,
            code=ObservationDictionary.objects.get(code="8480-6"),
            value="120",
            unit="mmHg",
            observed_at=now(),
        )
        Observation.objects.create(
            patient=patient,
            encounter=encounter,
            code=ObservationDictionary.objects.get(code="2345-7"),
            value="95",
            unit="mg/dL",
            observed_at=now(),
        )

        # -------------------------------
        # 7) أدوية (Medications)
        # -------------------------------
        Medication.objects.create(
            patient=patient,
            encounter=encounter,
            code=MedicationDictionary.objects.get(code="1049630"),
            local_name="Panadol",
            dose="500mg",
            frequency="Twice a day",
            start_date=now().date(),
            end_date=(now() + timedelta(days=5)).date(),
            status="ACTIVE",
        )

        # -------------------------------
        # 8) حالة مرضية (Condition)
        # -------------------------------
        Condition.objects.create(
            patient=patient,
            code=ConditionDictionary.objects.get(code="J10"),
            status="Active",
            onset_date="2025-09-10",
        )

        # -------------------------------
        # 9) حساسية (Allergy)
        # -------------------------------
        Allergy.objects.create(
            patient=patient,
            substance="Penicillin",
            reaction="Skin rash",
            severity="Moderate",
        )

        # -------------------------------
        # 10) موافقة (Consent)
        # -------------------------------
        Consent.objects.create(
            patient=patient,
            status="GRANTED",
            valid_from="2025-09-01",
            valid_to="2026-09-01",
            purpose="Research and treatment",
        )

        self.stdout.write(self.style.SUCCESS("✅ تم إدخال البيانات بنجاح!"))
