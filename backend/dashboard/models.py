from django.db import models
from django.contrib.postgres.fields import ranges
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from authorization.models import User



class Pregnancy(models.Model):
    """
    Беременность.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='Дата начала')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    class Meta:
        db_table = 'pregnancy'


class PregnancyEvent(models.Model):
    """
    События беременности.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pregnancy_event'


class PregnancyRecommendation(models.Model):
    """
    Рекомендации для беременных.
    """
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pregnancy_recommendation'


class PregnancyNotification(models.Model):
    """
    Напоминания для беременных.
    """
    pregnancy = models.ForeignKey(Pregnancy, on_delete=models.CASCADE)
    event = models.ForeignKey(PregnancyEvent, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(PregnancyRecommendation, on_delete=models.CASCADE)
    frequency_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'pregnancy_notification'


class Test(models.Model):
    """
    Тесты для беременных.
    """
    image = models.ImageField(upload_to='images/tests/')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'test'


class TestResultScore(models.Model):
    """
    Результаты тестов.
    """
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()
    score = ranges.IntegerRangeField()

    class Meta:
        db_table = 'test_result_score'


class Question(models.Model):
    """
    Вопросы для тестов.
    """
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/questions/', null=True, blank=True)
    title = models.CharField(max_length=255)
    text = models.TextField()

    class Meta:
        db_table = 'question'


class Answer(models.Model):
    """
    Ответы для вопросов.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    score = models.IntegerField()

    class Meta:
        db_table = 'answer'


class Result(models.Model):
    """
    Результаты тестирования.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'result'


class Notification(models.Model):
    """
    Уведомления для пользователей.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'


class ChatAI(models.Model):
    """
    Чат с искусственным интеллектом.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    response = models.TextField()
    is_active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_ai'


class ArticleTag(models.Model):
    """
    Теги для статей.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        db_table = 'article_tag'


class Article(models.Model):
    """
    Статьи для беременных.
    """
    tags = models.ManyToManyField(ArticleTag)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='images/articles/')
    title = models.CharField(max_length=255)
    text = models.TextField()
    term_pregnancy = models.IntegerField()
    published_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        db_table = 'article'


class ArticleComment(models.Model):
    """
    Комментарии к статьям.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_comment'


class ArticleLike(models.Model):
    """
    Лайки к статьям.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_like'


class ArticleDislike(models.Model):
    """
    Дизлайки к статьям.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_dislike'


class ArticleFavorite(models.Model):
    """
    Избранное для статей.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_favorite'


class ArticleView(models.Model):
    """
    Просмотры статей.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'article_view'


class QuestionnaireQuestion(models.Model):
    """
        Вопросы для анкеты.
    """
    text = models.TextField()
    image = models.ImageField(upload_to='images/questionnaire/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questionnaire_question'
        verbose_name = _('Questionnaire Question')
        verbose_name_plural = _('Questionnaire Questions')

    def __str__(self):
        return self.text


class QuestionnaireAnswer(models.Model):
    question = models.ForeignKey(QuestionnaireQuestion, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questionnaire_answer'
        verbose_name = _('Questionnaire Answer')
        verbose_name_plural = _('Questionnaire Answers')

    def __str__(self):
        return self.text


class QuestionnaireRecommendation(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    answers = models.ManyToManyField(QuestionnaireAnswer, related_name='recommendations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questionnaire_recommendation'
        verbose_name = _('Questionnaire Recommendation')
        verbose_name_plural = _('Questionnaire Recommendations')

    def __str__(self):
        return self.title


class QuestionnaireResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answers = models.ManyToManyField(QuestionnaireAnswer, related_name='results')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questionnaire_result'
        verbose_name = _('Questionnaire Result')
        verbose_name_plural = _('Questionnaire Results')

    def __str__(self):
        return f"Result for {self.user.mobile_phone} at {self.created_at}"


class Vitamin(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(help_text="What this vitamin does and why it's important")
    recommended_dose = models.CharField(max_length=255, help_text="Recommended daily dose")
    side_effects = models.TextField(help_text="Possible side effects")
    sources = models.TextField(help_text="Natural sources of this vitamin")
    image = models.ImageField(upload_to='images/vitamins/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    trimester_1 = models.BooleanField(default=False, help_text="Is this vitamin recommended for the first trimester?")
    trimester_2 = models.BooleanField(default=False, help_text="Is this vitamin recommended for the second trimester?")
    trimester_3 = models.BooleanField(default=False, help_text="Is this vitamin recommended for the third trimester?")
    critical = models.BooleanField(default=False, help_text="Is this vitamin critical for pregnancy?")

    class Meta:
        db_table = 'vitamin'
        verbose_name = _('Vitamin')
        verbose_name_plural = _('Vitamins')

    def __str__(self):
        return self.name


class WorkoutCategory(models.Model):
    """Категории тренировок (напр. йога, кардио, силовые)"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    icon = models.CharField(max_length=50, verbose_name="Иконка", blank=True,
                            help_text="Название класса иконки (например 'fa-yoga')")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория тренировок"
        verbose_name_plural = "Категории тренировок"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class WorkoutDifficulty(models.Model):
    """Уровни сложности тренировок"""
    name = models.CharField(max_length=50, verbose_name="Название уровня")
    value = models.PositiveSmallIntegerField(verbose_name="Значение (1-5)")

    class Meta:
        verbose_name = "Уровень сложности"
        verbose_name_plural = "Уровни сложности"
        ordering = ['value']

    def __str__(self):
        return f"{self.name} ({self.value})"


class Workout(models.Model):
    """Модель тренировки"""
    TRIMESTER_CHOICES = [
        (1, 'First trimester'),
        (2, 'Second trimester'),
        (3, 'Third trimester'),
        (0, 'All trimesters'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название тренировки")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(verbose_name="Описание")
    duration = models.PositiveIntegerField(verbose_name="Длительность (минуты)")
    category = models.ForeignKey(WorkoutCategory, on_delete=models.CASCADE,
                                 related_name="workouts", verbose_name="Категория")
    difficulty = models.ForeignKey(WorkoutDifficulty, on_delete=models.SET_NULL,
                                   null=True, related_name="workouts", verbose_name="Сложность")
    trimester = models.PositiveSmallIntegerField(choices=TRIMESTER_CHOICES, default=0,
                                                 verbose_name="Триместр")
    image = models.ImageField(upload_to='workouts/', blank=True, null=True, verbose_name="Изображение")
    video_url = models.URLField(blank=True, verbose_name="Ссылка на видео")
    instructions = models.TextField(verbose_name="Инструкции к упражнениям")
    benefits = models.TextField(verbose_name="Польза для беременных", blank=True)
    contraindications = models.TextField(verbose_name="Противопоказания", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Тренировка"
        verbose_name_plural = "Тренировки"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('workout_detail', args=[self.slug])


class NutrientCategory(models.Model):
    name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7, default="#b3a2d1")  # Hex code color

    def __str__(self):
        return self.name


class DailyRecommendation(models.Model):
    TRIMESTER_CHOICES = [
        ('1', 'First Trimester'),
        ('2', 'Second Trimester'),
        ('3', 'Third Trimester'),
        ('all', 'All Trimesters'),
    ]

    CATEGORY = [
        ('vitamins', 'Vitamins'),
        ('minerals', 'Minerals'),
        ('macros', 'Macronutrients'),
        ('hydration', 'Hydration'),
    ]

    nutrient = models.CharField(max_length=100)
    target_amount = models.FloatField()
    unit = models.CharField(max_length=10)  # g, mg, mcg, L, etc.
    trimester = models.CharField(max_length=3, choices=TRIMESTER_CHOICES)
    color_code = models.CharField(max_length=7, default="#b3a2d1")  # Hex code color
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY, default='vitamins')

    def __str__(self):
        return f"{self.nutrient} - {self.trimester} Trimester"


class NutritionContentType(models.Model):
    name = models.CharField(max_length=100)  # Recipe, Meal Plan, Nutrition Facts, Supplements

    def __str__(self):
        return self.name


class NutritionContent(models.Model):
    TRIMESTER_CHOICES = [
        ('1', 'First Trimester'),
        ('2', 'Second Trimester'),
        ('3', 'Third Trimester'),
        ('all', 'All Trimesters'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    content_type = models.ForeignKey(NutritionContentType, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='nutrition_images/')
    trimester = models.CharField(max_length=3, choices=TRIMESTER_CHOICES)
    description = models.TextField()
    color_code = models.CharField(max_length=7, default="#b3a2d1")  # Hex code color

    # Fields for Recipes
    prep_time = models.PositiveIntegerField(null=True, blank=True)  # in minutes
    cook_time = models.PositiveIntegerField(null=True, blank=True)  # in minutes
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, null=True, blank=True)
    recipe_steps = models.TextField(null=True, blank=True)

    # Fields for Meal Plans
    days = models.PositiveIntegerField(null=True, blank=True)
    focus = models.CharField(max_length=100, null=True, blank=True)

    # Fields for Nutrition Facts & Supplements
    read_time = models.PositiveIntegerField(null=True, blank=True)  # in minutes

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class NutritionBenefit(models.Model):
    name = models.CharField(max_length=100)
    content = models.ManyToManyField(NutritionContent, related_name='benefits')

    def __str__(self):
        return self.name


class NutritionTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.mobile_phone}'s nutrition - {self.date}"


class NutrientProgress(models.Model):
    tracker = models.ForeignKey(NutritionTracker, on_delete=models.CASCADE, related_name='progress')
    nutrient = models.ForeignKey(DailyRecommendation, on_delete=models.CASCADE)
    current_amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.nutrient.nutrient} - {self.current_amount}/{self.nutrient.target_amount} {self.nutrient.unit}"

    @property
    def progress_percentage(self):
        return min(100, (self.current_amount / self.nutrient.target_amount) * 100)