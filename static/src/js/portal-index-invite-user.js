$(document).ready(function () {

  $("#btn_invite_user").click(function () {
    data = {
      contrato_convite_id: $("#contrato_convite_id").val(),
    };
    callServer("save_new_user_invite", data, save_new_user_invite_callback);
  });

  function save_new_user_invite_callback(data) {
    if (data.result.errno != "0") {
      Swal.fire({
        title: "Erro",
        text: data.result.message,
        icon: "error",
      });
      return;
    }

    share(
      "Convite para Cadastro",
      "Este é o seu link de cadastro do sistema de automação de portaria.\n\n" +
        "Validade do link: " +
        data.result.date +
        ".\n\n",
      data.result.url,
      null
    );
    
  }
  

 
});
