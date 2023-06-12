window.onload = function () {
  var el = document.getElementById('on_hand');
  var on_table = document.getElementById('on_table');

  var sortable = Sortable.create(el, {
    group: 'shared', 
    animation: 150,
    onEnd: function (evt) {
      if (on_table.childElementCount > 6) {
        evt.from.appendChild(evt.item);
      }
      updateCardPositions();
    },
  });

  Sortable.create(on_table, {
    group: 'shared',
    onEnd: function (evt) {
      updateCardPositions();
    },
  });

  var angleStep = 15; // угол наклона каждой следующей карты в веере

  function updateCardPositions() {
    var cardsInHand = document.querySelectorAll('#on_hand .card');
    var totalCardsInHand = cardsInHand.length;

    cardsInHand.forEach(function (card, index) {
      var angle = angleStep * (index - (totalCardsInHand - 1) / 2);
      var offset = (index - (totalCardsInHand - 1) / 2) * 30;
      var initialTransform = `translateX(${offset}px) rotate(${angle}deg)`; // Save this for later use

      card.style.transform = initialTransform;

      card.addEventListener('touchstart', function () {
        this.style.transform = initialTransform + ' scale(1.2)';
        this.style.zIndex = '100';
      });

      card.addEventListener('touchend', function () {
        this.style.transform = initialTransform + ' scale(1)';
        this.style.zIndex = '';
      });

      // Ensure touchmove event doesn't interfere
      card.addEventListener('touchmove', function(e) {
        e.preventDefault();
      });
    });
  }


  updateCardPositions();
};
