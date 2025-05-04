import json
from datetime import timedelta
from sqlite3 import Date

from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.template.context_processors import request
from django.utils import timezone

from authorization.models import User, UserInfo
from authorization.utils import send_email, verify_account
from blog.models import Blog
from dashboard.models import QuestionnaireResult
from pregnancy.models import PregnancyWeekNow


def login(request: HttpRequest):
    if request.method == 'POST':
        mobile_phone = request.POST.get('mobile_phone')
        password = request.POST.get('password')

        user: User = User.objects.filter(mobile_phone=mobile_phone).first()
        print(mobile_phone)

        if user is None:
            messages.error(request, 'User with this phone number does not exist!')
            return redirect('login')

        if not user.check_password(password):
            messages.error(request, 'Password is incorrect!')
            return redirect('login')

        auth.login(request, user)

        return redirect('/')

    return render(request, 'authorization/login.html')


def register(request: HttpRequest):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile_phone = request.POST.get('mobile_phone')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if User.objects.filter(mobile_phone=mobile_phone).exists():
            messages.error(request, 'User with this phone number already exists!')
            return redirect('register')

        new_user = User.objects.create(
            full_name=full_name,
            mobile_phone=mobile_phone,
            role=role,
            password=password
        )

        messages.success(request, 'User created successfully!')

        request.session['mobile_phone'] = mobile_phone
        request.session['password'] = password

        return redirect('enter-email')

    return render(request, 'authorization/register.html')


def enter_email(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST.get('email')

        send_email(
            email=email,
            subject='Amma - Verify email',
            message='Your verification code'
        )

        request.session['email'] = email

        return redirect('verify-email')

    return render(request, 'authorization/enter_email.html')


def verify_email(request: HttpRequest):
    mobile_phone = request.session.get('mobile_phone')
    password = request.session.get('password')
    email = request.session.get('email')

    if request.method == 'POST':
        body = json.loads(request.body)
        code = body.get('verification_code')

        if verify_account(email=email, code=int(code)):
            user = User.objects.filter(mobile_phone=mobile_phone).first()
            user.email = email
            user.save()

            if not user.check_password(password):
                return JsonResponse({'message': 'Password is incorrect!', 'status': 400})

            auth.login(request, user)

            return JsonResponse({'message': 'User verified successfully!', 'status': 200})

        return JsonResponse({'message': 'Verification code is incorrect!', 'status': 400})

    return render(request, 'authorization/verify_email.html', {'email': email})


def logout(request: HttpRequest):
    auth.logout(request)
    return redirect('login')


def profile(request: HttpRequest):
    if request.user.is_authenticated:
        profile = UserInfo.objects.filter(user=request.user).first()
        if not profile:
            UserInfo.objects.create(user=request.user)

        articles = Blog.objects.filter(author=request.user).order_by('-created_date')

        questionnaire_result = QuestionnaireResult.objects.filter(user=request.user).first()

        pregnancy_week = PregnancyWeekNow.objects.filter(user=request.user).last()  # Последняя запись для пользователя

        if pregnancy_week:
            start_date = pregnancy_week.start_date
            today = timezone.now().date()  # Текущая дата
            week_number = ((today - start_date).days // 7) + 1  # Вычисляем текущую неделю беременности (1 неделя = 7 дней)

            # Предполагаемая дата родов (40 недель с момента начала беременности)
            due_date = start_date + timedelta(weeks=40)

            # Прогресс беременности (вычисляем как процент от 40 недель)
            pregnancy_progress = ((week_number - 1) / 40) * 100 if week_number <= 40 else 100
        else:
            week_number = 0
            start_date = None
            due_date = None
            pregnancy_progress = 0

        context = {
            'profile': profile,
            'empty_fields': profile.empty_fields(),
            'completion_percentage': int(100 - (profile.empty_fields() / 5 * 100)),
            'articles': articles,
            'questionnaire_result': questionnaire_result,
            'week_number': week_number,
            'start_date': start_date,
            'due_date': due_date,
            'pregnancy_progress': pregnancy_progress,
        }
        return render(request, 'authorization/profile.html', context)
    else:
        return HttpResponse('', status=404)


def edit_profile(request):
    profile = UserInfo.objects.filter(user=request.user.id).first()
    articles = Blog.objects.filter(author=request.user).order_by('-created_date')

    # POST DATA: Profile contacts
    if request.method == 'POST' and 'full_name' in request.POST:
        avatar = request.FILES.get('avatar')
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        country = request.POST.get('country')

        if not full_name:
            messages.error(request, 'Full name is required.')
        else:
            if avatar:
                profile.photo_avatar = avatar
            profile.phone_number = phone_number
            profile.country = country
            profile.save()

            User.objects.filter(id=request.user.id).update(
                full_name=full_name
            )

        return redirect('edit_profile')

    # POST DATA: Change Email contacts
    if request.method == 'POST' and 'new_email' in request.POST:
        new_email = request.POST.get('new_email')
        confirm_password = request.POST.get('confirm_password')

        if profile.user.check_password(confirm_password):
            # Check if email is already in use by another user
            if User.objects.filter(Q(email=new_email) & ~Q(id=request.user.id)).exists():
                messages.error(request, 'Email address already in use.')
            else:
                User.objects.filter(id=request.user.id).update(email=new_email)
        else:
            messages.error(request, 'Invalid password')

        return redirect('edit_profile')

    # POST DATA: Change Password contacts
    if request.method == 'POST' and 'new_password' in request.POST:
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        if profile.user.check_password(current_password):
            user = User.objects.get(id=request.user.id)
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # update session
        else:
            messages.error(request, 'Invalid password.')

        return redirect('edit_profile')

    context = {
        'profile': profile,
        'empty_fields': profile.empty_fields() if profile else 0,
        'completion_percentage': int(100 - (profile.empty_fields() / 5 * 100)) if profile else 0,
        'articles': articles
    }

    return render(request, 'authorization/edit_profile.html', context)


def forgot_password(request: HttpRequest):
    if request.method == "POST":
        email = request.POST.get("email")

        send_email(
            email=email,
            subject="Donor - Reset password",
            message="Your verification code"
        )

        request.session['email'] = email

        return redirect("verify-by-code")

    return JsonResponse({"error": "Not Allowed Method", "status": 405})


def verify_by_code(request: HttpRequest):
    if request.method == "POST":
        email = request.session.get("email")
        body = json.loads(request.body)
        code = body.get('verification_code')

        if verify_account(email, code):
            return redirect("set-password")

        return JsonResponse({'message': 'Verification code is incorrect!', 'status': 400})

    return JsonResponse({"error": "Not Allowed Method", "status": 405})


def set_new_password(request: HttpRequest):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('set-password')

        user: User = User.objects.get(email=request.session.get("email"))

        user.set_password(password)

        return redirect("login")

    return JsonResponse({"error": "Not Allowed Method", "status": 405})
