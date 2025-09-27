from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import (
    Patient, Appointment, Encounter, Observation, Medication, DocumentRef,
    Condition, Consent, ConditionDictionary, ObservationDictionary, MedicationDictionary, Allergy,
)
from .serializers import (
    PatientSerializer, AppointmentSerializer, EncounterSerializer,
    ObservationSerializer, MedicationSerializer, DocumentRefSerializer,
    ConditionSerializer, ConsentSerializer,  # ✅ موجود
    ConditionDictionarySerializer, ObservationDictionarySerializer, MedicationDictionarySerializer,
    AllergySerializer,  # ✅ أضفنا AllergySerializer
)
from .permissions import (
    WriteByAdminDoctorNurse, CanCreatePatient, in_groups
)

# -------- Patients --------
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("id")
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, CanCreatePatient, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Admin", "Doctor", "Nurse"]):
            return Patient.objects.all()
        if in_groups(user, ["Patient"]):
            return Patient.objects.filter(user=user)
        return Patient.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        patient = self.get_object()
        if in_groups(user, ["Patient"]) and patient.user == user:
            serializer.save(
                phone=serializer.validated_data.get("phone", patient.phone),
                address=serializer.validated_data.get("address", patient.address),
            )
        else:
            serializer.save()

    def destroy(self, request, *args, **kwargs):
        if not in_groups(request.user, ["Admin"]):
            raise PermissionDenied("حذف المريض مسموح للمشرف فقط.")
        return super().destroy(request, *args, **kwargs)

# -------- Appointments --------
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("-start_at")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Appointment.objects.filter(patient__user=user)
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        if not in_groups(request.user, ["Admin", "Nurse"]):
            raise PermissionDenied("حذف المواعيد مسموح للإدمن أو الممرضة فقط.")
        return super().destroy(request, *args, **kwargs)

# -------- Encounters --------
class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.all().order_by("-start_at")
    serializer_class = EncounterSerializer
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Encounter.objects.filter(patient__user=user)
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        if not in_groups(request.user, ["Admin"]):
            raise PermissionDenied("حذف الزيارة مسموح للمشرف فقط.")
        return super().destroy(request, *args, **kwargs)

# -------- Observations --------
class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.all().order_by("-observed_at")
    serializer_class = ObservationSerializer
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Observation.objects.filter(patient__user=user)
        return super().get_queryset()

# -------- Medications --------
class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by("-start_date")
    serializer_class = MedicationSerializer   # ✅ يستعمل النسخة المعدلة
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Medication.objects.filter(patient__user=user)
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        if not in_groups(request.user, ["Admin", "Doctor"]):
            raise PermissionDenied("حذف الأدوية مسموح للإدمن أو الطبيب فقط.")
        return super().destroy(request, *args, **kwargs)

# -------- Documents --------
class DocumentRefViewSet(viewsets.ModelViewSet):
    queryset = DocumentRef.objects.all().order_by("-uploaded_at")
    serializer_class = DocumentRefSerializer
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return DocumentRef.objects.filter(patient__user=user)
        return super().get_queryset()

# -------- Conditions --------
class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all().order_by("-onset_date")
    serializer_class = ConditionSerializer   # ✅ يستعمل النسخة المعدلة
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Condition.objects.filter(patient__user=user)
        return super().get_queryset()

# -------- Consents --------
class ConsentViewSet(viewsets.ModelViewSet):
    queryset = Consent.objects.all().order_by("-valid_from")
    serializer_class = ConsentSerializer
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Consent.objects.filter(patient__user=user)
        return super().get_queryset()

# -------- Allergies --------
class AllergyViewSet(viewsets.ModelViewSet):
    queryset = Allergy.objects.all().order_by("-recorded_date")
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, WriteByAdminDoctorNurse]

    def get_queryset(self):
        user = self.request.user
        if in_groups(user, ["Patient"]):
            return Allergy.objects.filter(patient__user=user)
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        # بس Admin يقدر يحذف الحساسية
        if not in_groups(request.user, ["Admin"]):
            raise PermissionDenied("حذف الحساسية مسموح للإدمن فقط.")
        return super().destroy(request, *args, **kwargs)

# -------- Dictionaries --------
class BaseDictionaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet للـ Dictionaries مع بحث وترتيب وصفحات.
    ?search= و ?ordering=
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name"]
    ordering = ["code"]  # افتراضي

class ConditionDictionaryViewSet(BaseDictionaryViewSet):
    queryset = ConditionDictionary.objects.all().order_by("code")
    serializer_class = ConditionDictionarySerializer

class ObservationDictionaryViewSet(BaseDictionaryViewSet):
    queryset = ObservationDictionary.objects.all().order_by("code")
    serializer_class = ObservationDictionarySerializer

class MedicationDictionaryViewSet(BaseDictionaryViewSet):
    queryset = MedicationDictionary.objects.all().order_by("code")
    serializer_class = MedicationDictionarySerializer
