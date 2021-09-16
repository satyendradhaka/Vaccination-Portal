from django.urls import path, include
from . import views 
urlpatterns = [
	path('registration/relatives/', views.add_relative, name='relatives'),
	path('registration/', views.register,name="register"),
	path('', views.home, name="loginPage")
]