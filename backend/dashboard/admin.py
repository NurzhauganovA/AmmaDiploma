from django.contrib import admin

from dashboard.models import QuestionnaireQuestion, QuestionnaireAnswer, QuestionnaireRecommendation, \
    QuestionnaireResult, Vitamin, Workout, WorkoutCategory, WorkoutDifficulty, NutrientProgress, NutritionBenefit, \
    NutritionTracker, NutritionContent, NutritionContentType, DailyRecommendation, NutrientCategory

admin.site.register(QuestionnaireQuestion)
admin.site.register(QuestionnaireAnswer)
admin.site.register(QuestionnaireRecommendation)
admin.site.register(QuestionnaireResult)

admin.site.register(Vitamin)

admin.site.register(Workout)
admin.site.register(WorkoutCategory)
admin.site.register(WorkoutDifficulty)


class NutritionBenefitInline(admin.TabularInline):
    model = NutritionContent.benefits.through
    extra = 1


class NutrientProgressInline(admin.TabularInline):
    model = NutrientProgress
    extra = 1


@admin.register(NutrientCategory)
class NutrientCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code')
    search_fields = ('name',)


@admin.register(DailyRecommendation)
class DailyRecommendationAdmin(admin.ModelAdmin):
    list_display = ('nutrient', 'target_amount', 'unit', 'trimester', 'color_code')
    list_filter = ('trimester',)
    search_fields = ('nutrient',)


@admin.register(NutritionContentType)
class NutritionContentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(NutritionContent)
class NutritionContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'trimester', 'created_at')
    list_filter = ('content_type', 'trimester')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('benefits',)
    inlines = [NutritionBenefitInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'content_type', 'image', 'trimester', 'description', 'color_code')
        }),
        ('Recipe Details', {
            'fields': ('prep_time', 'cook_time', 'difficulty', 'recipe_steps'),
            'classes': ('collapse',),
            'description': 'Fill these fields only if content type is Recipe'
        }),
        ('Meal Plan Details', {
            'fields': ('days', 'focus'),
            'classes': ('collapse',),
            'description': 'Fill these fields only if content type is Meal Plan'
        }),
        ('Information Details', {
            'fields': ('read_time',),
            'classes': ('collapse',),
            'description': 'Fill these fields only if content type is Nutrition Facts or Supplements'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(NutritionBenefit)
class NutritionBenefitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(NutritionTracker)
class NutritionTrackerAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    list_filter = ('date',)
    search_fields = ('user__username',)
    inlines = [NutrientProgressInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(NutrientProgress)
class NutrientProgressAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'nutrient', 'current_amount', 'progress_percentage')
    list_filter = ('tracker__date',)
    search_fields = ('tracker__user__username', 'nutrient__nutrient')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tracker__user=request.user)