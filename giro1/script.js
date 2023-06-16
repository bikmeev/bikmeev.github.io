// Получение вопроса из GET-запроса
const urlParams = new URLSearchParams(window.location.search);
const question = urlParams.get('question');

// Установка вопроса на странице
document.querySelector('.question').textContent = question;

// Обработка нажатия на круги
document.getElementById('leftCircle').addEventListener('touchstart', function() {
    this.style.backgroundColor = 'green';
});
document.getElementById('leftCircle').addEventListener('touchend', function() {
    this.style.backgroundColor = 'red';
});
document.getElementById('rightCircle').addEventListener('touchstart', function() {
    this.style.backgroundColor = 'green';
});
document.getElementById('rightCircle').addEventListener('touchend', function() {
    this.style.backgroundColor = 'red';
});

// Проверка ориентации устройства
window.addEventListener('deviceorientation', function(event) {
    if (Math.abs(event.beta) > 45 || Math.abs(event.gamma) > 45) {
        document.querySelector('.question').textContent = 'Переверните телефон в горизонтальное положение';
    } else {
        document.querySelector('.question').textContent = question;
    }
});

// Создание графика
const ctx = document.getElementById('chart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Угол наклона',
            data: [],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    }
});

// Сбор данных с гироскопа
window.addEventListener('deviceorientation', function(event) {
    chart.data.labels.push(new Date().toLocaleTimeString());
    chart.data.datasets[0].data.push(event.gamma);
    chart.update();
});

