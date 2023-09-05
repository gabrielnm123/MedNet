function desativarLink(link) {
  link.classList.add("desativado");
  link.removeEventListener("click", desativarLink);
}