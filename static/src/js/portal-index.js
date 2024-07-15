// Setup the QR Scanner when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
  $("#btn_new_visit").click(function () {
    data = {
      nome_visitante: $("#nome_visitante").val(),
      duracao: $("#duracao").val(),
      usa_uma_vez: $("#usa_uma_vez").is(":checked") ? "1" : "0",
    };
    callServer("save_new_visit", data, save_new_visit_callback);
  });

  window.getKey = function () {
    let key = localStorage.getItem("key");
    return key;
  };

  window.doorRequestCallback = function (data) {
    $("#mensagem").text(data.result.message);
  };

});

function save_new_visit_callback(data) {
  if (data.result.errno != "0") {
    alert(data.result.message);
    return;
  }
  share(
    "Liberação de Acesso",
    "Olá " +
      data.result.visitor +
      ".\n" +
      "Este é o seu link de acesso para sua visita a " +
      data.result.user +
      ".\n" +
      "Quando chegar ao local, abra o link e aponte a câmera para o QRCode localizado ao lado da porta.\n\n",
    data.result.url,
    visit_share_callback
  );
}

function visit_share_callback() {
  $("#nome_visitante").val("");
  $("#duracao").val("");
  $("#usa_uma_vez").prop("checked", false);
}

function showPage(index) {
  $("#page_0").addClass("d-none");
  $("#page_1").addClass("d-none");
  $("#page_2").addClass("d-none");
  $("#page_" + index).removeClass("d-none");
}

function openByPin(obj) {
  var pin = prompt("Informe seu PIN numérico:");
  if (pin === null || pin === "") {
    return;
  }

  data = {
    key: window.getKey(),
    door: $(obj).attr("data-value"),
    pin: pin,
  };

  callServer("open_door_by_pin", data, openByPin_callback);
}

function openByPin_callback(data) {
  if (data.result.errno != "0") {
    alert(data.result.message);
    return;
  }

  alert("Porta aberta.");
}
