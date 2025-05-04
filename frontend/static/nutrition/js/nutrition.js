/* JavaScript для улучшенного трекера питания */

document.addEventListener('DOMContentLoaded', function() {
    // Функциональность вкладок/табов для категорий питательных веществ
    const tabButtons = document.querySelectorAll('.tab-btn');
    const nutritionCards = document.querySelectorAll('.recommendation-card');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Убираем активный класс со всех кнопок
            tabButtons.forEach(btn => btn.classList.remove('active'));

            // Добавляем активный класс на кликнутую кнопку
            this.classList.add('active');

            // Получаем категорию из атрибута
            const category = this.dataset.category;

            // Показываем/скрываем карточки в зависимости от выбранной категории
            nutritionCards.forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.style.display = 'block';
                    // Анимация появления
                    fadeIn(card);
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Функциональность кнопок увеличения/уменьшения значения
    const decreaseButtons = document.querySelectorAll('.amount-btn.decrease');
    const increaseButtons = document.querySelectorAll('.amount-btn.increase');

    decreaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.nutrient-input');
            let value = parseFloat(input.value);

            // Уменьшаем значение, но не ниже 0
            value = Math.max(0, value - 1);

            // Округляем до 1 десятичного знака
            input.value = value.toFixed(1);

            // Подсвечиваем изменение
            highlightChange(input);
        });
    });

    increaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.nutrient-input');
            let value = parseFloat(input.value);
            const max = parseFloat(input.getAttribute('max') || 1000);

            // Увеличиваем значение, но не выше максимума
            value = Math.min(max, value + 1);

            // Округляем до 1 десятичного знака
            input.value = value.toFixed(1);

            // Подсвечиваем изменение
            highlightChange(input);
        });
    });

    // Функциональность кнопок быстрого добавления
    const quickOptionButtons = document.querySelectorAll('.quick-option');

    quickOptionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.recommendation-card');
            const input = card.querySelector('.nutrient-input');
            const amount = parseFloat(this.dataset.amount);

            // Устанавливаем указанное значение
            input.value = amount.toFixed(1);

            // Подсвечиваем изменение
            highlightChange(input);

            // Отправляем fetch, если есть кнопка Auto-Update
            const autoUpdateButton = card.querySelector('.auto-update-btn');
            if (autoUpdateButton && autoUpdateButton.checked) {
                const formData = new FormData(card.querySelector('.input-group'));
                const progressId = formData.get('progress_id');

                // Получаем CSRF токен
                const csrfToken = getCookie('csrftoken');

                // Отправляем AJAX запрос
                fetch('/nutrition_update_progress/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Обновляем прогресс-бар
                        const progressBar = card.querySelector('.progress-bar');
                        progressBar.style.width = `${data.progress_percentage}%`;

                        // Анимация успешного обновления
                        animateSuccess(progressBar);
                    }
                });
            }
        });
    });

    // Обработка отправки формы обновления прогресса через AJAX
    const updateForms = document.querySelectorAll('.input-group');

    updateForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const progressId = formData.get('progress_id');
            const amount = formData.get('amount');

            // Получаем CSRF токен
            const csrfToken = getCookie('csrftoken');

            // Отправляем AJAX запрос
            fetch('/nutrition_update_progress/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем прогресс-бар
                    const card = this.closest('.recommendation-card');
                    const progressBar = card.querySelector('.progress-bar');
                    const currentAmount = card.querySelector('.current-amount');

                    progressBar.style.width = `${data.progress_percentage}%`;
                    currentAmount.textContent = parseFloat(amount).toFixed(1);

                    // Анимация успешного обновления
                    animateSuccess(progressBar);

                    // Добавляем или удаляем бейдж завершения
                    updateCompleteBadge(card, data.progress_percentage);

                    // Обновляем общий прогресс
                    updateOverallProgress();
                } else {
                    alert('Не удалось обновить прогресс. Пожалуйста, попробуйте снова.');
                }
            })
            .catch(error => {
                console.error('Ошибка при обновлении прогресса:', error);
                alert('Произошла ошибка. Пожалуйста, попробуйте снова.');
            });
        });
    });

    // Инициализация страницы
    initializePage();

    // Функция для получения CSRF токена из cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Функция для анимации появления
    function fadeIn(element) {
        element.style.opacity = '0';
        element.style.transition = 'opacity 0.3s ease';

        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    }

    // Функция для подсветки изменения в поле ввода
    function highlightChange(input) {
        input.style.backgroundColor = '#f0f7ff';
        input.style.transition = 'background-color 0.5s ease';

        setTimeout(() => {
            input.style.backgroundColor = '';
        }, 300);
    }

    // Функция для анимации успешного обновления
    function animateSuccess(progressBar) {
        const originalColor = progressBar.style.backgroundColor;

        progressBar.style.transition = 'width 0.5s ease, background-color 0.5s ease';
        progressBar.style.backgroundColor = '#6ed06e';

        setTimeout(() => {
            progressBar.style.backgroundColor = originalColor;
        }, 1000);
    }

    // Функция для обновления бейджа завершения
    function updateCompleteBadge(card, percentage) {
        const existingBadge = card.querySelector('.complete-badge');

        if (percentage >= 100) {
            if (!existingBadge) {
                const badge = document.createElement('div');
                badge.className = 'complete-badge';
                badge.innerHTML = '<i class="icon-check"></i> Complete';

                card.appendChild(badge);

                // Анимация появления бейджа
                badge.style.opacity = '0';
                badge.style.transform = 'translateY(-10px)';
                badge.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

                setTimeout(() => {
                    badge.style.opacity = '1';
                    badge.style.transform = 'translateY(0)';
                }, 10);
            }
        } else if (existingBadge) {
            // Анимация исчезновения бейджа
            existingBadge.style.opacity = '0';
            existingBadge.style.transform = 'translateY(-10px)';

            setTimeout(() => {
                existingBadge.remove();
            }, 300);
        }
    }

    // Функция для обновления общего прогресса
    function updateOverallProgress() {
        const allNutrients = document.querySelectorAll('.recommendation-card').length;
        const completedNutrients = document.querySelectorAll('.complete-badge').length;

        const percentage = (completedNutrients / allNutrients) * 100;

        const circleChart = document.querySelector('.circular-chart .circle');
        const percentageText = document.querySelector('.circular-chart .percentage');

        if (circleChart && percentageText) {
            circleChart.setAttribute('stroke-dasharray', `${percentage}, 100`);
            percentageText.textContent = `${Math.round(percentage)}%`;
        }
    }

    // Функция для инициализации страницы
    function initializePage() {
        // Анимированное появление карточек
        const cards = document.querySelectorAll('.recommendation-card');

        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50 * index);
        });

        // Инициализация общего прогресса
        updateOverallProgress();
    }
});