document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form');

  form.addEventListener('submit', function (event) {
    setTimeout(function() {
      const buttons = form.getElementsByTagName('button');
      for(let i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
      }
    });
  });
});
