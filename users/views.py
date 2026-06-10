from django.core.exceptions import PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from users.models import User
from users.paginators import UsersPaginator
from users.permissions import IsUserActive, IsUserOwner
from users.serializer import ProfileSerializer, ProfileUserSerializer, CreateProfileSerializer, \
    ProfileViewingSerializer, ProfileUpdateUserSerializer


class ProfilesListAPIView(generics.ListAPIView):
    """Класс представления вида Generic для эндпоинта списка пользователей."""

    serializer_class = ProfileViewingSerializer
    queryset = User.objects.all()
    pagination_class = UsersPaginator
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return ProfileSerializer
        return ProfileViewingSerializer


class ProfileViewingAPIView(generics.RetrieveAPIView):
    """Класс представления вида Generic для эндпоинта просмотра профиля пользователя."""

    serializer_class = ProfileViewingSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.method == "GET" and self.get_object() != self.request.user:
            return ProfileViewingSerializer
        if self.request.user.is_staff:
            return ProfileSerializer
        return ProfileUserSerializer


class ProfileCreateAPIView(generics.CreateAPIView):
    """Класс представления вида Generic для эндпоинта создания пользователя."""

    serializer_class = CreateProfileSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.user.is_staff or self.request.user.is_superuser:
            return ProfileSerializer
        return CreateProfileSerializer

    def perform_create(self, serializer):
        """Метод вносит изменение в сериализатор создания "Пользователя"."""

        if not self.request.user.is_staff or not self.request.user.is_superuser:
            try:
                if serializer.validated_data['is_staff'] or serializer.validated_data['is_superuser']:
                    raise PermissionDenied('Создавать пользователей с административными правами могут только '
                                           'администраторы.')
                else:
                    user = serializer.save()
                    user.set_password(user.password)
                    user.is_active = True
                    user.save()
            except KeyError:
                user = serializer.save()
                user.set_password(user.password)
                user.is_active = True
                user.save()
        else:
            user = serializer.save()
            user.set_password(user.password)
            user.is_active = True
            user.save()


class ProfileUpdateAPIView(generics.UpdateAPIView):
    """Класс представления вида Generic для эндпоинта редактирования профиля пользователя."""

    serializer_class = ProfileUserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive, IsUserOwner | IsAdminUser]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.method == "PATCH":
            return ProfileUpdateUserSerializer
        if self.request.user.is_staff or self.request.user.is_superuser:
            return ProfileSerializer
        return ProfileUserSerializer


class ProfileDestroyAPIView(generics.DestroyAPIView):
    """Класс представления вида Generic для эндпоинта удаления профиля пользователя."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive, IsAdminUser]
