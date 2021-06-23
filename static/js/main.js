function loading() {
  document.getElementById("loading").style.display = "none";
}
function mySubmit(id) {
  document.getElementById(id).submit();
}

function myremoveSubmit(id) {
  var input = document.createElement("input");
  input.setAttribute("value", "True");
  input.setAttribute("type", "hidden");
  input.setAttribute("name", "product_remove");
  var parent = document.getElementById(id);
  parent.appendChild(input);
  document.getElementById(id).submit();
}

$(document).ready(function () {
  // MDB Lightbox Init
  $(function () {
    $("#mdb-lightbox-ui").load("mdb-addons/mdb-lightbox-ui.html");
  });
});
