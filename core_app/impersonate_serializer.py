from rest_framework import serializers
from django.contrib.auth.models import User

class ImpersonateSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("المستخدم غير موجود")
        return value
