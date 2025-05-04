from django.db import models

from authorization.models import User


class PregnancyWeek(models.Model):
    week_number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='weeks_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"

    class Meta:
        ordering = ['week_number']
        verbose_name = 'Pregnancy Week'
        verbose_name_plural = 'Pregnancy Weeks'
        db_table = 'pregnancy_weeks'


class WeekContent(models.Model):
    """
    Дополнительный контент для каждой недели.
    """
    week = models.ForeignKey(PregnancyWeek, related_name='content', on_delete=models.CASCADE)
    week_image = models.ImageField(upload_to='week_images/', null=True, blank=True)
    highlights_this_week_text = models.TextField(null=True, blank=True)
    baby_development_text = models.TextField(null=True, blank=True)
    baby_development_image = models.ImageField(upload_to='baby_development_images/', null=True, blank=True)
    pregnancy_symptoms_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Content for Week {self.week.week_number}"


class UserWeekProgress(models.Model):
    """
    Модель для отслеживания прогресса пользователя по неделям.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем
    week = models.ForeignKey(PregnancyWeek, on_delete=models.CASCADE)  # Связь с неделей
    completed = models.BooleanField(default=False)  # Статус выполнения недели
    date_completed = models.DateTimeField(null=True, blank=True)  # Дата, когда пользователь завершил просмотр этой недели

    class Meta:
        unique_together = ['user', 'week']

    def __str__(self):
        return f"{self.user.full_name} - Week {self.week.week_number} - Completed: {self.completed}"


class PregnancyWeekNow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User: {self.user.full_name} - Week: {self.start_date}"

    class Meta:
        verbose_name = 'Pregnancy Week Now'
        verbose_name_plural = 'Pregnancy Weeks Now'
        db_table = 'pregnancy_week_now'
