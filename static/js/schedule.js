console.log("schedule.js LOADED");
const LOGIN_TIME_KEY = "login_time";
const MAX_SESSION = 3 * 60 * 60 * 1000; // 3 часа

const loginTime = localStorage.getItem(LOGIN_TIME_KEY);
if (!loginTime || Date.now() - loginTime > MAX_SESSION) {
    localStorage.clear();
    window.location.href = "/static/login.html";
}

/* ===================== CONFIG ===================== */
const API_BASE = "http://127.0.0.1:8000";

/* ===================== AUTH ===================== */
const token = localStorage.getItem("token");
if (!token) {
    window.location.href = "/static/login.html";
}

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
const saveOrderBtn = document.getElementById("saveOrderBtn");
const formError = document.getElementById("formError");

const hourSelect = document.getElementById("hourSelect");
const minuteSelect = document.getElementById("minuteSelect");

const masterFilter = document.getElementById("masterFilter");
const masterSelect = document.getElementById("masterSelect");

const userNameEl = document.getElementById("userName");
const userRoleEl = document.getElementById("userRole");
const logoutBtn = document.getElementById("logoutBtn");

const phoneInput = document.getElementById("phoneInput");
const clientNameInput = document.getElementById("clientNameInput");
const petNameInput = document.getElementById("petNameInput");
const speciesSelect = document.getElementById("speciesSelect");
const breedSelect = document.getElementById("breedSelect");
const sizeSelect = document.getElementById("sizeSelect");
const ageGroupSelect = document.getElementById("ageGroupSelect");
const serviceSelect = document.getElementById("serviceSelect");
const priceInput = document.getElementById("priceInput");
const orderDateInput = document.getElementById("orderDate");
const commentInput = document.getElementById("commentInput");

function capitalizeInput(el) {
    el.addEventListener("input", () => {
        if (!el.value) return;
        el.value = el.value.charAt(0).toUpperCase() + el.value.slice(1);
    });
}

[
    clientNameInput,
    petNameInput,
    commentInput
].forEach(el => el && capitalizeInput(el));


/* ===================== STATE ===================== */
let currentView = "week";
let currentDate = new Date();
let orders = [];
let masters = [];
let services = [];
let breeds = [];
let ageGroups = [];
let tariffs = [];

/* ===================== CONSTANTS ===================== */
const roleMap = {
    admin: "Администратор",
    manager: "Руководитель",
    master: "Мастер"
};

const hours = [];
for (let h = 9; h <= 19; h++) {
    hours.push(`${String(h).padStart(2, "0")}:00`);
}

const daysShort = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
const months = [
    "января","февраля","марта","апреля","мая","июня",
    "июля","августа","сентября","октября","ноября","декабря"
];

/* ===================== HELPERS ===================== */
function startOfWeek(date) {
    const d = new Date(date);
    const day = d.getDay() || 7;
    d.setDate(d.getDate() - day + 1);
    return d;
}

function toISODate(date) {
    return date.toISOString().split("T")[0];
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

function capitalizeInput(input) {
    input.addEventListener("input", () => {
        input.value = input.value.charAt(0).toUpperCase() + input.value.slice(1);
    });
}

function calculatePrice() {
    priceInput.value = "";

    if (!serviceSelect.value || !sizeSelect.value || !ageGroupSelect.value) {
        return;
    }

    const tariff = tariffs.find(t =>
        String(t.service_id) === serviceSelect.value &&
        t.size === sizeSelect.value
    );

    if (!tariff) return;

    const age = ageGroups.find(a => String(a.id) === ageGroupSelect.value);
    if (!age) return;

    const finalPrice = Math.round(
        tariff.price * age.price_factor / 100
    );

    priceInput.value = finalPrice;
}


/* ===================== API ===================== */
function apiGet(url) {
    return fetch(`${API_BASE}${url}`, {
        headers: { Authorization: `Bearer ${token}` }
    }).then(r => {
        if (!r.ok) throw new Error(r.status);
        return r.json();
    });
}

/* ===================== USER ===================== */
function loadUser() {
    apiGet("/auth/me").then(data => {
        currentUser = data;

        userNameEl.innerText = data.full_name;

        userRoleEl.innerText =
            data.role === "admin" ? "Администратор" :
            data.role === "manager" ? "Руководитель" :
            "Мастер";

        applyRoleRules();
    });
}

function applyRoleRules() {
    if (!currentUser) return;

    // МАСТЕР
    if (currentUser.role === "master") {

        // ❌ скрываем фильтр мастеров
        masterFilter.style.display = "none";

        // ❌ запрещаем создание заявок
        createBtn.style.display = "none";

        // 🔒 фиксируем мастера (он = текущий пользователь)
        masterSelect.disabled = true;

        // автоматически фильтруем расписание
        apiGet("/masters").then(data => {
            const myMaster = data.find(m =>
                m.name.toLowerCase().includes(currentUser.login.toLowerCase())
            );

            if (myMaster) {
                masterFilter.value = myMaster.id;
            }

            loadOrders();
        });
    }

    // ADMIN / MANAGER
    if (currentUser.role === "admin" || currentUser.role === "manager") {
        createBtn.style.display = "block";
        masterFilter.style.display = "block";
    }
}


logoutBtn.onclick = () => {
    localStorage.removeItem("token");
    window.location.href = "/static/login.html";
};

/* ===================== TIME ===================== */
    function initTimeSelectors() {
    hourSelect.innerHTML = "";
    minuteSelect.innerHTML = "";

     for (let h = 9; h <= 19; h++) {
        hourSelect.innerHTML += `<option>${String(h).padStart(2,"0")}</option>`;
    }
        for (let m = 0; m < 60; m += 5) {
        minuteSelect.innerHTML += `<option>${String(m).padStart(2,"0")}</option>`;
    }
}

/* ===================== MODAL ===================== */
function openModal(date = null, time = null) {
    formError.innerText = "";
    initTimeSelectors();
    if (date) orderDateInput.value = date;
    if (time) {
        const [h, m] = time.split(":");
        hourSelect.value = h;
        minuteSelect.value = m;
        }
    modal.style.display = "flex";
}

function closeModalFn() {
    modal.style.display = "none";
}

/* ===================== LOAD DATA ===================== */
function loadMasters() {
    apiGet("/masters").then(data => {
        masters = data;

        masterFilter.innerHTML = `<option value="">Все мастера</option>`;
        masterSelect.innerHTML = `<option value="">Выберите мастера</option>`;

        data.forEach(m => {
            // если мастер — показываем только себя
            if (currentUser.role === "master" && currentUser.login !== m.name) {
                return;
            }

            const opt1 = document.createElement("option");
            opt1.value = m.id;
            opt1.textContent = m.name;
            masterFilter.appendChild(opt1);

            const opt2 = document.createElement("option");
            opt2.value = m.id;
            opt2.textContent = m.name;
            masterSelect.appendChild(opt2);
        });

        // если мастер — сразу выбираем его
        if (currentUser.role === "master") {
            masterFilter.value = masterSelect.value;
        }
    });
}


function loadServices() {
    apiGet("/services").then(data => {
        services = data;
        serviceSelect.innerHTML = `<option value="">Выберите услугу</option>`;
        data.forEach(s => {
            serviceSelect.innerHTML += `<option value="${s.id}">${s.name}</option>`;
        });
    });
}

function calculatePrice() {
    priceInput.value = "";

    if (!serviceSelect.value || !sizeSelect.value || !ageGroupSelect.value) {
        return;
    }

    const tariff = tariffs.find(t =>
        String(t.service_id) === serviceSelect.value &&
        t.size === sizeSelect.value
    );

    if (!tariff) return;

    const age = ageGroups.find(a => String(a.id) === ageGroupSelect.value);
    if (!age) return;

    priceInput.value = Math.round(
        tariff.price * age.price_factor / 100
    );
}



function loadTariffs() {
    apiGet("/service-tariffs").then(data => {
        tariffs = data;
    }).catch(() => {
        tariffs = [];
    });
}

function loadBreeds() {
    apiGet("/breeds").then(data => {
        breeds = data;
        renderBreeds();
    });
}

function renderBreeds() {
    breedSelect.innerHTML = `<option value="">Выберите породу</option>`;

    breeds.forEach(b => {
        const opt = document.createElement("option");
        opt.value = b.id;
        opt.textContent = b.name;
        opt.dataset.defaultSize = b.default_size || "";
        breedSelect.appendChild(opt);
    });
}

breedSelect.onchange = () => {
    const opt = breedSelect.selectedOptions[0];
    if (opt && opt.dataset.defaultSize) {
        sizeSelect.value = opt.dataset.defaultSize;
        calculatePrice();
    }
};


function loadAgeGroups() {
    apiGet("/age-groups").then(data => {
        ageGroups = data;
        ageGroupSelect.innerHTML = `<option value="">Выберите возраст</option>`;
        data.forEach(a => {
            ageGroupSelect.innerHTML += `<option value="${a.id}">${a.name}</option>`;
        });
    });
}

/* ===================== ORDERS ===================== */
function loadOrders() {
    const from = currentView === "week"
        ? toISODate(startOfWeek(currentDate))
        : toISODate(currentDate);

    const to = currentView === "week"
        ? toISODate(new Date(startOfWeek(currentDate).getTime() + 6 * 86400000))
        : toISODate(currentDate);

    apiGet(`/orders/schedule?date_from=${from}&date_to=${to}`)
        .then(data => {
            orders = Array.isArray(data) ? data : [];
            render();
        });
}

/* ===================== RENDER ===================== */
function renderPeriodLabel() {
    periodLabel.innerText =
        currentView === "week"
            ? formatWeekRange(currentDate)
            : formatDay(currentDate);
}

function renderOrders(cell, dateISO, time) {
    const masterId = masterFilter.value;

    orders
        .filter(o =>
            o.date === dateISO &&
            o.start_time === time &&
            (!masterId || o.master_id == masterId)
        )
        .forEach(o => {
            const div = document.createElement("div");
            div.className = `order ${o.status}`;
            div.innerText =
                `${o.client_name}\n${o.pet_name}\n${o.service_name}`;
            cell.appendChild(div);
        });
}


function renderWeek() {
    const grid = document.createElement("div");
     grid.className = "schedule-grid";
    grid.appendChild(document.createElement("div"));

    daysShort.forEach(d => {
        const h = document.createElement("div");
        h.className = "schedule-header";
        h.innerText = d;
        grid.appendChild(h);
    });

    const ws = startOfWeek(currentDate);

    hours.forEach(time => {
        const t = document.createElement("div");
        t.className = "time-cell";
        t.innerText = time;
        grid.appendChild(t);

        for (let i = 0; i < 7; i++) {
        const d = new Date(ws);
        d.setDate(ws.getDate() + i);
        const dateISO = toISODate(d);

        const cell = document.createElement("div");
        cell.className = "cell";

        cell.onclick = () => {
            openModal(dateISO, time);
        };

        renderOrders(cell, dateISO, time);
        grid.appendChild(cell);
    }

    });

    scheduleEl.appendChild(grid);
}

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
            openModal();
            orderDateInput.value = toISODate(currentDate);

            const [h, m] = time.split(":");
            hourSelect.value = h;
            minuteSelect.value = m;
        };


        renderOrders(cell, toISODate(currentDate), time);
        grid.appendChild(cell);
    });

    scheduleEl.appendChild(grid);
}

    function render() {
        scheduleEl.innerHTML = "";
        renderPeriodLabel();
        currentView === "week" ? renderWeek() : renderDay();
    }

/* ===================== CONTROLS ===================== */
dayBtn.onclick = () => {
    currentView = "day";
    dayBtn.classList.add("active");
    weekBtn.classList.remove("active");
    loadOrders();
};

weekBtn.onclick = () => {
    currentView = "week";
    weekBtn.classList.add("active");
    dayBtn.classList.remove("active");
    loadOrders();
};

prevBtn.onclick = () => {
    currentDate.setDate(currentDate.getDate() + (currentView === "week" ? -7 : -1));
    loadOrders();
};

nextBtn.onclick = () => {
    currentDate.setDate(currentDate.getDate() + (currentView === "week" ? 7 : 1));
    loadOrders();
};

    closeModal.onclick = closeModalFn;
    cancelBtn.onclick = closeModalFn;
    createBtn.onclick = () => openModal();

/* ===================== SAVE ORDER ===================== */
saveOrderBtn.onclick = () => {
    const errorEl = document.getElementById("formError");
    errorEl.innerText = "";

    if (
        !phoneInput.value ||
        !clientNameInput.value ||
        !petNameInput.value ||
        !speciesSelect.value ||
        !sizeSelect.value ||
        !ageGroupSelect.value ||
        !masterSelect.value ||
        !serviceSelect.value ||
        !orderDateInput.value
    ) {
        errorEl.innerText = "Пожалуйста, заполните все обязательные поля";
        return;
    }

    const payload = {
        phone: phoneInput.value,
        full_name: clientNameInput.value,
        pet: {
            name: petNameInput.value,
            species: speciesSelect.value,
            breed_id: breedSelect.value || null,
            age_group_id: ageGroupSelect.value,
            size: sizeSelect.value,
        },
        master_id: masterSelect.value,
        service_id: serviceSelect.value,
        date: orderDateInput.value,
        start_time: `${hourSelect.value}:${minuteSelect.value}`,
        comment: commentInput.value,
    };

    fetch(`${API_BASE}/orders`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
    })
        .then(res => {
            if (!res.ok) throw new Error();
            closeModalFn();
            loadOrders();
        })
        .catch(() => {
            errorEl.innerText = "Ошибка создания заявки";
        });
};




/* ===================== INIT ===================== */
function capitalizeInput(el) {
    el.addEventListener("input", () => {
        el.value = el.value.replace(/(^|\s|-)\S/g, s => s.toUpperCase());
    });
}

capitalizeInput(clientNameInput);
capitalizeInput(petNameInput);
capitalizeInput(commentInput);

function validateForm() {
    if (!phoneInput.value) return "Введите телефон";
    if (!clientNameInput.value) return "Введите ФИО клиента";
    if (!petNameInput.value) return "Введите кличку питомца";
    if (!speciesSelect.value) return "Выберите вид";
    if (!breedSelect.value) return "Выберите породу";
    if (!sizeSelect.value) return "Выберите размер";
    if (!ageGroupSelect.value) return "Выберите возраст";
    if (!masterSelect.value) return "Выберите мастера";
    if (!serviceSelect.value) return "Выберите услугу";
    if (!orderDateInput.value) return "Выберите дату";
    if (!hourSelect.value || !minuteSelect.value) return "Выберите время";

    return null;
}



weekBtn.classList.add("active");
loadUser();
loadMasters();
loadServices();
loadBreeds();
loadAgeGroups();
loadOrders();
loadTariffs();



serviceSelect.onchange = calculatePrice;
sizeSelect.onchange = calculatePrice;
ageGroupSelect.onchange = calculatePrice;
masterFilter.onchange = loadOrders;

