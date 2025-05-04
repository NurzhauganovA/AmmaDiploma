from django.contrib import admin
from .models import PregnancyWeek, WeekContent, UserWeekProgress, PregnancyWeekNow


admin.site.register(PregnancyWeek)
admin.site.register(WeekContent)
admin.site.register(UserWeekProgress)
admin.site.register(PregnancyWeekNow)