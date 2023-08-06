let tg = window.Telegram.WebApp;
let idTg = tg.initDataUnsafe.user.id;

function showQuestion() {
    hideAll();
    document.getElementById('question').style.display = 'block';
}

function showProfile() {
    hideAll();
    document.getElementById('profile').style.display = 'block';
}

function hideAll() {
    document.getElementById('question').style.display = 'none';
    document.getElementById('profile').style.display = 'none';
}

function sendEmail() {
    window.location.href = "mailto:support@example.com";
}
