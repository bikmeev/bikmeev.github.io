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
    animation: 150,
    onEnd: function (evt) {
      updateCardPositions();
      // Log the position of the moved card
      if (evt.from === el) {
        var index = Array.from(on_table.children).indexOf(evt.item);
        console.log(`Card ${evt.item.innerText} is in cell ${index + 1}`);
      }
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

    var cardsOnTable = document.querySelectorAll('#on_table .card');
    var totalCardsOnTable = cardsOnTable.length;

    cardsOnTable.forEach(function(card, index) {
      var offsetX = (index % 3 - (totalCardsOnTable - 1) % 3 / 2) * 160; // Reduce offset to decrease distance between cards
      var offsetY = Math.floor(index / 3) * 260; // Reduce offset to decrease distance between cards
      card.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
    });
  }

  updateCardPositions();
};
