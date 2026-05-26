from django.urls import path
from .views import SignupView, LoginView, CheckIdentifierView

urlpatterns = [
    path('signup/',            SignupView.as_view(),           name='signup'),
    path('login/',             LoginView.as_view(),            name='login'),
    path('check-identifier/',  CheckIdentifierView.as_view(), name='check-identifier'),
]
