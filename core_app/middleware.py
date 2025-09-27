import threading
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from .models import LoginSession

# مكان نخزن فيه بيانات خاصة بكل طلب (request) بشكل منفصل
_thread_local = threading.local()

# دوال مساعدة للوصول للبيانات المخزنة
def get_current_user():
    return getattr(_thread_local, "user", None)

def get_current_ip():
    return getattr(_thread_local, "ip", None)

def get_current_session_key():
    return getattr(_thread_local, "session_key", None)


class ThreadLocalMiddleware(MiddlewareMixin):
    """
    Middleware يشتغل مع كل طلب HTTP.
    وظيفته يخزن:
    - المستخدم الحالي (request.user)
    - عنوان الـ IP
    - session_key للجلسة
    بمكان (ThreadLocal) بحيث أي كود تاني (signals مثلاً) يقدر يوصل لهاي القيم.
    """

    def process_request(self, request):
        # خزّن المستخدم الحالي
        _thread_local.user = getattr(request, "user", None)

        # استخرج الـ IP من الهيدر (يدعم سيرفر خلفي + بديل REMOTE_ADDR)
        """
        منستخرج الـ IP:
        إذا في Proxy (مثل Nginx) وبيبعث الهيدر HTTP_X_FORWARDED_FOR، 
        مناخد أول IP (الـ client الأصلي عادةً).
        إذا ما في، منرجع لـ REMOTE_ADDR (الطريقة التقليدية).
        منخزّن النتيجة في _thread_local.ip.
        """
        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR")
        )
        _thread_local.ip = ip

        # تأكدي أن الجلسة لها مفتاح (إذا ما عندها، نعمل save لتوليد مفتاح)
        if not request.session.session_key:
            request.session.save()

        # خزّن session_key
        _thread_local.session_key = request.session.session_key

    def process_response(self, request, response):
        # ننضّف بعد ما نخلص الرد
        for attr in ("user", "ip", "session_key"):
            if hasattr(_thread_local, attr):
                setattr(_thread_local, attr, None)
        return response


class EnsureLoginSessionMiddleware:
    """
    يضمن وجود LoginSession للمستخدم يلي داخل عبر JWT.
    - إذا المستخدم مصادق (is_authenticated) وما عنده LoginSession نشط، ينشئ واحد جديد.
    - إذا عنده LoginSession موجود لكنه مو Active، يفعّله.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated and not user.is_anonymous:
            # توليد session_key إذا ما في
            sk = request.session.session_key
            if not sk:
                request.session.save()
                sk = request.session.session_key

            # نحاول نجيب LoginSession إذا موجود، إذا مو موجود ننشئه
            session_obj, created = LoginSession.objects.get_or_create(
                user=user,
                session_key=sk,
                defaults={
                    "ip_address": request.META.get("REMOTE_ADDR"),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "is_active": True,
                    "login_at": now(),
                }
            )

            # إذا لقينا Session بس مو Active → نفعّله
            if not created and not session_obj.is_active:
                session_obj.is_active = True
                session_obj.save(update_fields=["is_active"])

        return self.get_response(request)
