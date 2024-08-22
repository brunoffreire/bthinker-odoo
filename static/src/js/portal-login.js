function login() {
  username = $("#username").val();
  senha = $("#senha").val();

  callServer(
    "do_user_login",
    {
      username: username,
      senha: senha,
    },
    login_callback
  );
}

function login_callback(data) {
  if (data.result.errno != "0") {
    Swal.fire({
      title: "Erro",
      text: data.result.message,
      icon: "error",
    });
    return;
  }

  remember_me = $("#rememberMe").is(":checked");
  if (remember_me) {
    localStorage.setItem("user", data.result.user);
    localStorage.setItem("hash", data.result.hash);
    localStorage.setItem("auto_login", remember_me);
  }
  redirect("/virtualkey/index");
}

function change_password() {
  username = $("#username").val();
  callServer(
    "change_user_password",
    {
      username: username,
    },
    change_password_callback
  );
}

function change_password_callback(data) {
  if (data.result.errno != "0") {
    Swal.fire({
      title: "Erro",
      text: data.result.message,
      icon: "error",
    });
    return;
  }

  Swal.fire({
    title: "Sucesso",
    text: data.result.message,
    icon: "success",
  });
}

$(document).ready(function () {

  localStorage.clear();

  $("#btn_login").click(function () {
    login();
  });

  $("#btn_login, #username, #senha").keypress(function (ev) {
    if (ev.keyCode == 13) {
      login();
    }
  });

  $("#forgot_password").click(function () {
    var ok = confirm("Deseja receber um e-mail para redefinição de senha?");
    if (!ok) {
      return;
    }
    change_password();
  });
  
});
