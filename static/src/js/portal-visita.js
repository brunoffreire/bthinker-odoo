// Setup the QR Scanner when the DOM is fully loaded

function sendDoorRequest(door) {
  if (door == "") {
    return;
  }

  let params = new URLSearchParams(window.location.search);
  let key = params.get("key");

  let data = { door: door, key: key, method: "qrcode" };
  callServer("auth_key_door", data, sendDoorRequest_callback);
}

function sendDoorRequest_callback(data) {
  $("#mensagem").text(data.result.message);
}

document.addEventListener("DOMContentLoaded", function () {
  const scanner = new QRScanner("canvas", sendDoorRequest);
  scanner.initCamera();
});
