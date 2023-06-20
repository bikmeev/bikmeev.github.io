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
let answerRecorded1 = false;
// Флаг для отслеживания, в какой позиции находится устройство
let currentPosition = "не ответил";


let answerTime = null;

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
    const chart = document.getElementById('chart'); // Добавлено
    if (window.orientation === 0 || window.orientation === 180) {
        document.querySelector('.question').textContent = 'Переверните телефон в горизонтальное положение';
        container.style.display = 'none';
        header.style.display = 'none'; // Добавлено
        chart.style.display = 'none'; // Добавлено

        chart.style.visibility = 'hidden';

    } else {
        document.querySelector('.question').textContent = question;
        container.style.display = 'block';
        header.style.display = 'flex'; // Добавлено
        chart.style.display = 'block'; // Добавлено

        //chart.style.visibility = 'hidden';

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


// Подключите библиотеку dom-to-image
// <script src="https://cdnjs.cloudflare.com/ajax/libs/dom-to-image/2.6.0/dom-to-image.min.js"></script>

function sendGraphToTelegram() {
    var node = document.getElementById('chart');

    domtoimage.toBlob(node)
        .then(function(blob) {
            var formData = new FormData();
            formData.append('chat_id', '5110225769');
            formData.append('photo', blob, 'graph.png');

            fetch('https://api.telegram.org/bot5822273239:AAEoFhjttiPIMZ0N7sVIWuVRaVAZ7FAzhG4/sendPhoto', {
                method: 'POST',
                body: formData
            })
            .then(response => console.log('Graph sent to Telegram successfully'))
            .catch(error => console.error('Error:', error));
        })
        .catch(function(error) {
            console.error('Error:', error);
        });
}


// Сбор данных с гироскопа
// Сбор данных с гироскопа
window.addEventListener('deviceorientation', function(event) {
    if (leftPressed && rightPressed && (currentPosition === "не ответил" || (answerRecorded && Date.now() - answerTime < 3000))) {
        if (initialBeta === null) {
            initialBeta = event.beta; // Задаем начальное положение при первом нажатии
        }

        let deltaBeta = event.beta - initialBeta;

        // Записываем данные только если устройство находится в позиции "не ответил"
        console.log(new Date().toLocaleTimeString(), deltaBeta);
        chart.data.labels.push(new Date().toLocaleTimeString());
        chart.data.datasets[0].data.push(deltaBeta); // Добавляем данные в график
        chart.update();

        if (deltaBeta > posAngle) {
            currentPosition = "положительно";
            answerTime = Date.now();
            console.log('Положительно');

        } else if (deltaBeta < negAngle) {
            currentPosition = "отрицательно";
            answerTime = Date.now();
            console.log('отрицательно');
        }
    } else if (currentPosition !== "не ответил" && Math.abs(event.beta - initialBeta) < 5 && answerRecorded == false) {
        // Если устройство вернулось в позицию "не ответил", фиксируем ответ
        console.log('ответ зафиксирован');
        setTimeout(function() {
            answerRecorded = true;
            sendGraphToTelegram();
        }, 1000);

        //document.querySelector('.container').style.visibility = 'hidden';            
        //document.getElementById('header').style.visibility = 'hidden';
        //document.getElementById('chart').style.visibility = 'visible'; // Изменено
        //document.getElementById('chart').style.height = '400px'; // Добавлено
        //chart.update(); // Обновляем график
 
    }
});
