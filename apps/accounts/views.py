from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.audit.models import AuditLog
from utils.request_context import get_current_ip

from .serializers import RegisterSerializer, UserSerializer, AdminUserSerializer

User = get_user_model()


class AuditedTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            email = request.data.get('email', '')
            try:
                user = User.objects.get(email=email)
                AuditLog.objects.create(
                    user=user,
                    action='LOGIN',
                    resource='User',
                    resource_id=str(user.id),
                    description=f"Login via JWT email={email}",
                    ip_address=get_current_ip(),
                )
            except Exception:
                pass
        return response


class RegisterView(generics.CreateAPIView):
    """
    Registra un nuevo usuario en el sistema.

    POST /accounts/register/
    Permisos: público (AllowAny).
    Body: { "email": str, "username": str, "password": str }
    Returns: datos del usuario creado con tokens JWT.
    """

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class MeView(APIView):
    """
    Retorna los datos del usuario autenticado actualmente.

    GET /accounts/me/
    Permisos: usuario autenticado.
    Returns: { "id": int, "email": str, "username": str, "role": str }
    """

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class IsAdmin(permissions.BasePermission):
    """
    Permiso personalizado que restringe el acceso a usuarios con role == 'admin'.
    Retorna True solo si el usuario está autenticado y su rol es 'admin'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class AdminUserListView(generics.ListAPIView):
    """
    Lista todos los usuarios registrados en el sistema.

    GET /accounts/users/
    Permisos: solo administradores (IsAdmin).
    Returns: lista de usuarios con email, username, role e is_active.
    """

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Recupera, actualiza o elimina un usuario específico.

    GET    /accounts/users/<id>/  — detalle del usuario.
    PATCH  /accounts/users/<id>/  — actualiza role o is_active.
    DELETE /accounts/users/<id>/  — elimina la cuenta.
    Permisos: solo administradores (IsAdmin).
    """

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
