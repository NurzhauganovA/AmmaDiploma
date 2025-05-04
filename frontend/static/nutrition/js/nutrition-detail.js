/* nutrition-detail.js - JavaScript for the redesigned nutrition detail page */

document.addEventListener('DOMContentLoaded', function() {
    // Tab Navigation
    initTabNavigation();

    // Servings adjustment
    initServingsControl();

    // Day selector for meal plans
    initDaySelector();

    // Shopping list filters
    initShoppingFilters();

    // Shopping list select/deselect all
    initShoppingSelectButtons();

    // Timer functionality
    initCookingTimer();

    // Bookmark and Share functionality
    initActionButtons();

    // Checkbox handlers
    initCheckboxes();
});

/**
 * Initialize tab navigation
 */
function initTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');

            // Remove active class from all tabs and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            document.getElementById(targetId).classList.add('active');

            // Smooth scroll to content
            window.scrollTo({
                top: document.querySelector('.tab-navigation').offsetTop - 20,
                behavior: 'smooth'
            });
        });
    });
}

/**
 * Initialize servings control for ingredients
 */
function initServingsControl() {
    const servingDecrease = document.querySelector('.serving-adjust[data-action="decrease"]');
    const servingIncrease = document.querySelector('.serving-adjust[data-action="increase"]');
    const servingCount = document.querySelector('.serving-count');

    if (servingDecrease && servingIncrease && servingCount) {
        servingDecrease.addEventListener('click', function() {
            let count = parseInt(servingCount.textContent);
            if (count > 1) {
                count--;
                servingCount.textContent = count;
                updateIngredientAmounts(count);
            }
        });

        servingIncrease.addEventListener('click', function() {
            let count = parseInt(servingCount.textContent);
            count++;
            servingCount.textContent = count;
            updateIngredientAmounts(count);
        });
    }
}

/**
 * Update ingredient amounts based on servings
 */
function updateIngredientAmounts(servings) {
    const baseServings = 2; // Initial servings count
    const ratio = servings / baseServings;

    // Original ingredient amounts (for a reset)
    const originalAmounts = [
        '2 cups',
        '2',
        '1/4 cup',
        '1',
        '1 tbsp',
        'to taste'
    ];

    const amountElements = document.querySelectorAll('.ingredient-amount');

    amountElements.forEach((element, index) => {
        const originalAmount = originalAmounts[index];

        // Skip ingredients with "to taste" or similar non-numeric amounts
        if (originalAmount === 'to taste' || originalAmount === 'as needed' || originalAmount === 'for garnish') {
            return;
        }

        // Extract numeric value and unit from original amount
        const match = originalAmount.match(/^([\d./]+)(?:\s+(.+))?$/);

        if (match) {
            let numValue = match[1];
            const unit = match[2] || '';

            // Handle fractions
            if (numValue.includes('/')) {
                const [numerator, denominator] = numValue.split('/');
                numValue = parseFloat(numerator) / parseFloat(denominator);
            } else {
                numValue = parseFloat(numValue);
            }

            // Calculate new value
            let newValue = numValue * ratio;

            // Format the new value
            if (Number.isInteger(newValue)) {
                newValue = newValue.toString();
            } else {
                // Try to convert to fraction for common values
                const fraction = toFraction(newValue);
                if (fraction) {
                    newValue = fraction;
                } else {
                    newValue = newValue.toFixed(1).replace(/\.0$/, '');
                }
            }

            // Update the amount text
            element.textContent = unit ? `${newValue} ${unit}` : newValue;
        }
    });
}

/**
 * Convert decimal to fraction string
 */
function toFraction(decimal) {
    const tolerance = 0.03;

    // Common fractions map
    const fractions = [
        {decimal: 0.25, fraction: '1/4'},
        {decimal: 0.33, fraction: '1/3'},
        {decimal: 0.5, fraction: '1/2'},
        {decimal: 0.66, fraction: '2/3'},
        {decimal: 0.75, fraction: '3/4'}
    ];

    // Check for common fractions
    for (const item of fractions) {
        if (Math.abs(decimal - item.decimal) < tolerance) {
            return item.fraction;
        }
    }

    // For whole numbers with fractions
    const wholePart = Math.floor(decimal);
    const decimalPart = decimal - wholePart;

    if (wholePart > 0 && decimalPart > 0) {
        for (const item of fractions) {
            if (Math.abs(decimalPart - item.decimal) < tolerance) {
                return `${wholePart} ${item.fraction}`;
            }
        }
    }

    return null;
}

/**
 * Initialize day selector for meal plans
 */
function initDaySelector() {
    const dayButtons = document.querySelectorAll('.day-button');
    const dayContents = document.querySelectorAll('.day-content');

    if (dayButtons.length > 0 && dayContents.length > 0) {
        dayButtons.forEach(button => {
            button.addEventListener('click', function() {
                const dayNumber = this.textContent.replace('Day ', '');
                const targetDayContent = document.getElementById(`day-${dayNumber}`);

                dayButtons.forEach(btn => btn.classList.remove('active'));
                dayContents.forEach(content => content.classList.remove('active'));

                this.classList.add('active');
                if (targetDayContent) {
                    targetDayContent.classList.add('active');
                }
            });
        });
    }
}

/**
 * Initialize shopping list filters
 */
function initShoppingFilters() {
    const filterButtons = document.querySelectorAll('.filter-button');
    const shoppingItems = document.querySelectorAll('.shopping-item');

    if (filterButtons.length > 0 && shoppingItems.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                const category = this.getAttribute('data-filter');

                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                if (category === 'all') {
                    shoppingItems.forEach(item => item.style.display = 'flex');
                } else {
                    shoppingItems.forEach(item => {
                        if (item.getAttribute('data-category') === category) {
                            item.style.display = 'flex';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }
            });
        });
    }
}

/**
 * Initialize shopping list select/deselect all buttons
 */
function initShoppingSelectButtons() {
    const selectAllBtn = document.querySelector('.select-all');
    const deselectAllBtn = document.querySelector('.deselect-all');
    const shoppingCheckboxes = document.querySelectorAll('.shopping-item input[type="checkbox"]');

    if (selectAllBtn && deselectAllBtn && shoppingCheckboxes.length > 0) {
        selectAllBtn.addEventListener('click', function() {
            shoppingCheckboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });

        deselectAllBtn.addEventListener('click', function() {
            shoppingCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        });
    }
}

/**
 * Initialize cooking timer functionality
 */
function initCookingTimer() {
    const timerStart = document.querySelector('.timer-start');
    const timerReset = document.querySelector('.timer-reset');
    const timerTime = document.querySelector('.timer-time');

    if (timerStart && timerReset && timerTime) {
        let timerInterval;
        let seconds = 0;
        let timerRunning = false;

        timerStart.addEventListener('click', function() {
            if (timerRunning) {
                // Pause timer
                clearInterval(timerInterval);
                timerStart.textContent = 'Resume';
                timerRunning = false;
            } else {
                // Start or resume timer
                timerInterval = setInterval(function() {
                    seconds++;
                    updateTimerDisplay();
                }, 1000);

                timerStart.textContent = 'Pause';
                timerRunning = true;
            }
        });

        timerReset.addEventListener('click', function() {
            clearInterval(timerInterval);
            seconds = 0;
            updateTimerDisplay();
            timerStart.textContent = 'Start Timer';
            timerRunning = false;
        });

        function updateTimerDisplay() {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            timerTime.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
    }
}

/**
 * Initialize bookmark and share buttons
 */
function initActionButtons() {
    const bookmarkBtn = document.querySelector('.bookmark-btn');
    const shareBtn = document.querySelector('.share-btn');

    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            const icon = this.querySelector('i');

            if (icon.classList.contains('far')) {
                // Not bookmarked -> bookmark
                icon.classList.remove('far');
                icon.classList.add('fas');
                showToast('Success', 'Added to your favorites', 'success');
            } else {
                // Bookmarked -> remove bookmark
                icon.classList.remove('fas');
                icon.classList.add('far');
                showToast('Success', 'Removed from your favorites', 'success');
            }
        });
    }

    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            if (navigator.share) {
                navigator.share({
                    title: document.querySelector('.content-title').textContent,
                    url: window.location.href
                })
                .then(() => showToast('Success', 'Shared successfully', 'success'))
                .catch(() => showToast('Info', 'Sharing canceled', 'info'));
            } else {
                // Fallback for browsers without Web Share API
                const tempInput = document.createElement('input');
                document.body.appendChild(tempInput);
                tempInput.value = window.location.href;
                tempInput.select();
                document.execCommand('copy');
                document.body.removeChild(tempInput);
                showToast('Success', 'Link copied to clipboard', 'success');
            }
        });
    }

    // Initialize other action buttons
    const shoppingListBtns = document.querySelectorAll('.shopping-list-btn');
    const calendarBtns = document.querySelectorAll('.calendar-btn');

    shoppingListBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            showToast('Success', 'Added to your shopping list', 'success');
        });
    });

    calendarBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            showToast('Success', 'Added to your calendar', 'success');
        });
    });
}

/**
 * Initialize checkboxes for ingredients and shopping list
 */
function initCheckboxes() {
    const ingredientCheckboxes = document.querySelectorAll('.ingredient-check input[type="checkbox"]');

    ingredientCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const ingredientItem = this.closest('.ingredient-item');
            if (this.checked) {
                ingredientItem.classList.add('checked');
            } else {
                ingredientItem.classList.remove('checked');
            }
        });
    });
}

/**
 * Show toast notification
 */
function showToast(title, message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');

    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';

    // Set toast content based on type
    let iconClass = 'info';
    if (type === 'success') iconClass = 'check';
    if (type === 'error') iconClass = 'exclamation-triangle';

    toast.innerHTML = `
        <div class="toast-icon ${type}">
            <i class="fas fa-${iconClass}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <p class="toast-message">${message}</p>
        </div>
        <div class="toast-close">
            <i class="fas fa-times"></i>
        </div>
    `;

    // Add to container
    toastContainer.appendChild(toast);

    // Add close event
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', function() {
        toast.classList.add('hide');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 300);
    });

    // Auto close after 5 seconds
    setTimeout(() => {
        if (toastContainer.contains(toast)) {
            toast.classList.add('hide');
            setTimeout(() => {
                if (toastContainer.contains(toast)) {
                    toastContainer.removeChild(toast);
                }
            }, 300);
        }
    }, 5000);
}