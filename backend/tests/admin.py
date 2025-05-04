from django.contrib import admin
from .models import Tests, QuizQuestion, QuizOption, QuizResult, QuizResultText


admin.site.register(Tests)
admin.site.register(QuizQuestion)
admin.site.register(QuizOption)
admin.site.register(QuizResult)
admin.site.register(QuizResultText)
