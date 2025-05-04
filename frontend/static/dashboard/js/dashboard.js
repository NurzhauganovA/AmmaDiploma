class Calendar {
    constructor(options) {
        this._locales = options.locales;
        this._calendarContainer = options.calendarContainer;
        const today = options.today ?? new Date();
        this._dateEvents = [];
        this._eventDates = [];
        this._currentYear = today.getFullYear();
        this._currentMonth = today.getMonth();
    }

    getMonthDays(month = null) {
        month ??= this.currentMonth;
        const firstDayOfMonth = new Date(month[0], month[1], 1);
        const lastDayOfMonth = new Date(month[0], month[1] + 1, 0);
        const firstWeekday = firstDayOfMonth.getDay() || 7; // Преобразуем воскресенье (0) в 7
        const lastDate = lastDayOfMonth.getDate();

        const prevMonthLastDay = new Date(month[0], month[1], 0).getDate();
        let days = [];
        let week = [];

        // Добавляем дни предыдущего месяца
        for (let i = firstWeekday - 1; i > 0; i--) {
            week.push({ date: new Date(month[0], month[1] - 1, prevMonthLastDay - i + 1), type: "previous" });
        }

        // Добавляем дни текущего месяца
        for (let day = 1; day <= lastDate; day++) {
            week.push({ date: new Date(month[0], month[1], day), type: "current" });
            if (week.length === 7) {
                days.push(week);
                week = [];
            }
        }

        // Добавляем дни следующего месяца
        let nextMonthDay = 1;
        while (week.length > 0 && week.length < 7) {
            week.push({ date: new Date(month[0], month[1] + 1, nextMonthDay++), type: "next" });
        }
        if (week.length === 7) days.push(week);

        return days;
    }

    getMonthName(month) {
        return new Date(month[0], month[1], 1).toLocaleDateString(this._locales, { year: "numeric", month: "long" })
    }

    getWeekdayNames() {
        return Array.from({ length: 7 }, (_, i) =>
            new Date(2024, 0, i + 1).toLocaleDateString(this._locales, { weekday: "long" })
        );
    }

    getDateSteps(options) {
        const step = options.step ?? 1;
        let maxCount = options.maxCount ?? 1;
        const startDate = options.startDate ?? new Date();
        let date = new Date(startDate);
        let result = [];
        while (maxCount !== 0) {
            result.push(new Date(date));
            date.setDate(date.getDate() + step);
            maxCount--;
        }

        return result;
    }

    get previousMonth() {
        const year = this._currentMonth === 0 ? this._currentYear - 1 : this._currentYear;
        const month = this._currentMonth === 0 ? 11 : this._currentMonth - 1;
        return [year, month];
    }

    get currentMonth() {
        return [this._currentYear, this._currentMonth];
    }

    set currentMonth(month) {
        [this._currentYear, this._currentMonth] = month;
    }

    get nextMonth() {
        const year = this._currentMonth === 11 ? this._currentYear + 1 : this._currentYear;
        const month = this._currentMonth === 11 ? 0 : this._currentMonth + 1;
        return [year, month];
    }

    stepPreviousMonth() {
        this.currentMonth = this.previousMonth;
        this.render();
    }

    stepNextMonth() {
        this.currentMonth = this.nextMonth;
        this.render();
    }

    setupEvents(eventDates, dateEvents) {
        this._eventDates = eventDates;
        this._dateEvents = dateEvents;
    }

    setupStepByStepEvents() {

    }

    render() {
        this._calendarContainer.innerHTML = "";
        const monthDays = this.getMonthDays(this.currentMonth);
        const monthName = this.getMonthName(this.currentMonth);
        const weekdayNames = this.getWeekdayNames();
        const calendarElement = document.createElement("div");
        calendarElement.classList.add("calendar");
        const calendarControlContainerElement = document.createElement("div");
        calendarControlContainerElement.classList.add("calendar__control-container")
        const previousMonthButtonElement = document.createElement("button");
        previousMonthButtonElement.classList.add("calendar__step-previous-month-button");
        previousMonthButtonElement.textContent = "<";
        previousMonthButtonElement.addEventListener("click", () => this.stepPreviousMonth());
        calendarControlContainerElement.appendChild(previousMonthButtonElement);
        const monthNameContainerElement = document.createElement("div");
        monthNameContainerElement.classList.add("calendar__month-name-container")
        monthNameContainerElement.textContent = monthName;
        calendarControlContainerElement.appendChild(monthNameContainerElement)
        const stepNextMonthButtonElement = document.createElement("button");
        stepNextMonthButtonElement.classList.add("calendar__step-next-month-button");
        stepNextMonthButtonElement.textContent = ">";
        stepNextMonthButtonElement.addEventListener("click", () => this.stepNextMonth());
        calendarControlContainerElement.appendChild(stepNextMonthButtonElement);

        calendarElement.appendChild(calendarControlContainerElement);
        const weekdayNamesContainerElement = document.createElement("div");
        weekdayNamesContainerElement.classList.add("calendar__weekday-names-container");
        for (const weekdayName of weekdayNames) {
            const weekdayNameElement = document.createElement("div");
            weekdayNameElement.classList.add("calendar__weekday-name");

            weekdayNameElement.textContent = weekdayName;
            weekdayNamesContainerElement.appendChild(weekdayNameElement);
        }
        calendarElement.appendChild(weekdayNamesContainerElement);
        const monthDaysContainerElement = document.createElement("div");
        monthDaysContainerElement.classList.add("calendar__month-days-container");
        for (const days of monthDays) {
            const daysContainerElement = document.createElement("div");
            daysContainerElement.classList.add("calendar__days-container");
            for (const day of days) {
                const dayElement = document.createElement("div");
                dayElement.classList.add("calendar__day");
                dayElement.dataset.dayType = day.type;
                dayElement.dataset.dayToday = day.date.toDateString() === new Date().toDateString();
                const dateContainer = document.createElement("div");
                dateContainer.classList.add("calendar__day-date");
                dateContainer.textContent = day.date.getDate();
                dayElement.append(dateContainer);
                const eventIndex = this._eventDates.findIndex(eventDate => eventDate.toDateString() === day.date.toDateString())
                if (eventIndex !== -1) {
                    const eventsContainer = document.createElement("div");
                    eventsContainer.classList.add("calendar__events-container");
                    const events = this._dateEvents[eventIndex];
                    for (const event of events) {
                        const eventElement = document.createElement("a");
                        eventElement.classList.add("calendar__event");
                        eventElement.dataset.eventColor = event.color;
                        eventElement.textContent = event.text;
                        eventElement.href = event.href;
                        eventsContainer.appendChild(eventElement);
                    }
                    dayElement.appendChild(eventsContainer);
                }
                daysContainerElement.appendChild(dayElement);
            }
            monthDaysContainerElement.appendChild(daysContainerElement);
        }
        calendarElement.appendChild(monthDaysContainerElement);
        this._calendarContainer.appendChild(calendarElement);
    }
}

const calendar = new Calendar({
    locales: "en-US",
    calendarContainer: document.getElementById("calendar-container")
});

fetch('/api/calendar-events')
.then(res => res.json())
.then(data => {
    const eventDates = data.map(event => new Date(event.date));
    const dateEvents = data.map(event => event.events);

    calendar.setupEvents(eventDates, dateEvents);
    calendar.render();
});