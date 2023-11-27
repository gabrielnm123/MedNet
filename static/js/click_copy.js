function copiarValor(btn) {
  var valor = btn.value;
  var inputTemporario = document.createElement("input");
  inputTemporario.value = valor;
  document.body.appendChild(inputTemporario);
  inputTemporario.select();
  document.execCommand("copy");
  document.body.removeChild(inputTemporario);
  alert("Valor copiado: " + valor);
}
