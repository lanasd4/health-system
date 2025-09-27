from rest_framework.permissions import BasePermission, SAFE_METHODS

def in_groups(user, group_names):
    return user.is_authenticated and user.groups.filter(name__in=group_names).exists()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return in_groups(request.user, ["Admin"])

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return in_groups(request.user, ["Doctor"])

class IsNurse(BasePermission):
    def has_permission(self, request, view):
        return in_groups(request.user, ["Nurse"])

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return in_groups(request.user, ["Patient"])

class WriteByAdminDoctorNurse(BasePermission):
    """
    القراءة لأي مستخدم مُسجّل دخول.
    أما الكتابة (POST/PUT/PATCH/DELETE) فمسموحة فقط لـ Admin/Doctor/Nurse.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return in_groups(request.user, ["Admin", "Doctor", "Nurse"])

class CanCreatePatient(BasePermission):
    """
    إنشاء مريض جديد مسموح لـ Admin/Doctor/Nurse فقط.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            return in_groups(request.user, ["Admin", "Doctor", "Nurse"])
        return True
