from UserApp.views import index
from django.urls import path
from UserApp.views import RegisterView, LoginView


urlpatterns = [
    path('', index, name='user-index'),
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    
]