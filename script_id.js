document.addEventListener('DOMContentLoaded', (event) => {
    let tg = window.Telegram.WebApp;
    let idTg = tg.initDataUnsafe.user.id;
});

function showLayer(layerId) {
    hideAll();
    if (layerId === 'menu') {
        document.getElementById('menu').style.display = 'flex';
    } else {
        document.getElementById(layerId).style.display = 'block';
    }
}

function hideAll() {
    document.getElementById('question').style.display = 'none';
    document.getElementById('profile').style.display = 'none';
    // Меню больше не скрывается
}

function sendEmail() {
    window.location.href = "mailto:support@example.com";
}
