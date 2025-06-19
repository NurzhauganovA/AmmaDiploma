from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('delete_pregnancy_progress', views.delete_pregnancy_progress, name='delete_pregnancy_progress'),
    path('api/calendar-events', views.calendar_events, name='calendar_events'),
    path('api/pregnancy-week-now', views.pregnancy_week_now, name='pregnancy_week_now'),
    path('api/pregnancy-week-create', views.pregnancy_week_create, name='pregnancy_week_create'),

    path('vitamins/', views.vitamin_list, name='vitamin_list'),
    path('vitamins/<int:pk>/', views.vitamin_detail, name='vitamin_detail'),
    path('api/vitamins/<int:vitamin_id>/related/', views.vitamin_related_api, name='vitamin_related_api'),

    path('workouts/', views.workout_list, name='workout_list'),
    path('workouts/category/<slug:category_slug>/', views.workout_list, name='workout_list_by_category'),
    path('workouts/trimester/<int:trimester>/', views.workout_list, name='workout_list_by_trimester'),
    path('workouts/<slug:slug>/', views.workout_detail, name='workout_detail'),

    path('api/seed-nutrition-data/', views.seed_nutrition_data, name='seed_nutrition_data'),

    path('nutritions', views.nutrition_home, name='nutrition_list'),
    path('nutritions/<int:content_id>/', views.nutrition_detail, name='nutrition_detail'),
    path('nutrition_filter/', views.filter_content, name='nutrition_filter'),
    path('nutrition_update_progress/', views.update_nutrient_progress, name='nutrition_update_progress'),

    path('api/chatbot/', views.ChatBotView.as_view(), name='chatbot')
]
