from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ExecuteCodeView, InstallPackageView, RegisterView, AvailableLanguagesView

urlpatterns = [
    path('execute/', ExecuteCodeView.as_view(), name='execute_code'),
    path('install/', InstallPackageView.as_view(), name='install_package'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register_api'),
    path('languages/', AvailableLanguagesView.as_view(), name='available_languages'),
]