from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render
from .models import PregnancyWeek, WeekContent, UserWeekProgress, PregnancyWeekNow


def pregnancy(request):
    return render(request, 'pregnancy/pregnancy.html')


def week_by_week(request):
    first_trimester_pregnancy = PregnancyWeek.objects.filter(week_number__lte=13)
    second_trimester_pregnancy = PregnancyWeek.objects.filter(week_number__gte=14, week_number__lte=27)
    third_trimester_pregnancy = PregnancyWeek.objects.filter(week_number__gte=28)

    context = {
        'first_trimester_pregnancy': first_trimester_pregnancy,
        'second_trimester_pregnancy': second_trimester_pregnancy,
        'third_trimester_pregnancy': third_trimester_pregnancy
    }

    return render(request, 'pregnancy/week_by_week.html', context)


def week_by_week_detail(request, week_number):
    week = PregnancyWeek.objects.get(week_number=week_number)
    week_content = WeekContent.objects.filter(week=week).first()
    if not week_content:
        week_content = WeekContent.objects.filter(week__week_number=41).first()
    user = request.user
    user_week_progress = UserWeekProgress.objects.filter(user=user, week=week).first()

    context = {
        'week': week,
        'week_content': week_content,
        'user_week_progress': user_week_progress
    }

    return render(request, f'pregnancy/detail_week.html', context)


def due_date_calculator(request):
    context = {}

    return render(request, 'pregnancy/due_date_calculator.html', context)


def weight_gain_calculator(request):
    context = {}

    return render(request, 'pregnancy/gain_calculator.html', context)