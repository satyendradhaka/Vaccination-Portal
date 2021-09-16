from django.urls import path
from .views import send_email
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.list, name='get_list'),
    path('send_mail/', send_email, name="send_mail"),
    path('return_csv',views.return_csv),
]
