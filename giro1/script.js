// Сбор данных с гироскопа
window.addEventListener('deviceorientation', function(event) {
    if (leftPressed && rightPressed && currentPosition === "не ответил") {
        if (initialBeta === null) {
            initialBeta = event.beta; // Задаем начальное положение при первом нажатии
        }

        let deltaBeta = event.beta - initialBeta;

        // Записываем данные только если устройство находится в позиции "не ответил"
        chart.data.labels.push(new Date().toLocaleTimeString());
        if (deltaBeta > posAngle) {
            currentPosition = "положительно";
            answerTime = Date.now();
            console.log('Положительно');

        } else if (deltaBeta < negAngle) {
            currentPosition = "отрицательно";
            answerTime = Date.now();
            console.log('отрицательно');
        }
    } else if (answerTime && Date.now() - answerTime > 1000 && answerRecorded == false) {
        // Если устройство вернулось в позицию "не ответил", фиксируем ответ
        console.log('ответ зафиксирован');
        answerRecorded = true;
        setTimeout(function() {
            document.querySelector('.container').style.display = 'none';
            document.getElementById('header').style.display = 'none';
            document.getElementById('chart').style.display = 'block';
            document.getElementById('chart').style.visibility = 'visible'; // Изменено
            document.getElementById('chart').style.height = 'auto'; // Добавлено
            chart.update(); // Обновляем график
        }, 0);
    }
});
