from django.urls import path
from . import views


urlpatterns = [
    path('', views.pregnancy, name='pregnancy'),
    path('week-by-week', views.week_by_week, name='week_by_week'),
    path('week-by-week/<int:week_number>', views.week_by_week_detail, name='week_by_week_detail'),

    path('due-date-calculator', views.due_date_calculator, name='due_date_calculator'),
    path('weight-gain-calculator', views.weight_gain_calculator, name='weight_gain_calculator'),
]
