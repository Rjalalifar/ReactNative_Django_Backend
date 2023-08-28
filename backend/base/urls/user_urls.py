from django.urls import path
from base.views import user_views as views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', views.MyCreatorTokenView.as_view(), name='token_obtain_pair'),
    path('profile/', views.getUserProfile, name='users_profile'),
    path('profile/update', views.updateUserProfile, name='users_profile'),
    path('', views.getUsers, name='users'),
    path('register/', views.registerUser, name='register'),
    path('verify/<str:token>/', views.verifyEmail, name='verify-email'),
    path('token/refresh/', TokenRefreshView.as_view, name='token_refresh')

]
