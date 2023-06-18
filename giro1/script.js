// Получение вопроса из GET-запроса
const urlParams = new URLSearchParams(window.location.search);
const question = urlParams.get('question') || 'null';

// Обработка нажатия на круги
let leftPressed = false;
let rightPressed = false;

// Угол наклона для ответа
let posAngle = 15;
let negAngle = -15;

// Начальное положение устройства
let initialBeta = null;

// Флаг для отслеживания, когда ответ был зафиксирован
let answerRecorded = false;

document.getElementById('leftCircle').addEventListener('touchstart', function() {
    this.style.backgroundColor = 'green';
    leftPressed = true;
    initialBeta = null; // Сброс начального положения при каждом нажатии
});
document.getElementById('leftCircle').addEventListener('touchend', function() {
    this.style.backgroundColor = 'red';
    leftPressed = false;
});
document.getElementById('rightCircle').addEventListener('touchstart', function() {
    this.style.backgroundColor = 'green';
    rightPressed = true;
    initialBeta = null; // Сброс начального положения при каждом нажатии
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
    if (leftPressed && rightPressed && !answerRecorded) {
        if (initialBeta === null) {
            initialBeta = event.beta; // Задаем начальное положение при первом нажатии
        }

        let deltaBeta = event.beta - initialBeta;

        if (deltaBeta > posAngle) {
            console.log('Положительно');
            answerRecorded = true;
        } else if (deltaBeta < negAngle) {
            console.log('Отрицательно');
            answerRecorded = true;
        }

        // Если ответ был зафиксирован, скрываем все элементы и показываем график
        if (answerRecorded) {
            document.querySelector('.container').style.display = 'none';
            document.getElementById('header').style.display = 'none';
            document.getElementById('chart').style.display = 'block';
        } else {
            // Если ответ еще не был зафиксирован, продолжаем собирать данные
            chart.data.labels.push(new Date().toLocaleTimeString());
            chart.data.datasets[0].data.push(deltaBeta);
            chart.update();
        }
    }
});
