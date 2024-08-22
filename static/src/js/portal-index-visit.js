$(document).ready(function () {

  $("#btn_new_visit").click(function () {
    data = {
      nome_visitante: $("#nome_visitante").val(),
      duracao: $("#duracao").val(),
      usa_uma_vez: $("#usa_uma_vez").is(":checked") ? "1" : "0",
    };
    callServer("save_new_visit", data, save_new_visit_callback);
  });

  function save_new_visit_callback(data) {
    if (data.result.errno != "0") {
      Swal.fire({
        title: "Erro",
        text: data.result.message,
        icon: "error",
      });
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
  
});
