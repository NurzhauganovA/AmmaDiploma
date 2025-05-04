from django.urls import path
from . import views


urlpatterns = [
    path('', views.recommendation_list, name='recommendation_list'),
    path('<int:pk>', views.recommendation_detail, name='recommendation_detail'),
]
