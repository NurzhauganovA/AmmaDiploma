from django.shortcuts import render
from dashboard.models import QuestionnaireRecommendation


def recommendation_list(request):
    recommendations = QuestionnaireRecommendation.objects.all()

    context = {
       'recommendations': recommendations,
    }

    return render(request, 'recommendation/recommendation_list.html', context)


def recommendation_detail(request, pk):
    recommendation = QuestionnaireRecommendation.objects.get(pk=pk)

    context = {
       'recommendation': recommendation,
    }

    return render(request, 'recommendation/recommendation_detail.html', context)