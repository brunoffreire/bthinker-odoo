$(document).ready(function () {
  init_page_controls();
});

function openMenu() {
  $("#sideMenu").css("left", "0");
}

function closeMenu() {
  $("#sideMenu").css("left", "-250px");
}

function showPage(index) {
  $(".index-page").removeClass("selected");
  $(`.index-page[page-index='${index}']`).addClass("selected");

  stopQRCamera();
  if (index == 0) {
    startQRCamera();
  }

  if (index == 2) {
    $("#camera_id").change();
  }

  closeMenu();
}
function stopQRCamera() {
  if (window.scanner) {
    window.scanner.stopCamera();
  }
  $("#canvas-container").empty();
}

function startQRCamera() {
  $("#canvas-container").empty();
  var canvas = $("<canvas>", {
    id: "canvas",
  });
  $("#canvas-container").append(canvas);

  let scanner = new QRScanner("canvas", sendDoorRequest);
  scanner.initCamera();
  window.scanner = scanner;
}

function init_page_controls() {
  $(".menu-item").on("click", function (e) {
    showPage($(this).attr("page-index"));
  });

  

  if ($(".index-page[page-index='0']").hasClass("selected")) {
    startQRCamera();
  }
}

function sendDoorRequest(door) {
  if (door == "") {
    return;
  }

  let data = { door: door, method: "qrcode" };
  callServer("auth_user_door", data, sendDoorRequest_callback);
}

function sendDoorRequest_callback(data) {
  $("#mensagem").text(data.result.message);
}