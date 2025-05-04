import json
import os
from datetime import timedelta, date

from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from blog.models import Blog
from dashboard.models import QuestionnaireResult, QuestionnaireRecommendation, Vitamin, Workout, WorkoutCategory, \
    WorkoutDifficulty, NutritionContentType, NutritionContent, DailyRecommendation, NutritionTracker, NutrientProgress, \
    NutritionBenefit, NutrientCategory
from diploma import settings
from pregnancy.models import PregnancyWeekNow


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    count_blogs = Blog.objects.count()

    blogs = Blog.objects.annotate(count_of_comments=Count('blog_discussion')).order_by('-count_of_comments')

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
        "count_blogs": count_blogs,
        "blogs": blogs,
        "pregnancy_progress": pregnancy_progress
    }

    return render(request, 'dashboard/home.html', context)


def delete_pregnancy_progress(request):
    PregnancyWeekNow.objects.filter(user=request.user).delete()
    return redirect('profile')


def calendar_events(request):
    user = request.user
    result = QuestionnaireResult.objects.filter(user=user).latest('created_at')

    frequency_answer = result.answers.filter(
        question__text__icontains="How often would you like to know about changes").first()
    frequency = frequency_answer.text if frequency_answer else 'Every week'

    interval_days = {
        'Every day': 1,
        'Every week': 7,
        'Every month': 30
    }.get(frequency, 7)

    recommendations = QuestionnaireRecommendation.objects.filter(answers__in=result.answers.all()).distinct()
    vitamins = Vitamin.objects.all()
    workouts_list = Workout.objects.all()
    nutrition_content = NutritionContent.objects.all()

    start_date = date.today()
    max_count = 30

    events = []

    recommendations_list = list(recommendations)
    vitamins_list = list(vitamins)
    workouts_list = list(workouts_list)
    nutrition_content_list = list(nutrition_content)

    for idx in range(max_count):
        event_date = start_date + timedelta(days=interval_days * idx)
        daily_events = []

        if idx < len(recommendations_list):
            recommendation = recommendations_list[idx]
            daily_events.append({
                'color': 'blue',
                'text': f'{recommendation.title}',
                'href': f'/recommendation/{recommendation.id}',
            })

        # Добавляем стандартные события для отслеживания развития ребенка
        daily_events.append({
            'color': 'green',
            'text': "Check child's development",
            'href': f'/pregnancy/week-by-week/{idx + 2}',
        })

        if idx < len(vitamins_list):
            vitamin = vitamins_list[idx]
            daily_events.append({
                'color': 'purple',
                'text': f'{vitamin.name} - {vitamin.recommended_dose}',
                'href': f'/vitamins/{vitamin.id}',
            })

        if idx < len(workouts_list):
            workout = workouts_list[idx]
            daily_events.append({
                'color': 'red',
                'text': f'{workout.name}',
                'href': f'/workouts/{workout.slug}',
            })

        if idx < len(nutrition_content_list):
            nutrition = nutrition_content_list[idx]
            daily_events.append({
                'color': 'pink',
                'text': f'{nutrition.title}',
                'href': f'/nutritions/{nutrition.id}',
            })

        events.append({
            'date': event_date.isoformat(),
            'events': daily_events
        })

    return JsonResponse(events, safe=False)


def pregnancy_week_now(request):
    user = request.user
    pregnancy_week = PregnancyWeekNow.objects.filter(user=user).first()
    if not pregnancy_week:
        return JsonResponse({
            'status': 403
        })

    return JsonResponse({
        'status': 200
    })


def pregnancy_week_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        now_week_number = data.get('pregnancy_week')
        pregnancy, _ = PregnancyWeekNow.objects.update_or_create(
            user=request.user,
            start_date=now_week_number
        )

        return JsonResponse({
            'detail': 'Created',
            'status': 201
        })
    return JsonResponse({
        'detail': 'Method not allowed',
        'status': 405
    })


def vitamin_list(request):
    vitamins = Vitamin.objects.all()

    context = {
        'vitamins': vitamins
    }
    return render(request, 'vitamins/vitamin_list.html', context)


def vitamin_detail(request, pk):
    vitamin = Vitamin.objects.get(pk=pk)

    context = {
        'vitamin': vitamin
    }
    return render(request, 'vitamins/vitamin_detail.html', context)


def vitamin_related_api(request, vitamin_id):
    """API endpoint to get related vitamins for a specific vitamin"""
    try:
        vitamin = Vitamin.objects.get(id=vitamin_id, is_active=True)

        # Logic to find related vitamins
        # For example, vitamins recommended for the same trimester
        related_vitamins = []

        if vitamin.trimester_1:
            related_vitamins.extend(Vitamin.objects.filter(trimester_1=True, is_active=True).exclude(id=vitamin_id)[:3])

        if vitamin.trimester_2 and len(related_vitamins) < 3:
            related_vitamins.extend(Vitamin.objects.filter(trimester_2=True, is_active=True).exclude(id=vitamin_id)[
                                    :3 - len(related_vitamins)])

        if vitamin.trimester_3 and len(related_vitamins) < 3:
            related_vitamins.extend(Vitamin.objects.filter(trimester_3=True, is_active=True).exclude(id=vitamin_id)[
                                    :3 - len(related_vitamins)])

        # Add critical vitamins if we still need more
        if len(related_vitamins) < 3:
            related_vitamins.extend(Vitamin.objects.filter(critical=True, is_active=True).exclude(id=vitamin_id)[
                                    :3 - len(related_vitamins)])

        # Deduplicate (in case a vitamin appears in multiple categories)
        related_vitamins = list({v.id: v for v in related_vitamins}.values())

        # Convert to JSON-serializable format
        related_data = []
        for rv in related_vitamins:
            related_data.append({
                'id': rv.id,
                'name': rv.name,
                'recommended_dose': rv.recommended_dose,
                'image': rv.image.url if rv.image else '',
            })

        print("Related data:", related_data)  # Debugging line

        return JsonResponse(related_data, safe=False)

    except Vitamin.DoesNotExist:
        return JsonResponse([], safe=False)


def workout_list(request, category_slug=None, trimester=None):
    """
    Отображение списка тренировок с фильтрацией по категории или триместру
    """
    category = None
    categories = WorkoutCategory.objects.filter(is_active=True)
    workouts = Workout.objects.filter(is_active=True)

    # Применяем фильтр по категории, если указан
    if category_slug:
        category = get_object_or_404(WorkoutCategory, slug=category_slug, is_active=True)
        workouts = workouts.filter(category=category)

    # Применяем фильтр по триместру, если указан
    if trimester:
        workouts = workouts.filter(trimester__in=[trimester, 0])  # 0 = все триместры

    # Пагинация: 9 тренировок на страницу
    paginator = Paginator(workouts, 9)
    page = request.GET.get('page')

    try:
        workouts_page = paginator.page(page)
    except PageNotAnInteger:
        # Если page не целое число, вернуть первую страницу
        workouts_page = paginator.page(1)
    except EmptyPage:
        # Если page больше максимального, вернуть последнюю страницу
        workouts_page = paginator.page(paginator.num_pages)

    # Формируем контекст для шаблона
    context = {
        'category': category,
        'categories': categories,
        'workouts': workouts_page,
        'current_trimester': trimester,
        'trimester_choices': dict(Workout.TRIMESTER_CHOICES),
    }

    return render(request, 'workout/workout_list.html', context)


def workout_detail(request, slug):
    """
    Детальное представление тренировки
    """
    workout = get_object_or_404(Workout, slug=slug, is_active=True)

    # Рекомендуемые тренировки той же категории (кроме текущей)
    related_workouts = Workout.objects.filter(
        category=workout.category,
        is_active=True
    ).exclude(id=workout.id)[:3]

    context = {
        'workout': workout,
        'related_workouts': related_workouts,
    }

    return render(request, 'workout/workout_detail.html', context)


def nutrition_home(request):
    """Main nutrition page view"""
    # Get content types for filtering
    content_types = NutritionContentType.objects.all()

    # Get nutrition content for display
    content = NutritionContent.objects.all().order_by('-created_at')

    # Get daily recommendations based on user's trimester
    # Default to first trimester if not logged in or no profile
    trimester = 'all'

    if request.user.is_authenticated:
        # Logic to determine user's trimester from profile (implementation depends on your user profile model)
        # Example: trimester = request.user.profile.trimester
        pass

    recommendations = DailyRecommendation.objects.filter(trimester__in=[trimester, 'all'])

    # Get user's nutrition tracker for today if logged in
    tracker_data = None
    if request.user.is_authenticated:
        today = timezone.now().date()
        tracker, created = NutritionTracker.objects.get_or_create(
            user=request.user,
            date=today
        )

        # Create progress records for any missing nutrients
        for rec in recommendations:
            NutrientProgress.objects.get_or_create(
                tracker=tracker,
                nutrient=rec
            )

        # Get all progress records for this tracker
        tracker_data = tracker.progress.all()

        # Если есть данные трекера, рассчитываем процент выполнения
        progress_percentage = 0
        if tracker_data:
            for progress in tracker_data:
                progress.half_amount = progress.nutrient.target_amount / 2
                progress.quarter_amount = progress.nutrient.target_amount / 4

            completed_count = sum(1 for progress in tracker_data if progress.progress_percentage >= 100)
            if tracker_data.count() > 0:
                progress_percentage = (completed_count / tracker_data.count()) * 100

    context = {
        'content_types': content_types,
        'nutrition_content': content,
        'recommendations': recommendations,
        'tracker_data': tracker_data,
        'total_items': tracker_data.count() if tracker_data else 0,
        'completed_count': completed_count if tracker_data else 0,
        'progress_percentage': progress_percentage,
    }

    return render(request, 'nutrition/nutrition.html', context)


def nutrition_detail(request, content_id):
    """View for a specific nutrition content item"""
    content = get_object_or_404(NutritionContent, id=content_id)
    related_content = NutritionContent.objects.filter(
        content_type=content.content_type
    ).exclude(id=content_id)[:3]  # Get 3 related items of the same type

    context = {
        'content': content,
        'related_content': related_content,
    }

    return render(request, 'nutrition/nutrition_detail.html', context)


def filter_content(request):
    """AJAX view for filtering nutrition content"""
    content_type = request.GET.get('type', '')
    trimester = request.GET.get('trimester', '')
    search = request.GET.get('search', '')

    content = NutritionContent.objects.all()

    if content_type and content_type != 'All':
        content = content.filter(content_type__name=content_type)

    if trimester and trimester != 'All':
        content = content.filter(trimester=trimester)

    if search:
        content = content.filter(title__icontains=search)

    # Return JsonResponse with content data for frontend rendering
    content_data = []
    for item in content:
        benefits = [benefit.name for benefit in item.benefits.all()]

        data = {
            'id': item.id,
            'title': item.title,
            'image_url': item.image.url if item.image else '',
            'content_type': item.content_type.name,
            'trimester': item.trimester,
            'description': item.description[:100] + '...',
            'color_code': item.color_code,
            'benefits': benefits,
        }

        # Add type-specific fields
        if item.content_type.name == 'Recipe':
            data.update({
                'prep_time': item.prep_time,
                'cook_time': item.cook_time,
                'difficulty': item.difficulty,
            })
        elif item.content_type.name == 'Meal Plan':
            data.update({
                'days': item.days,
                'focus': item.focus,
            })
        else:  # Nutrition Facts or Supplements
            data.update({
                'read_time': item.read_time,
            })

        content_data.append(data)

    return JsonResponse({'content': content_data})


@login_required
def update_nutrient_progress(request):
    """AJAX view for updating nutrient progress"""
    if request.method == 'POST':
        progress_id = request.POST.get('progress_id')
        amount = float(request.POST.get('amount', 0))

        progress = get_object_or_404(NutrientProgress, id=progress_id)
        progress.current_amount = amount
        progress.save()

        return JsonResponse({
            'success': True,
            'progress_percentage': progress.progress_percentage
        })

    return JsonResponse({'success': False}, status=400)


def seed_nutrition_data(request):
    """
    Endpoint for populating the database with test data about pregnancy nutrition.
    Accessible via GET request.
    """
    # Check for secret key for security (optional)
    secret_key = request.GET.get('key')
    if not settings.DEBUG and (not secret_key or secret_key != 'your_secret_seed_key'):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        with transaction.atomic():
            # Clear existing data if clear=true parameter is specified
            if request.GET.get('clear') == 'true':
                NutritionContent.objects.all().delete()
                NutrientProgress.objects.all().delete()
                NutritionTracker.objects.all().delete()
                NutritionBenefit.objects.all().delete()
                DailyRecommendation.objects.all().delete()
                NutrientCategory.objects.all().delete()
                NutritionContentType.objects.all().delete()

            # Create nutrient categories
            nutrient_categories = seed_nutrient_categories()

            # Create content types
            content_types = seed_content_types()

            # Create daily nutrient recommendations
            daily_recommendations = seed_daily_recommendations()

            # Create health benefits
            benefits = seed_benefits()

            # Create nutrition content
            nutrition_content = seed_nutrition_content(content_types, benefits)

        # Prepare response data
        data = {
            "success": True,
            "message": "Database successfully populated with test data",
            "stats": {
                "nutrient_categories": len(nutrient_categories),
                "content_types": len(content_types),
                "daily_recommendations": len(daily_recommendations),
                "benefits": len(benefits),
                "nutrition_content": len(nutrition_content),
            }
        }

        # Return JSON response if requested via AJAX, otherwise render template
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(data)
        else:
            return render(request, 'nutrition/seeder_result.html', data)

    except Exception as e:
        error_data = {
            "success": False,
            "error": str(e)
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(error_data, status=500)
        else:
            return render(request, 'nutrition/seeder_result.html', error_data, status=500)


def seed_nutrient_categories():
    """Create nutrient categories"""
    categories = [
        {
            "name": "Vitamins",
            "color_code": "#b3a2d1"  # Lavender
        },
        {
            "name": "Minerals",
            "color_code": "#b8e0d2"  # Mint
        },
        {
            "name": "Macronutrients",
            "color_code": "#fed9ca"  # Peach
        },
        {
            "name": "Water & Hydration",
            "color_code": "#a2c8e0"  # Blue
        },
        {
            "name": "Micronutrients",
            "color_code": "#f8c291"  # Orange
        },
        {
            "name": "Fatty Acids",
            "color_code": "#f7db95"  # Yellow
        }
    ]

    created_categories = []
    for category in categories:
        cat_obj, created = NutrientCategory.objects.get_or_create(
            name=category["name"],
            defaults={"color_code": category["color_code"]}
        )
        created_categories.append(cat_obj)

    return created_categories


def seed_content_types():
    """Create content types"""
    types = [
        {"name": "Recipe"},
        {"name": "Meal Plan"},
        {"name": "Nutrition Facts"},
        {"name": "Supplements"},
        {"name": "Tips & Advice"}
    ]

    created_types = []
    for content_type in types:
        type_obj, created = NutritionContentType.objects.get_or_create(
            name=content_type["name"]
        )
        created_types.append(type_obj)

    return created_types


def seed_daily_recommendations():
    """Create daily nutrient recommendations"""
    recommendations = [
        {
            "nutrient": "Water",
            "target_amount": 2.5,
            "unit": "L",
            "trimester": "all",
            "color_code": "#a2c8e0",
            "description": "Adequate water intake is essential for amniotic fluid formation, increased blood volume, and carrying nutrients to your baby. During pregnancy, your water needs increase by about 300ml per day."
        },
        {
            "nutrient": "Protein",
            "target_amount": 75,
            "unit": "g",
            "trimester": "all",
            "color_code": "#fed9ca",
            "description": "Protein is critical for your baby's growth, especially in the second and third trimesters when growth accelerates. It's the building block for your baby's cells, the placenta, and maternal tissues."
        },
        {
            "nutrient": "Calcium",
            "target_amount": 1000,
            "unit": "mg",
            "trimester": "all",
            "color_code": "#b8e0d2",
            "description": "Calcium helps build your baby's bones and teeth. If you don't get enough calcium, your body will take it from your bones, which can lead to health problems later on."
        },
        {
            "nutrient": "Folate",
            "target_amount": 600,
            "unit": "mcg",
            "trimester": "all",
            "color_code": "#b3a2d1",
            "description": "Folate (vitamin B9) is crucial in early pregnancy for preventing neural tube defects and supporting the rapid cell division happening as your baby grows."
        },
        {
            "nutrient": "Iron",
            "target_amount": 27,
            "unit": "mg",
            "trimester": "all",
            "color_code": "#f8c291",
            "description": "Iron helps your body make more blood to supply oxygen to your baby and prevents anemia, a condition that can make you feel tired and weak."
        },
        {
            "nutrient": "Iodine",
            "target_amount": 220,
            "unit": "mcg",
            "trimester": "all",
            "color_code": "#f7db95",
            "description": "Iodine is needed for thyroid hormone production, which regulates metabolism and is important for your baby's brain and nervous system development."
        },
        {
            "nutrient": "Vitamin D",
            "target_amount": 15,
            "unit": "mcg",
            "trimester": "all",
            "color_code": "#f7db95",
            "description": "Vitamin D helps your body absorb calcium and phosphorus, needed for your baby's developing bones and teeth. It also supports immune function and may lower the risk of pregnancy complications."
        },
        {
            "nutrient": "Omega-3 (DHA)",
            "target_amount": 300,
            "unit": "mg",
            "trimester": "all",
            "color_code": "#a2c8e0",
            "description": "DHA, an omega-3 fatty acid, plays a key role in your baby's brain and eye development. It's especially important in the third trimester when the brain is rapidly growing."
        },
        {
            "nutrient": "Magnesium",
            "target_amount": 350,
            "unit": "mg",
            "trimester": "all",
            "color_code": "#b8e0d2",
            "description": "Magnesium supports over 300 biochemical reactions in the body and helps regulate blood sugar levels, blood pressure, and muscle function, including the uterus."
        },
        {
            "nutrient": "Zinc",
            "target_amount": 11,
            "unit": "mg",
            "trimester": "all",
            "color_code": "#b3a2d1",
            "description": "Zinc supports your immune system, wound healing, and helps with DNA and protein synthesis, necessary for proper cell development."
        },
        {
            "nutrient": "Vitamin C",
            "target_amount": 85,
            "unit": "mg",
            "trimester": "all",
            "color_code": "#a8d5aa",
            "description": "Vitamin C helps your body absorb iron, promotes your baby's immune system development, and is an antioxidant that protects cells from damage."
        },
        {
            "nutrient": "Fiber",
            "target_amount": 28,
            "unit": "g",
            "trimester": "all",
            "color_code": "#a8d5aa",
            "description": "Fiber helps prevent constipation, a common pregnancy complaint, and supports digestive health. It can also help control blood sugar levels."
        }
    ]

    created_recommendations = []
    for rec in recommendations:
        rec_obj, created = DailyRecommendation.objects.get_or_create(
            nutrient=rec["nutrient"],
            trimester=rec["trimester"],
            defaults={
                "target_amount": rec["target_amount"],
                "unit": rec["unit"],
                "color_code": rec["color_code"],
                "description": rec["description"]
            }
        )
        created_recommendations.append(rec_obj)

    return created_recommendations


def seed_benefits():
    """Create health benefits"""
    benefits = [
        {"name": "Iron"},
        {"name": "Calcium"},
        {"name": "Folate"},
        {"name": "Protein"},
        {"name": "Fiber"},
        {"name": "Vitamin C"},
        {"name": "Omega-3"},
        {"name": "Vitamin D"},
        {"name": "Magnesium"},
        {"name": "Zinc"},
        {"name": "Balanced"},
        {"name": "Energy"},
        {"name": "Nausea-friendly"},
        {"name": "Brain development"},
        {"name": "Bone health"},
        {"name": "Immunity"},
        {"name": "Digestive health"},
        {"name": "Heart health"},
        {"name": "Blood sugar control"},
        {"name": "Antioxidants"},
        {"name": "Swelling relief"},
        {"name": "Skin health"}
    ]

    created_benefits = []
    for benefit in benefits:
        benefit_obj, created = NutritionBenefit.objects.get_or_create(
            name=benefit["name"]
        )
        created_benefits.append(benefit_obj)

    return created_benefits


def seed_nutrition_content(content_types, benefits):
    """Create nutrition content"""

    # Find content types by name
    recipe_type = next((ct for ct in content_types if ct.name == "Recipe"), None)
    meal_plan_type = next((ct for ct in content_types if ct.name == "Meal Plan"), None)
    info_type = next((ct for ct in content_types if ct.name == "Nutrition Facts"), None)
    supplements_type = next((ct for ct in content_types if ct.name == "Supplements"), None)
    tips_type = next((ct for ct in content_types if ct.name == "Tips & Advice"), None)

    # Structure to store content
    content_items = []

    # ============= RECIPES =============
    recipes = [
        {
            "title": "Spinach & Feta Breakfast Wrap",
            "trimester": "all",
            "description": "This nutritious breakfast is rich in iron from spinach, calcium from feta cheese, and protein from eggs. It's the perfect start to a mother-to-be's day! The dish helps maintain energy levels and provides important nutrients for your baby's development.",
            "color_code": "#a8d5aa",
            "prep_time": 10,
            "cook_time": 15,
            "difficulty": "easy",
            "recipe_steps": "1. Heat olive oil in a non-stick pan over medium heat.\n2. Add 2 cups fresh spinach and cook until wilted, about 2 minutes.\n3. Whisk 2 eggs in a bowl, then pour over the spinach.\n4. Cook until eggs are set, about 3 minutes.\n5. Sprinkle with 2 tablespoons crumbled feta cheese and let melt slightly.\n6. Season with salt and pepper to taste.\n7. Serve with a whole grain toast for extra fiber.",
            "benefits": ["Iron", "Calcium", "Folate", "Protein"]
        },
        {
            "title": "Ginger Lentil Soup",
            "trimester": "all",
            "description": "This warming soup is a powerhouse of iron and plant-based protein. The ginger helps combat nausea, while tomatoes provide vitamin C to enhance iron absorption. A perfect dish for all trimesters that you can make ahead and freeze.",
            "color_code": "#f8c291",
            "prep_time": 15,
            "cook_time": 30,
            "difficulty": "medium",
            "recipe_steps": "1. Dice 1 onion, 2 carrots, and 2 celery stalks.\n2. Mince 2 garlic cloves and 1 tablespoon fresh ginger.\n3. Heat 2 tablespoons olive oil in a large pot.\n4. Sauté onion, carrots, and celery until soft, about 5 minutes.\n5. Add garlic and ginger, cook for 30 seconds until fragrant.\n6. Add 1 cup red lentils (rinsed), 1 can diced tomatoes, and 4 cups vegetable broth.\n7. Season with turmeric, cumin, salt, and pepper.\n8. Bring to a boil, then reduce heat and simmer for 25-30 minutes until lentils are tender.\n9. Optional: purée to desired consistency with an immersion blender.\n10. Serve with a lemon wedge and fresh parsley.",
            "benefits": ["Iron", "Protein", "Fiber", "Vitamin C", "Nausea-friendly"]
        },
        {
            "title": "Blueberry Avocado Smoothie Bowl",
            "trimester": "all",
            "description": "This nutrient-packed smoothie bowl combines healthy fats from avocado, antioxidants from blueberries, and calcium from yogurt. It's easy to digest, making it perfect for first-trimester morning sickness, and provides important nutrients for your baby's brain development.",
            "color_code": "#b3a2d1",
            "prep_time": 5,
            "cook_time": 0,
            "difficulty": "easy",
            "recipe_steps": "1. In a blender, combine 1/2 ripe avocado, 1 cup frozen blueberries, 1/2 banana, 1/2 cup Greek yogurt, and 1/4 cup almond milk.\n2. Blend until smooth and creamy.\n3. Pour into a bowl.\n4. Top with fresh berries, granola, chia seeds, and coconut flakes.",
            "benefits": ["Omega-3", "Calcium", "Antioxidants", "Brain development", "Nausea-friendly"]
        },
        {
            "title": "Quinoa Roasted Vegetable Salad",
            "trimester": "all",
            "description": "This colorful salad combines complete protein from quinoa with a variety of roasted vegetables rich in fiber and vitamins. The addition of seeds provides essential fatty acids, while feta cheese adds calcium. Perfect for lunch or a light dinner.",
            "color_code": "#a8d5aa",
            "prep_time": 15,
            "cook_time": 30,
            "difficulty": "medium",
            "recipe_steps": "1. Cook 1 cup quinoa according to package instructions.\n2. Dice 1 bell pepper, 1 zucchini, 1 eggplant, and 1 red onion.\n3. Spread vegetables on a baking sheet, drizzle with olive oil, season with salt and pepper.\n4. Roast at 400°F (200°C) for 25-30 minutes, stirring once.\n5. Combine cooked quinoa with roasted vegetables.\n6. Add 1/4 cup crumbled feta cheese, 2 tablespoons pumpkin seeds, and 2 tablespoons chopped fresh mint.\n7. Make a dressing with 3 tablespoons olive oil, 1 tablespoon lemon juice, 1 minced garlic clove, salt, and pepper.\n8. Drizzle dressing over salad and gently toss.",
            "benefits": ["Protein", "Fiber", "Folate", "Calcium", "Balanced"]
        },
        {
            "title": "Grilled Salmon with Lemon Sauce",
            "trimester": "all",
            "description": "Salmon is one of the best sources of omega-3 fatty acids essential for your baby's brain development. This dish is also rich in high-quality protein and vitamin D. The simple lemon sauce enhances the fish's flavor and adds vitamin C.",
            "color_code": "#fed9ca",
            "prep_time": 10,
            "cook_time": 15,
            "difficulty": "medium",
            "recipe_steps": "1. Mix 2 tablespoons olive oil, juice and zest of 1 lemon, 1 minced garlic clove, 1 teaspoon honey, salt, and pepper.\n2. Brush 4 salmon fillets (about 5oz each) with half the marinade and let sit for 10 minutes.\n3. Heat grill or pan over medium heat.\n4. Cook salmon skin-side down for 4-5 minutes, then flip and cook for another 3-4 minutes or until done.\n5. Serve drizzled with remaining sauce and garnish with fresh dill.\n6. Pair with quinoa or brown rice and green vegetables.",
            "benefits": ["Omega-3", "Protein", "Vitamin D", "Brain development"]
        },
        {
            "title": "Oatmeal Fruit Pancakes",
            "trimester": "1",
            "description": "These gentle oatmeal pancakes are perfect for the first trimester when nausea might be troublesome. They're easy to digest, provide steady energy, and contain fiber that helps with pregnancy-related constipation.",
            "color_code": "#f7db95",
            "prep_time": 10,
            "cook_time": 15,
            "difficulty": "easy",
            "recipe_steps": "1. In a bowl, mix 1 cup rolled oats, 1 teaspoon baking powder, and 1/4 teaspoon salt.\n2. In another bowl, whisk 1 egg, 3/4 cup milk, 1 tablespoon maple syrup, and 1 teaspoon vanilla extract.\n3. Combine wet and dry ingredients, let sit for 5 minutes to allow oats to absorb liquid.\n4. Dice 1/2 cup fruit (apples, pears, or bananas) into small pieces and gently fold into batter.\n5. Heat a pan over medium heat and lightly grease.\n6. Pour 1/4 cup batter for each pancake and cook 2-3 minutes per side.\n7. Serve with yogurt and fresh fruit.",
            "benefits": ["Energy", "Fiber", "Nausea-friendly", "Digestive health"]
        },
        {
            "title": "Chia Berry Overnight Pudding",
            "trimester": "all",
            "description": "This no-cook breakfast is packed with omega-3 fatty acids from chia seeds, calcium from milk, and antioxidants from berries. Preparing it the night before makes it a convenient option for busy mornings or when you need a quick nutrient boost.",
            "color_code": "#b3a2d1",
            "prep_time": 5,
            "cook_time": 0,
            "difficulty": "easy",
            "recipe_steps": "1. In a jar or container, combine 3 tablespoons chia seeds, 1 cup milk or plant-based milk, 1/2 teaspoon vanilla extract, and 1 teaspoon honey or maple syrup.\n2. Stir well, then refrigerate for at least 4 hours or overnight.\n3. In the morning, stir again and check consistency (add more milk if too thick).\n4. Top with 1/2 cup mixed berries, 1 tablespoon chopped nuts, and a sprinkle of cinnamon.",
            "benefits": ["Omega-3", "Calcium", "Fiber", "Antioxidants"]
        },
        {
            "title": "Mediterranean Stuffed Bell Peppers",
            "trimester": "2",
            "description": "These colorful stuffed peppers are loaded with protein, fiber, and vitamins. The Mediterranean-inspired flavors include whole grains, lean protein, and plenty of vegetables for a complete meal that supports your second-trimester growth needs.",
            "color_code": "#a8d5aa",
            "prep_time": 20,
            "cook_time": 40,
            "difficulty": "medium",
            "recipe_steps": "1. Preheat oven to 375°F (190°C).\n2. Cut 4 bell peppers in half lengthwise and remove seeds.\n3. Cook 1 cup quinoa according to package directions.\n4. In a pan, sauté 1 diced onion in olive oil until translucent.\n5. Add 2 minced garlic cloves and cook for 30 seconds.\n6. Add 1 pound ground turkey or 1 can rinsed chickpeas and cook until done.\n7. Stir in 1 can diced tomatoes, 1 teaspoon dried oregano, 1 teaspoon dried basil, salt, and pepper.\n8. Add cooked quinoa, 1 cup chopped spinach, and 1/4 cup olives. Mix well.\n9. Fill pepper halves with mixture and place in baking dish.\n10. Top with 1/2 cup crumbled feta cheese.\n11. Cover with foil and bake for 30 minutes, then uncover and bake 10 more minutes.\n12. Garnish with fresh parsley before serving.",
            "benefits": ["Protein", "Fiber", "Folate", "Iron", "Calcium"]
        }
    ]

    for recipe_data in recipes:
        # Create recipe object
        recipe, created = NutritionContent.objects.get_or_create(
            title=recipe_data["title"],
            content_type=recipe_type,
            defaults={
                "trimester": recipe_data["trimester"],
                "description": recipe_data["description"],
                "color_code": recipe_data["color_code"],
                "prep_time": recipe_data["prep_time"],
                "cook_time": recipe_data["cook_time"],
                "difficulty": recipe_data["difficulty"],
                "recipe_steps": recipe_data["recipe_steps"],
            }
        )

        # If new recipe created or updating existing
        if created or True:  # For demonstration always update relationships
            # Add benefits
            for benefit_name in recipe_data["benefits"]:
                benefit = next((b for b in benefits if b.name == benefit_name), None)
                if benefit:
                    recipe.benefits.add(benefit)

            # Create or substitute placeholder for image
            if not recipe.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, recipe.image.name)):
                placeholder_name = f"recipe_{recipe.id}.jpg"
                placeholder_path = os.path.join(settings.MEDIA_ROOT, "nutrition_images", placeholder_name)

                # In a real application, you would create an actual image file
                # In this example, we just create an empty file as a placeholder
                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "nutrition_images")):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, "nutrition_images"))

                with open(placeholder_path, 'wb') as f:
                    f.write(b'placeholder')  # In a real app, this would be an actual image

                recipe.image = f"nutrition_images/{placeholder_name}"
                recipe.save()

        content_items.append(recipe)

    # ============= MEAL PLANS =============
    meal_plans = [
        {
            "title": "First Trimester Meal Plan",
            "trimester": "1",
            "description": "This 7-day meal plan is specifically designed for the first trimester when nausea and food aversions may be an issue. It includes gentle, nutrient-rich meals that help manage nausea while ensuring essential nutrient intake.",
            "color_code": "#b3a2d1",
            "days": 7,
            "focus": "Morning sickness relief",
            "benefits": ["Nausea-friendly", "Balanced", "Folate", "Digestive health"]
        },
        {
            "title": "Second Trimester Energy Boost Plan",
            "trimester": "2",
            "description": "In the second trimester, appetite usually returns and energy needs increase. This 5-day plan focuses on balanced nutrition with an emphasis on quality carbohydrates, proteins, and healthy fats to maintain energy and fuel your baby's healthy growth.",
            "color_code": "#f7db95",
            "days": 5,
            "focus": "Energy and nutrient boost",
            "benefits": ["Energy", "Balanced", "Iron", "Calcium", "Protein"]
        },
        {
            "title": "Third Trimester Meal Plan",
            "trimester": "3",
            "description": "In the third trimester, your baby is growing rapidly, and your body is preparing for birth. This plan focuses on nutrients that support your baby's brain development, bone health, and preparation for lactation. It also accounts for reduced stomach capacity due to your growing baby.",
            "color_code": "#fed9ca",
            "days": 7,
            "focus": "Birth preparation and lactation",
            "benefits": ["Omega-3", "Calcium", "Protein", "Brain development", "Bone health"]
        },
        {
            "title": "Gestational Diabetes Meal Plan",
            "trimester": "all",
            "description": "This specialized plan helps maintain stable blood sugar levels with gestational diabetes. It emphasizes balanced meals with a focus on protein, healthy fats, and complex carbohydrates that won't spike blood sugar, while still ensuring adequate nutrition for you and your baby.",
            "color_code": "#a8d5aa",
            "days": 7,
            "focus": "Blood sugar management",
            "benefits": ["Blood sugar control", "Balanced", "Protein", "Fiber", "Heart health"]
        },
        {
            "title": "High-Iron Pregnancy Meal Plan",
            "trimester": "all",
            "description": "Designed for mothers who need extra iron, this 5-day plan combines iron-rich foods with vitamin C to enhance absorption. Perfect for those with low iron levels or at risk of anemia, each meal is carefully crafted to maximize iron intake while maintaining overall nutritional balance.",
            "color_code": "#f8c291",
            "days": 5,
            "focus": "Iron boost and anemia prevention",
            "benefits": ["Iron", "Vitamin C", "Energy", "Protein", "Balanced"]
        }
    ]

    for plan_data in meal_plans:
        # Create meal plan object
        meal_plan, created = NutritionContent.objects.get_or_create(
            title=plan_data["title"],
            content_type=meal_plan_type,
            defaults={
                "trimester": plan_data["trimester"],
                "description": plan_data["description"],
                "color_code": plan_data["color_code"],
                "days": plan_data["days"],
                "focus": plan_data["focus"],
            }
        )

        # If new meal plan created or updating existing
        if created or True:  # For demonstration always update relationships
            # Add benefits
            for benefit_name in plan_data["benefits"]:
                benefit = next((b for b in benefits if b.name == benefit_name), None)
                if benefit:
                    meal_plan.benefits.add(benefit)

            # Create or substitute placeholder for image
            if not meal_plan.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, meal_plan.image.name)):
                placeholder_name = f"meal_plan_{meal_plan.id}.jpg"
                placeholder_path = os.path.join(settings.MEDIA_ROOT, "nutrition_images", placeholder_name)

                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "nutrition_images")):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, "nutrition_images"))

                with open(placeholder_path, 'wb') as f:
                    f.write(b'placeholder')

                meal_plan.image = f"nutrition_images/{placeholder_name}"
                meal_plan.save()

        content_items.append(meal_plan)

    # ============= NUTRITION FACTS =============
    nutrition_facts = [
        {
            "title": "Foods Rich in Folate",
            "trimester": "all",
            "description": "Folate is a B vitamin that is crucial during pregnancy, especially in the first trimester. It helps prevent neural tube defects and supports the development of your baby's brain and spinal cord. This guide covers the best natural sources of folate to include in your pregnancy diet.",
            "color_code": "#b8e0d2",
            "read_time": 5,
            "benefits": ["Folate", "Brain development", "Balanced"]
        },
        {
            "title": "Iron-Rich Foods for Pregnancy",
            "trimester": "all",
            "description": "Iron requirements nearly double during pregnancy to support increased blood volume and your baby's development. This guide explores both animal and plant sources of iron, explains how to enhance absorption, and includes delicious iron-rich recipe ideas to help prevent anemia.",
            "color_code": "#f8c291",
            "read_time": 6,
            "benefits": ["Iron", "Energy", "Balanced"]
        },
        {
            "title": "Calcium Beyond Dairy: Alternative Sources",
            "trimester": "all",
            "description": "While dairy products are well-known calcium sources, there are many alternatives for those who can't consume or prefer to limit dairy. This comprehensive guide explores plant-based calcium sources, fortified foods, and tips to ensure adequate calcium intake for you and your baby's bone development.",
            "color_code": "#b3a2d1",
            "read_time": 4,
            "benefits": ["Calcium", "Bone health", "Balanced"]
        },
        {
            "title": "Hydration Strategies During Pregnancy",
            "trimester": "all",
            "description": "Proper hydration is essential for amniotic fluid, nutrient circulation, and managing common pregnancy discomforts. This guide provides creative tips for staying hydrated, signs of dehydration to watch for, and delicious alternatives to plain water that support maternal and fetal health.",
            "color_code": "#a2c8e0",
            "read_time": 5,
            "benefits": ["Swelling relief", "Digestive health", "Energy"]
        },
        {
            "title": "Omega-3 Fatty Acids for Baby's Brain Development",
            "trimester": "all",
            "description": "Omega-3 fatty acids, particularly DHA, are essential for your baby's brain and eye development. This guide explores the best food sources (including options for vegetarians and vegans), recommended intake levels, and how omega-3s benefit both maternal and fetal health throughout pregnancy.",
            "color_code": "#f7db95",
            "read_time": 7,
            "benefits": ["Omega-3", "Brain development", "Heart health", "Skin health"]
        },
        {
            "title": "Managing Food Aversions in the First Trimester",
            "trimester": "1",
            "description": "Food aversions and nausea can make it challenging to maintain adequate nutrition during early pregnancy. This practical guide offers strategies to work around common aversions while ensuring you still get essential nutrients, with advice from registered dietitians and experiences from other mothers.",
            "color_code": "#fed9ca",
            "read_time": 6,
            "benefits": ["Nausea-friendly", "Balanced", "Energy"]
        },
        {
            "title": "Protein Requirements Throughout Pregnancy",
            "trimester": "all",
            "description": "Protein is the building block for your baby's cells and tissues. This comprehensive guide explains how protein needs change throughout pregnancy, highlights top protein sources (including plant-based options), and provides practical tips for incorporating sufficient protein into every meal and snack.",
            "color_code": "#a8d5aa",
            "read_time": 5,
            "benefits": ["Protein", "Balanced", "Energy"]
        },
        {
            "title": "Natural Ways to Manage Pregnancy Constipation",
            "trimester": "all",
            "description": "Constipation affects up to 50% of pregnant women due to hormonal changes and pressure from the growing uterus. This guide explores dietary strategies focused on fiber, hydration, and specific foods that can help maintain regularity naturally, along with safe physical activities to promote digestive health.",
            "color_code": "#b3a2d1",
            "read_time": 6,
            "benefits": ["Fiber", "Digestive health", "Swelling relief"]
        }
    ]

    for facts_data in nutrition_facts:
        # Create nutrition facts object
        facts, created = NutritionContent.objects.get_or_create(
            title=facts_data["title"],
            content_type=info_type,
            defaults={
                "trimester": facts_data["trimester"],
                "description": facts_data["description"],
                "color_code": facts_data["color_code"],
                "read_time": facts_data["read_time"],
            }
        )

        # If new facts created or updating existing
        if created or True:
            # Add benefits
            for benefit_name in facts_data["benefits"]:
                benefit = next((b for b in benefits if b.name == benefit_name), None)
                if benefit:
                    facts.benefits.add(benefit)

            # Create or substitute placeholder for image
            if not facts.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, facts.image.name)):
                placeholder_name = f"facts_{facts.id}.jpg"
                placeholder_path = os.path.join(settings.MEDIA_ROOT, "nutrition_images", placeholder_name)

                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "nutrition_images")):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, "nutrition_images"))

                with open(placeholder_path, 'wb') as f:
                    f.write(b'placeholder')

                facts.image = f"nutrition_images/{placeholder_name}"
                facts.save()

        content_items.append(facts)

    # ============= SUPPLEMENTS =============
    supplements = [
        {
            "title": "Prenatal Vitamins: What to Look For",
            "trimester": "all",
            "description": "Navigating prenatal vitamin options can be overwhelming. This evidence-based guide helps you understand the essential nutrients to look for in a quality prenatal supplement, how to choose the right one for your specific needs, and when to take them for optimal absorption and benefit.",
            "color_code": "#b3a2d1",
            "read_time": 8,
            "benefits": ["Folate", "Iron", "Calcium", "Vitamin D", "Balanced"]
        },
        {
            "title": "Third Trimester Supplements Guide",
            "trimester": "3",
            "description": "The third trimester brings unique nutritional needs as your baby's growth accelerates and you prepare for birth. While a balanced diet should provide most nutrients, some supplements may be recommended by your healthcare provider. This guide outlines common third-trimester supplements, their benefits, and what to look for when choosing them.",
            "color_code": "#fed9ca",
            "read_time": 7,
            "benefits": ["Omega-3", "Iron", "Calcium", "Vitamin D", "Energy"]
        },
        {
            "title": "Iron Supplements: Options and Optimization",
            "trimester": "all",
            "description": "Iron supplementation is often recommended during pregnancy, especially for those with anemia or at high risk. This comprehensive guide explains different types of iron supplements, strategies to minimize side effects, optimal timing for better absorption, and how to complement supplements with dietary iron.",
            "color_code": "#f8c291",
            "read_time": 6,
            "benefits": ["Iron", "Energy", "Balanced"]
        },
        {
            "title": "Probiotics During Pregnancy: Benefits and Options",
            "trimester": "all",
            "description": "Emerging research suggests probiotics may benefit both maternal and infant health during pregnancy. This evidence-based overview explores potential benefits for digestive health, immune function, and reducing pregnancy complications, along with guidance on choosing safe, effective probiotic supplements.",
            "color_code": "#a8d5aa",
            "read_time": 7,
            "benefits": ["Digestive health", "Immunity", "Balanced"]
        },
        {
            "title": "Vitamin D Supplementation in Pregnancy",
            "trimester": "all",
            "description": "Vitamin D deficiency is common during pregnancy and may impact both maternal and fetal health. This guide explains the importance of vitamin D, recommended intake levels, risk factors for deficiency, and how to choose between different supplement forms for optimal bone and immune health.",
            "color_code": "#f7db95",
            "read_time": 5,
            "benefits": ["Vitamin D", "Bone health", "Immunity", "Balanced"]
        }
    ]

    for supplement_data in supplements:
        # Create supplement object
        supplement, created = NutritionContent.objects.get_or_create(
            title=supplement_data["title"],
            content_type=supplements_type,
            defaults={
                "trimester": supplement_data["trimester"],
                "description": supplement_data["description"],
                "color_code": supplement_data["color_code"],
                "read_time": supplement_data["read_time"],
            }
        )

        # If new supplement created or updating existing
        if created or True:
            # Add benefits
            for benefit_name in supplement_data["benefits"]:
                benefit = next((b for b in benefits if b.name == benefit_name), None)
                if benefit:
                    supplement.benefits.add(benefit)

            # Create or substitute placeholder for image
            if not supplement.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, supplement.image.name)):
                placeholder_name = f"supplement_{supplement.id}.jpg"
                placeholder_path = os.path.join(settings.MEDIA_ROOT, "nutrition_images", placeholder_name)

                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "nutrition_images")):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, "nutrition_images"))

                with open(placeholder_path, 'wb') as f:
                    f.write(b'placeholder')

                supplement.image = f"nutrition_images/{placeholder_name}"
                supplement.save()

        content_items.append(supplement)

    # ============= TIPS & ADVICE =============
    tips = [
        {
            "title": "Mindful Eating During Pregnancy",
            "trimester": "all",
            "description": "Mindful eating can help you connect with your body's needs during pregnancy, manage cravings, and build a healthier relationship with food. This practical guide offers techniques to practice mindfulness at mealtimes, tune into hunger and fullness cues, and enjoy a more conscious approach to nourishing yourself and your baby.",
            "color_code": "#b8e0d2",
            "read_time": 5,
            "benefits": ["Balanced", "Digestive health", "Energy"]
        },
        {
            "title": "Creating a Pregnancy Meal Prep Routine",
            "trimester": "all",
            "description": "Meal preparation can be a lifesaver during pregnancy, especially when energy levels fluctuate. This step-by-step guide helps you establish an efficient meal prep routine with pregnancy-friendly recipes, safe food storage tips, and strategies to ensure nutritional variety while minimizing kitchen time.",
            "color_code": "#fed9ca",
            "read_time": 8,
            "benefits": ["Balanced", "Energy", "Protein"]
        },
        {
            "title": "Eating Out Wisely While Pregnant",
            "trimester": "all",
            "description": "Dining out doesn't have to compromise your pregnancy nutrition goals. This practical guide covers how to make healthy choices at different types of restaurants, foods to avoid for safety reasons, managing portion sizes, and special considerations for each trimester when enjoying meals away from home.",
            "color_code": "#a2c8e0",
            "read_time": 6,
            "benefits": ["Balanced", "Energy", "Digestive health"]
        },
        {
            "title": "Smart Snacking Strategies for Pregnancy",
            "trimester": "all",
            "description": "Strategic snacking helps maintain energy levels, manage hunger, and provide consistent nutrients throughout the day. This guide offers a variety of nutrient-dense snack ideas for different situations (on-the-go, at work, late night) with specific recommendations for each trimester's unique needs.",
            "color_code": "#a8d5aa",
            "read_time": 5,
            "benefits": ["Energy", "Balanced", "Protein", "Blood sugar control"]
        },
        {
            "title": "Navigating Food Cravings and Aversions",
            "trimester": "all",
            "description": "Food cravings and aversions are common pregnancy experiences that can impact nutrition. This evidence-based guide explains the potential causes, offers strategies to satisfy cravings in healthier ways, and provides creative alternatives when important food groups become unappetizing.",
            "color_code": "#b3a2d1",
            "read_time": 6,
            "benefits": ["Nausea-friendly", "Balanced", "Energy"]
        },
        {
            "title": "Managing Heartburn Through Diet",
            "trimester": "2",
            "description": "Heartburn affects many women, particularly in the second and third trimesters. This comprehensive guide explores dietary triggers to avoid, timing of meals, beneficial foods that may reduce symptoms, and safe eating positions that can help minimize discomfort while maintaining optimal nutrition.",
            "color_code": "#f8c291",
            "read_time": 5,
            "benefits": ["Digestive health", "Nausea-friendly", "Balanced"]
        }
    ]

    for tip_data in tips:
        # Create tip object
        tip, created = NutritionContent.objects.get_or_create(
            title=tip_data["title"],
            content_type=tips_type,
            defaults={
                "trimester": tip_data["trimester"],
                "description": tip_data["description"],
                "color_code": tip_data["color_code"],
                "read_time": tip_data["read_time"],
            }
        )

        # If new tip created or updating existing
        if created or True:
            # Add benefits
            for benefit_name in tip_data["benefits"]:
                benefit = next((b for b in benefits if b.name == benefit_name), None)
                if benefit:
                    tip.benefits.add(benefit)

            # Create or substitute placeholder for image
            if not tip.image or not os.path.exists(os.path.join(settings.MEDIA_ROOT, tip.image.name)):
                placeholder_name = f"tip_{tip.id}.jpg"
                placeholder_path = os.path.join(settings.MEDIA_ROOT, "nutrition_images", placeholder_name)

                if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "nutrition_images")):
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, "nutrition_images"))

                with open(placeholder_path, 'wb') as f:
                    f.write(b'placeholder')

                tip.image = f"nutrition_images/{placeholder_name}"
                tip.save()

        content_items.append(tip)

    return content_items