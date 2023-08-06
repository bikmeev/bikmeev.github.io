document.addEventListener('DOMContentLoaded', (event) => {
    let tg = window.Telegram.WebApp;
    let idTg = tg.initDataUnsafe.user.id;
});

function showLayer(layerId) {
    hideAll();
    document.getElementById(layerId).style.display = 'flex';
}

function hideAll() {
    document.getElementById('question').style.display = 'none';
    document.getElementById('profile').style.display = 'none';
    document.getElementById('menu').style.display = 'none';
}

function sendEmail() {
    window.location.href = "mailto:support@example.com";
}
