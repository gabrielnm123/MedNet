$(document).ready(function() {
  $('#form').on('keypress', function(e) {
    if (e.keyCode == 13) {
      e.preventDefault();
      $('.click').click();
    }
  });
});
