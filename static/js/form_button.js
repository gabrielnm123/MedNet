document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form');
  const button = document.getElementById('button');

  form.addEventListener('submit', function () {
    button.disabled = true;
  });
});