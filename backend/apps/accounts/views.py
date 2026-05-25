from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from apps.accounts.models import ScreenDefinition
from apps.accounts.serializers import LoginSerializer, ScreenDefinitionSerializer, UserSerializer
from apps.accounts.screens import get_available_screens


class IsStaffUser(permissions.BasePermission):
    # 사용자 생성/수정은 화면 권한 자체를 바꿀 수 있는 기능이므로 staff에게만 허용합니다.
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class LoginView(APIView):
    # 로그인 전에는 토큰이 없으므로 전역 TokenAuthentication/IsAuthenticated를 우회합니다.
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        # 같은 사용자는 하나의 토큰을 재사용합니다. 로그아웃 시 해당 토큰을 삭제합니다.
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,
            }
        )


class MeView(APIView):
    # 프론트가 새로고침 후 저장된 토큰으로 현재 사용자와 화면 권한을 복구할 때 사용합니다.
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    def post(self, request):
        # DRF token은 stateless 세션처럼 쓰이므로, 로그아웃은 서버 토큰 삭제로 처리합니다.
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListView(generics.ListCreateAPIView):
    # 사용자 목록과 생성은 staff 전용입니다. 일반 사용자는 자신에게 허용된 화면만 볼 수 있습니다.
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    permission_classes = [IsStaffUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    # 사용자별 화면 권한을 변경할 수 있으므로 상세/수정/삭제도 staff 전용입니다.
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    permission_classes = [IsStaffUser]


class ScreenListView(generics.ListCreateAPIView):
    # 사용자 권한 모달과 화면 관리 페이지가 같은 목록을 사용하도록 DB 기준으로 제공합니다.
    queryset = ScreenDefinition.objects.all()
    serializer_class = ScreenDefinitionSerializer
    permission_classes = [IsStaffUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data or get_available_screens(include_inactive=True))


class ScreenDetailView(generics.RetrieveUpdateDestroyAPIView):
    # 화면 id를 수정/삭제하면 기존 사용자 권한의 문자열 값은 자동 변경되지 않습니다.
    # 운영에서는 label/description 중심으로 수정하고, id 변경은 신중하게 다루는 전제입니다.
    queryset = ScreenDefinition.objects.all()
    serializer_class = ScreenDefinitionSerializer
    permission_classes = [IsStaffUser]
