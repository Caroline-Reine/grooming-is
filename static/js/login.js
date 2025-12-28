const loginBtn = document.getElementById("loginBtn");
const errorEl = document.getElementById("error");

loginBtn.onclick = async () => {
    const login = document.getElementById("login").value.trim();
    const password = document.getElementById("password").value.trim();
    localStorage.setItem("login_time", Date.now());

    errorEl.innerText = "";

    if (!login || !password) {
        errorEl.innerText = "Введите логин и пароль";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                username: login,
                password: password,
            }),
        });

        if (!response.ok) {
            throw new Error("auth_error");
        }

        const data = await response.json();
        localStorage.setItem("token", data.access_token);

        window.location.href = "/static/index.html";
    } catch (e) {
        errorEl.innerText = "Неверный логин или пароль";
    }
};
