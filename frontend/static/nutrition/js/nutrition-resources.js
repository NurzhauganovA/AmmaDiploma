document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('nutrition-content-grid');
    const filterPills = document.querySelectorAll('.filter-pill');
    const searchInput = document.getElementById('nutrition-search');

    // Собираем текущие параметры
    let curType = 'All', curTrimester = 'All', curSearch = '';

    // Функция рендера одной карточки по данным из JSON
    function renderCard(item) {
        return `
    <div class="content-card" data-type="${item.content_type}" data-trimester="${item.trimester}">
      <div class="card-image" style="background-image:url('${item.image_url}')">
        <span class="content-type-badge" style="background-color:${item.color_code}">
          ${item.content_type}
        </span>
        ${item.trimester !== 'all'
            ? `<span class="trimester-badge">${item.trimester}</span>`
            : ''}
      </div>
      <div class="card-content">
        <h3>${item.title}</h3>
        <div class="card-details">
          ${item.prep_time
            ? `<div class="detail-item"><i class="icon-prep-time"></i><span>${item.prep_time + item.cook_time} min</span></div>`
            : `<div class="detail-item"><i class="icon-clock"></i><span>${item.read_time} min read</span></div>`
        }
        </div>
        <div class="benefit-tags">
          ${item.benefits.map(b => `<span class="benefit-tag">${b}</span>`).join('')}
        </div>
        <a href="/nutritions/${item.id}/" class="view-more-btn">
          View Details <i class="icon-arrow-right"></i>
        </a>
      </div>
    </div>`;
    }

    // Запрос к серверу и отрисовка
    function fetchAndRender() {
        const params = new URLSearchParams({
            type: curType,
            trimester: curTrimester,
            search: curSearch
        });
        fetch(`/nutrition_filter/?${params}`, {headers: {'X-Requested-With': 'XMLHttpRequest'}})
            .then(r => r.json())
            .then(data => {
                grid.innerHTML = data.content.map(renderCard).join('') ||
                    `<p class="no-results">No items found for these filters.</p>`;
            });
    }

    // Обработчик клика по фильтрам
    filterPills.forEach(pill => {
        pill.addEventListener('click', () => {
            // Снимаем активный, ставим нажатый
            filterPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            // Определяем, какой именно фильтр это: по type или trimester
            if (pill.closest('.filter-group').querySelector('.filter-label').textContent.includes('Category')) {
                curType = pill.dataset.type;
            } else {
                curTrimester = pill.dataset.trimester;
            }

            fetchAndRender();
        });
    });

    // Поиск (отправляем запрос с задержкой 300ms)
    let searchTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        curSearch = searchInput.value.trim();
        searchTimer = setTimeout(fetchAndRender, 300);
    });

    // Инициализация
    fetchAndRender();
});