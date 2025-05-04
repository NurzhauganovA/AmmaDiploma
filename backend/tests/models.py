from django.db import models

from authorization.models import User


class Tests(models.Model):
    image = models.ImageField(upload_to='images/tests/')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Tests'
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'


class QuizQuestion(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    text = models.TextField()
    is_reversed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'QuizQuestion'
        verbose_name = 'Quiz Question'
        verbose_name_plural = 'Quiz Questions'


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    text = models.TextField()
    score = models.IntegerField()

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'QuizOption'
        verbose_name = 'Quiz Option'
        verbose_name_plural = 'Quiz Options'


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'User: {self.user} <---> Score: {self.score}'

    class Meta:
        db_table = 'QuizResult'
        verbose_name = 'Quiz Result'
        verbose_name_plural = 'Quiz Results'


class QuizResultText(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    text = models.TextField()
    score_min = models.IntegerField()
    score_max = models.IntegerField()

    def __str__(self):
        return f'Test: {self.test} <---> Score Range: {self.score_min} - {self.score_max}'

    class Meta:
        db_table = 'QuizResultText'
        verbose_name = 'Quiz Result Text'
        verbose_name_plural = 'Quiz Result Texts'
