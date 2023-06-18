// Получение вопроса из GET-запроса
const urlParams = new URLSearchParams(window.location.search);
const question = urlParams.get('question') || 'null';

// Обработка нажатия на круги
let leftPressed = false;
let rightPressed = false;

//угл наклона для ответа
let posAngle = 30;
let negAngle = -30;

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
function checkOrientation() {
    const container = document.querySelector('.container');
    const header = document.getElementById('header'); // Добавлено
    if (window.orientation === 0 || window.orientation === 180) {
        document.querySelector('.question').textContent = 'Переверните телефон в горизонтальное положение';
        container.style.display = 'none';
        header.style.display = 'none'; // Добавлено
    } else {
        document.querySelector('.question').textContent = question;
        container.style.display = 'block';
        header.style.display = 'flex'; // Добавлено
    }
}
setInterval(checkOrientation, 100);

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
        chart.data.datasets[0].data.push(event.beta);
        chart.update();

        if (event.beta > posAngle) {
            console.log('Положительно');
        } else if (event.beta < negAngle) {
            console.log('Отрицательно');
        }
    }
});

