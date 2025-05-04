import json

from django.core.mail import EmailMessage
from django.shortcuts import render

from dashboard.models import QuestionnaireQuestion, QuestionnaireResult


def base_questionnaire(request):
    questions = QuestionnaireQuestion.objects.filter(is_active=True).prefetch_related('questionnaireanswer_set')

    questionnaire_data = []

    for question in questions:
        answers = question.questionnaireanswer_set.all()

        questionnaire_data.append({
            'id': question.id,
            'title': question.text,
            'answers': [
                {
                    'id': answer.id,
                    'title': answer.text
                } for answer in answers
            ]
        })

    context = {
        'questionnaires': questionnaire_data
    }

    return render(request, 'questionnaire/base_questionnaire.html', context)


def get_my_plan(request):
    data = json.loads(request.body)
    email = data.get('email')
    result = data.get('result')

    result_text = ""
    for i in result:
        result_text += f"""
            {i['questionTitle']}: {i['answerTitle']}
        """

    EmailMessage(
        subject=f'Your personal pregnancy plan',
        body=f'Your answers: {result_text}',
        from_email='womenssdiary@gmail.com',
        to=[email]
    ).send()

    QuestionnaireResult.objects.filter(user=request.user).delete()

    questionnaire_result = QuestionnaireResult.objects.create(
        user=request.user
    )
    questionnaire_result.answers.set([answer['answerId'] for answer in result])
    questionnaire_result.save()

    return render(request, 'questionnaire/base_questionnaire.html')