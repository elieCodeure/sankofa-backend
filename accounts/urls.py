from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    UserProfileView, 
    SankhofaTokenObtainPairView, 
    ChangePasswordView,
    ActivateAccountView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    GoogleLoginView,
    GoogleRegisterView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate_account'),
    path('login/', SankhofaTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('current-user/', UserProfileView.as_view(), name='current_user'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Réinitialisation de mot de passe (Password Reset)
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('google-register/', GoogleRegisterView.as_view(), name='google_register'),
]