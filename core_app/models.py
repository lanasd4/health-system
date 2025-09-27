from django.db import models 
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


# =====================================================================
# Patient & Identifiers
# =====================================================================

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    blood_type = models.CharField(
        max_length=3, null=True, blank=True,
        choices=[
            ("A+", "A+"), ("A-", "A-"),
            ("B+", "B+"), ("B-", "B-"),
            ("AB+", "AB+"), ("AB-", "AB-"),
            ("O+", "O+"), ("O-", "O-"),
        ]
    )

    def __str__(self):
        return self.name


class PatientIdentifier(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="identifiers")
    type = models.CharField(max_length=30)   # NID, MRN, PASSPORT
    value = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type}: {self.value}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["patient", "type", "value"], name="uq_pid_type_value")
        ]

# =====================================================================
# Reference Dictionaries (ICD / LOINC / RxNorm)
# =====================================================================

class ConditionDictionary(models.Model):
    code = models.CharField(max_length=20, unique=True)   # ICD code
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"


class ObservationDictionary(models.Model):
    code = models.CharField(max_length=50, unique=True)   # LOINC code
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"


class MedicationDictionary(models.Model):
    code = models.CharField(max_length=50, unique=True)   # RxNorm code
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.name}"

# =====================================================================
# Medical Records
# =====================================================================

class Condition(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="conditions")
    code = models.ForeignKey(ConditionDictionary, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=50, null=True, blank=True)  # Active, Resolved, etc.
    onset_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient.name} - {self.code}"


class Allergy(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="allergies")
    substance = models.CharField(max_length=200)
    reaction = models.CharField(max_length=200, null=True, blank=True)
    severity = models.CharField(max_length=50, null=True, blank=True)  # Mild, Moderate, Severe
    recorded_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.substance} ({self.severity})"


class Encounter(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="encounters")
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    type = models.CharField(
        max_length=50, null=True, blank=True,
        choices=[("OUTPATIENT", "Outpatient"), ("INPATIENT", "Inpatient"), ("ER", "Emergency")]
    )
    reason = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Encounter {self.id} - {self.patient.name} ({self.type})"


class Observation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="observations")
    encounter = models.ForeignKey('Encounter', on_delete=models.SET_NULL, null=True, blank=True, related_name="observations")
    code = models.ForeignKey(ObservationDictionary, on_delete=models.SET_NULL, null=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=30, null=True, blank=True)
    observed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.encounter and self.encounter.patient_id != self.patient_id:
            raise ValidationError("المريض في الـ Observation يجب أن يطابق مريض الـ Encounter.")

    def __str__(self):
        return f"{self.patient.name} - {self.code}"


class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medications")
    encounter = models.ForeignKey('Encounter', on_delete=models.SET_NULL, null=True, blank=True, related_name="medications")
    code = models.ForeignKey(MedicationDictionary, on_delete=models.SET_NULL, null=True)
    local_name = models.CharField(max_length=200, null=True, blank=True)  # اسم شائع محلي (اختياري)
    dose = models.CharField(max_length=100, null=True, blank=True)
    frequency = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50, null=True, blank=True,
        choices=[("ACTIVE", "Active"), ("STOPPED", "Stopped"), ("COMPLETED", "Completed")]
    )

    def clean(self):
        if self.encounter and self.encounter.patient_id != self.patient_id:
            raise ValidationError("المريض في الدواء يجب أن يطابق مريض الـ Encounter.")

    def __str__(self):
        return f"{self.patient.name} - {self.code}"

# =====================================================================
# Documents & Other
# =====================================================================

class DocumentRef(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="documents")
    encounter = models.ForeignKey('Encounter', on_delete=models.SET_NULL, null=True, blank=True, related_name="documents")
    doc_type = models.CharField(max_length=50, null=True, blank=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.encounter and self.encounter.patient_id != self.patient_id:
            raise ValidationError("المريض في الملف يجب أن يطابق مريض الـ Encounter.")

    def __str__(self):
        return self.title


class Immunization(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="immunizations")
    vaccine_name = models.CharField(max_length=200)
    administered_at = models.DateField()
    lot_number = models.CharField(max_length=100, null=True, blank=True)
    performer = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.vaccine_name} - {self.administered_at}"


class Consent(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="consents")
    status = models.CharField(
        max_length=20,
        choices=[("GRANTED", "Granted"), ("REVOKED", "Revoked")],
        default="GRANTED"
    )
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    purpose = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Consent ({self.status}) for {self.patient.name}"


class AuditEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey('LoginSession', on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    action = models.CharField(max_length=30)    # READ, CREATE, UPDATE, DELETE
    resource = models.CharField(max_length=50)  # Patient, Observation, Medication...
    resource_id = models.CharField(max_length=64, null=True, blank=True)
    # لو لسا بدك تخزّني IP مباشرة ممكن نتركه، بس صار عندنا بديل عن طريق session
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        u = self.user or "Anon"
        local_time = timezone.localtime(self.created_at) if self.created_at else None
        return f"{u} - {self.action} {self.resource} ({local_time:%Y-%m-%d %H:%M})"


class LoginSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="login_sessions")
    session_key = models.CharField(max_length=64, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # اختياري: لو صارت محاولة فاشلة فينا نخزّنها
    username_attempt = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        who = self.user.username if self.user_id else (self.username_attempt or "Unknown")
        local_time = timezone.localtime(self.login_at) if self.login_at else None
        return f"{who} [{self.session_key}] @ {local_time:%Y-%m-%d %H:%M}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("NO_SHOW", "No show"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    practitioner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments"
    )
    start_at = models.DateTimeField()                 # وقت بداية الموعد
    end_at = models.DateTimeField()                   # وقت نهاية الموعد
    reason = models.CharField(max_length=255, blank=True, null=True)  # سبب الزيارة
    location = models.CharField(max_length=120, blank=True, null=True)  # عيادة/غرفة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")
    encounter = models.ForeignKey(                    # اختياري: نربطه بزيارة بعد ما تتم
        Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # تحقّق بسيط: البداية قبل النهاية
        if self.end_at <= self.start_at:
            raise ValidationError("وقت نهاية الموعد يجب أن يكون بعد وقت بدايته.")
        # (اختياري لاحقًا) نضيف فحص تعارض المواعيد لنفس الـ practitioner

    def __str__(self):
        who = self.patient.name if self.patient_id else "Unknown"
        return f"Appt {who} @ {self.start_at} ({self.status})"


# null=True → على مستوى قاعدة البيانات:
#الحقل بيسمح يكون قيمته NULL في الجدول.
#مفيدة خصوصًا مع حقول تاريخ/وقت/أرقام.
#مثال شائع: DateTimeField(null=True).
#blank=True → على مستوى التحقّق (Validation) في الفورم/الـ Serializer:
#بيسمح تتركي الحقل فاضي وقت الإدخال (ما يطلّع خطأ “هذا الحقل مطلوب”).
#حتى لو ما عندك فورم HTML، DRF serializers تعتبره كمان.
#مثال شائع: CharField(blank=True)، يعني مو مطلوب إدخال قيمة.
#self = الكائن الحالي (Current instance).
#أي دالة (method) داخل الكلاس لازم أول باراميتر يكون self.
#يعني: لما تنشئي كائن من الكلاس وتستدعي دالة، self هو المرجع لهالكائن.
