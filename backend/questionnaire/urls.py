from django.urls import path

from .views import base_questionnaire, get_my_plan


urlpatterns = [
    path('', base_questionnaire, name='base_questionnaire'),
    path('get_my_plan/', get_my_plan, name='get_my_plan'),
]