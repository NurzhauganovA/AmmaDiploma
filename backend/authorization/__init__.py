from django.db import models


class UserRoles(models.TextChoices):
    EMPLOYEE = "Employee", "Сотрудник"
    PARENT = "Parent", "Родитель"
    STUDENT = "Student", "Ученик"
    TEACHER = "Teacher", "Учитель"
