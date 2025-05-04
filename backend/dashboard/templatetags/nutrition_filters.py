from django import template
register = template.Library()


@register.filter
def count_completed(progress_list):
    """Подсчитывает количество элементов с процентом выполнения >= 100%"""
    return len([item for item in progress_list if item.progress_percentage >= 100])