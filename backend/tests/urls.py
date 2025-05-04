from django.urls import path
from tests import views


urlpatterns = [
    path('tests', views.TestsPage, name='tests'),
    path('test/<int:pk>', views.TestsDetail, name='tests-detail'),
    path('test/<int:pk>/pass', views.Quiz, name='quiz'),
    path('test/<int:pk>/result', views.QuizResultPage, name='quiz-result'),
]
