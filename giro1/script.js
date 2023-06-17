// Получение вопроса из GET-запроса
const urlParams = new URLSearchParams(window.location.search);
const question = urlParams.get('question') || 'null';

// Установка вопроса на странице
document.querySelector('.question').textContent = question;

// Обработка нажатия на круги
let leftPressed = false;
let rightPressed = false;

document.getElementById('leftCircle').addEventListener('touchstart', function() {
    this.style.backgroundColor = 'green';
    leftPressed = true;
});
document.getElementById('leftCircle').addEventListener('touchend', function() {
    this.style.backgroundColor = 'red';
    leftPressed = false;
});
document.getElementById('rightCircle').addEventListener('touchstart', function() {
    this.style.backgroundColor = 'green';
    rightPressed = true;
});
document.getElementById('rightCircle').addEventListener('touchend', function() {
    this.style.backgroundColor = 'red';
    rightPressed = false;
});

// Проверка ориентации устройства
window.addEventListener('orientationchange', function() {
    const container = document.querySelector('.container');
    if (window.orientation === 0 || window.orientation === 180) {
        document.querySelector('.question').textContent = 'Переверните телефон в горизонтальное положение';
        container.style.display = 'none';
    } else {
        document.querySelector('.question').textContent = question;
        container.style.display = 'block';
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
    if (leftPressed && rightPressed) {
        chart.data.labels.push(new Date().toLocaleTimeString());
        chart.data.datasets[0].data.push(event.gamma);
        chart.update();
    }
});
