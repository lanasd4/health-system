from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from .impersonate_serializer import ImpersonateSerializer
from .permissions import in_groups

class ImpersonateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ImpersonateSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']

            try:
                target_user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "المستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)

            # فقط الأدوار المسموحة: Admin, Doctor, Nurse
            if not in_groups(request.user, ["Admin", "Doctor", "Nurse"]):
                return Response({"error": "لا تملك صلاحية الانتحال"}, status=status.HTTP_403_FORBIDDEN)

            # إنشاء توكن جديد للمستخدم المستهدف
            refresh = RefreshToken.for_user(target_user)
            return Response({
                "message": f"تم الدخول كـ {target_user.username}",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
