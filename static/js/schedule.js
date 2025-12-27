console.log("schedule.js LOADED");

/* ===================== DOM ===================== */
const scheduleEl = document.getElementById("schedule");

const dayBtn = document.getElementById("dayBtn");
const weekBtn = document.getElementById("weekBtn");

const prevBtn = document.getElementById("prevPeriod");
const nextBtn = document.getElementById("nextPeriod");
const periodLabel = document.getElementById("currentPeriod");

const modal = document.getElementById("modalOverlay");
const closeModal = document.getElementById("closeModal");
const cancelBtn = document.getElementById("cancelBtn");
const createBtn = document.getElementById("createOrderBtn");

const dateInput = document.getElementById("orderDate");
const hourSelect = document.getElementById("hourSelect");
const minuteSelect = document.getElementById("minuteSelect");

/* ===================== STATE ===================== */
let currentView = "week"; // week | day
let currentDate = new Date();

let formMode = "manual"; // manual | slot
let selectedDate = null;
let selectedTime = null;

/* ===================== TIME DATA ===================== */
const hours = [];
for (let h = 9; h <= 19; h++) {
    hours.push(`${String(h).padStart(2, "0")}:00`);
}

const daysShort = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
const months = [
    "января","февраля","марта","апреля","мая","июня",
    "июля","августа","сентября","октября","ноября","декабря"
];

/* ===================== DATE HELPERS ===================== */
function startOfWeek(date) {
    const d = new Date(date);
    const day = d.getDay() || 7;
    d.setDate(d.getDate() - day + 1);
    return d;
}

function formatWeekRange(date) {
    const start = startOfWeek(date);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return `${start.getDate()}–${end.getDate()} ${months[end.getMonth()]} ${end.getFullYear()}`;
}

function formatDay(date) {
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
}

function toISODate(date) {
    return date.toISOString().split("T")[0];
}

/* ===================== PERIOD LABEL ===================== */
function renderPeriodLabel() {
    periodLabel.innerText =
        currentView === "week"
            ? formatWeekRange(currentDate)
            : formatDay(currentDate);
}

/* ===================== TIME SELECTORS ===================== */
function initTimeSelectors() {
    if (!hourSelect || !minuteSelect) return;

    hourSelect.innerHTML = "";
    minuteSelect.innerHTML = "";

    // часы 09–19
    for (let h = 9; h <= 19; h++) {
        const opt = document.createElement("option");
        opt.value = String(h).padStart(2, "0");
        opt.textContent = String(h).padStart(2, "0");
        hourSelect.appendChild(opt);
    }

    // минуты 00,05,10…55
    for (let m = 0; m < 60; m += 5) {
        const opt = document.createElement("option");
        opt.value = String(m).padStart(2, "0");
        opt.textContent = String(m).padStart(2, "0");
        minuteSelect.appendChild(opt);
    }
}

/* ===================== MODAL ===================== */
function openModal(mode, date = null, time = null) {
    formMode = mode;
    selectedDate = date;
    selectedTime = time;

    initTimeSelectors();

    if (dateInput) {
        if (mode === "slot") {
            dateInput.value = date;
        } else {
            dateInput.value = "";
        }
    }

    if (mode === "slot" && time) {
        const [h, m] = time.split(":");
        hourSelect.value = h;
        minuteSelect.value = m;
    }

    modal.style.display = "flex";
}

function closeModalFn() {
    modal.style.display = "none";
}

/* ===================== RENDER WEEK ===================== */
function renderWeek() {
    const grid = document.createElement("div");
    grid.className = "schedule-grid";

    grid.appendChild(document.createElement("div"));

    daysShort.forEach(day => {
        const h = document.createElement("div");
        h.className = "schedule-header";
        h.innerText = day;
        grid.appendChild(h);
    });

    const weekStart = startOfWeek(currentDate);

    hours.forEach(time => {
        const t = document.createElement("div");
        t.className = "time-cell";
        t.innerText = time;
        grid.appendChild(t);

        for (let i = 0; i < 7; i++) {
            const cellDate = new Date(weekStart);
            cellDate.setDate(weekStart.getDate() + i);

            const cell = document.createElement("div");
            cell.className = "cell";
            cell.onclick = () => {
                openModal(
                    "slot",
                    toISODate(cellDate),
                    time
                );
            };
            grid.appendChild(cell);
        }
    });

    scheduleEl.appendChild(grid);
}

/* ===================== RENDER DAY ===================== */
function renderDay() {
    const grid = document.createElement("div");
    grid.className = "schedule-grid";
    grid.style.gridTemplateColumns = "80px 1fr";

    grid.appendChild(document.createElement("div"));

    const h = document.createElement("div");
    h.className = "schedule-header";
    h.innerText = "День";
    grid.appendChild(h);

    hours.forEach(time => {
        const t = document.createElement("div");
        t.className = "time-cell";
        t.innerText = time;
        grid.appendChild(t);

        const cell = document.createElement("div");
        cell.className = "cell";
        cell.onclick = () => {
            openModal(
                "slot",
                toISODate(currentDate),
                time
            );
        };
        grid.appendChild(cell);
    });

    scheduleEl.appendChild(grid);
}

/* ===================== MAIN RENDER ===================== */
function render() {
    scheduleEl.innerHTML = "";
    renderPeriodLabel();

    if (currentView === "week") {
        renderWeek();
    } else {
        renderDay();
    }
}

/* ===================== CONTROLS ===================== */
dayBtn.onclick = () => {
    currentView = "day";
    dayBtn.classList.add("active");
    weekBtn.classList.remove("active");
    render();
};

weekBtn.onclick = () => {
    currentView = "week";
    weekBtn.classList.add("active");
    dayBtn.classList.remove("active");
    render();
};

prevBtn.onclick = () => {
    currentDate.setDate(
        currentDate.getDate() + (currentView === "week" ? -7 : -1)
    );
    render();
};

nextBtn.onclick = () => {
    currentDate.setDate(
        currentDate.getDate() + (currentView === "week" ? 7 : 1)
    );
    render();
};

/* ===================== MODAL BUTTONS ===================== */
closeModal.onclick = closeModalFn;
cancelBtn.onclick = closeModalFn;

createBtn.onclick = () => {
    openModal("manual");
};

modal.onclick = e => {
    if (e.target === modal) closeModalFn();
};

/* ===================== INIT ===================== */
weekBtn.classList.add("active");
render();
