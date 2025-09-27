# core_app/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import (
    Patient, PatientIdentifier, Appointment, Encounter, Observation, Medication, DocumentRef,
    Condition, Consent, Allergy, Immunization,
    AuditEvent, LoginSession
)
from .middleware import get_current_user, get_current_ip, get_current_session_key


# ---------------------------
# Helper: تسجيل حدث AuditEvent
# ---------------------------
def log_audit_event(action, resource, resource_id=None):
    print("🔎 AuditEvent Signal Triggered:", action, resource, resource_id)  # Debug
    """
    يسجل أي عملية (CRUD) بجدول AuditEvent.
    - المستخدم + IP + session_key يُسحبوا من الميدلوير (ThreadLocal).
    - يربط العملية بجلسة الدخول (LoginSession) إذا كانت فعّالة.
    """
    user = get_current_user()
    ip = get_current_ip()
    session_key = get_current_session_key()

    session_obj = None
    if session_key and user and user.is_authenticated:
        session_obj = LoginSession.objects.filter(
            user=user, session_key=session_key, is_active=True
        ).order_by('-login_at').first()

    AuditEvent.objects.create(
        user=user if isinstance(user, User) else None,
        session=session_obj,
        action=action,
        resource=resource,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip if not session_obj else None,  # إذا ما لقى Session خزّن الـ IP
        created_at=now(),
    )


# ---------------------------
# إشارات تسجيل الدخول/الخروج/الفشل
# ---------------------------

@receiver(user_logged_in, dispatch_uid="login_session_create")
def on_user_logged_in(sender, request, user, **kwargs):
    """ينشئ LoginSession جديدة عند تسجيل الدخول"""
    if not request.session.session_key:
        request.session.save()

    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
    ua = request.META.get("HTTP_USER_AGENT", "")

    LoginSession.objects.create(
        user=user,
        session_key=request.session.session_key,
        ip_address=ip,
        user_agent=ua,
        is_active=True,
    )


@receiver(user_logged_out, dispatch_uid="login_session_close")
def on_user_logged_out(sender, request, user, **kwargs):
    """يغلق LoginSession عند تسجيل الخروج"""
    sk = getattr(request.session, "session_key", None)
    if not sk:
        return
    LoginSession.objects.filter(
        session_key=sk, user=user, is_active=True
    ).update(is_active=False, logout_at=now())


@receiver(user_login_failed, dispatch_uid="login_session_failed")
def on_user_login_failed(sender, credentials, request, **kwargs):
    """يسجل محاولة دخول فاشلة"""
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
    ua = request.META.get("HTTP_USER_AGENT", "")
    sk = getattr(request.session, "session_key", None) if hasattr(request, "session") else None
    if not sk and request and hasattr(request, "session"):
        request.session.save()
        sk = request.session.session_key

    LoginSession.objects.create(
        user=None,
        username_attempt=credentials.get("username"),
        session_key=sk or "no-session",
        ip_address=ip,
        user_agent=ua,
        is_active=False,
        logout_at=now(),
    )


# ---------------------------
# إشارات CRUD على الموديلات
# ---------------------------

@receiver(post_save, sender=Patient, dispatch_uid="audit_patient_save")
def log_patient_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Patient", instance.id)

@receiver(post_delete, sender=Patient, dispatch_uid="audit_patient_delete")
def log_patient_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Patient", instance.id)


@receiver(post_save, sender=PatientIdentifier, dispatch_uid="audit_pid_save")
def log_pid_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "PatientIdentifier", instance.id)

@receiver(post_delete, sender=PatientIdentifier, dispatch_uid="audit_pid_delete")
def log_pid_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "PatientIdentifier", instance.id)


@receiver(post_save, sender=Appointment, dispatch_uid="audit_appointment_save")
def log_appointment_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Appointment", instance.id)

@receiver(post_delete, sender=Appointment, dispatch_uid="audit_appointment_delete")
def log_appointment_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Appointment", instance.id)


@receiver(post_save, sender=Encounter, dispatch_uid="audit_encounter_save")
def log_encounter_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Encounter", instance.id)

@receiver(post_delete, sender=Encounter, dispatch_uid="audit_encounter_delete")
def log_encounter_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Encounter", instance.id)


@receiver(post_save, sender=Observation, dispatch_uid="audit_observation_save")
def log_observation_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Observation", instance.id)

@receiver(post_delete, sender=Observation, dispatch_uid="audit_observation_delete")
def log_observation_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Observation", instance.id)


@receiver(post_save, sender=Medication, dispatch_uid="audit_medication_save")
def log_medication_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Medication", instance.id)

@receiver(post_delete, sender=Medication, dispatch_uid="audit_medication_delete")
def log_medication_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Medication", instance.id)


@receiver(post_save, sender=DocumentRef, dispatch_uid="audit_document_save")
def log_document_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "DocumentRef", instance.id)

@receiver(post_delete, sender=DocumentRef, dispatch_uid="audit_document_delete")
def log_document_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "DocumentRef", instance.id)


@receiver(post_save, sender=Condition, dispatch_uid="audit_condition_save")
def log_condition_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Condition", instance.id)

@receiver(post_delete, sender=Condition, dispatch_uid="audit_condition_delete")
def log_condition_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Condition", instance.id)


@receiver(post_save, sender=Consent, dispatch_uid="audit_consent_save")
def log_consent_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Consent", instance.id)

@receiver(post_delete, sender=Consent, dispatch_uid="audit_consent_delete")
def log_consent_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Consent", instance.id)


@receiver(post_save, sender=Allergy, dispatch_uid="audit_allergy_save")
def log_allergy_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Allergy", instance.id)

@receiver(post_delete, sender=Allergy, dispatch_uid="audit_allergy_delete")
def log_allergy_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Allergy", instance.id)


@receiver(post_save, sender=Immunization, dispatch_uid="audit_immunization_save")
def log_immunization_save(sender, instance, created, **kwargs):
    log_audit_event("CREATE" if created else "UPDATE", "Immunization", instance.id)

@receiver(post_delete, sender=Immunization, dispatch_uid="audit_immunization_delete")
def log_immunization_delete(sender, instance, **kwargs):
    log_audit_event("DELETE", "Immunization", instance.id)
