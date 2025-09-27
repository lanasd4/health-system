from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core_app.views import (  
    PatientViewSet,
    AppointmentViewSet,
    EncounterViewSet,
    ObservationViewSet,
    MedicationViewSet,
    DocumentRefViewSet,
    ConditionViewSet,
    ConsentViewSet,
    ConditionDictionaryViewSet,      
    ObservationDictionaryViewSet, 
    MedicationDictionaryViewSet,
    AllergyViewSet,
)
from core_app.impersonate_view import ImpersonateView


# 📌 Router
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'appointments', AppointmentViewSet, basename='appointments')
router.register(r'encounters', EncounterViewSet, basename='encounters')
router.register(r'observations', ObservationViewSet, basename='observations')
router.register(r'medications', MedicationViewSet, basename='medications')
router.register(r'documents', DocumentRefViewSet, basename='documents')
router.register(r'conditions', ConditionViewSet, basename='conditions')
router.register(r'consents', ConsentViewSet, basename='consents')
router.register(r'dictionaries/conditions', ConditionDictionaryViewSet, basename='dict-conditions')
router.register(r'dictionaries/observations', ObservationDictionaryViewSet, basename='dict-observations')
router.register(r'dictionaries/medications', MedicationDictionaryViewSet, basename='dict-medications')
router.register(r'allergies', AllergyViewSet, basename='allergies')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # 🔑 JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 👤 Impersonate (انتحال المستخدم)
    path("api/impersonate/", ImpersonateView.as_view(), name="impersonate"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
