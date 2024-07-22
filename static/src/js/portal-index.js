document.addEventListener("DOMContentLoaded", (event) => {
  hash_login();
});

function hash_login() {
  let user = localStorage.getItem("user");
  let hash = localStorage.getItem("hash");
  let auto_login = localStorage.getItem("auto_login");

  data = {
    user: user,
    hash: hash,
    auto_login: auto_login,
  };

  callServer("do_hash_login", data, hash_login_callback);
}

function hash_login_callback(data) {
  if (data.result.errno == "0") {
    $("body").html(data.result.html);
    set_index_page_controls();
    return;
  }
  redirect("/virtualkey/login");
}

function set_index_page_controls() {
  const holdTime = 2000;

  $(".button-door").on("mousedown touchstart", function (e) {
    const $button = $(this);
    let progress = 0;
    let progressInterval;

    e.preventDefault();

    progressInterval = setInterval(function () {
      progress += 100 / (holdTime / 100);
      $button.css(
        "background",
        `linear-gradient(to right, green ${progress}%, transparent ${progress}%)`
      );

      if (progress >= 100) {
        clearInterval(progressInterval);
        openByHolding($button);
        $button.css(
          "background",
          "linear-gradient(to right, green 0%, transparent 0%)"
        );
      }
    }, 100);

    $button.on(
      "mouseup mouseleave touchend touchcancel",
      function resetButton() {
        clearInterval(progressInterval);
        $button.css(
          "background",
          "linear-gradient(to right, green 0%, transparent 0%)"
        );
        $button.off("mouseup mouseleave", resetButton);
      }
    );
  });

  $("#btn_new_visit").click(function () {
    data = {
      nome_visitante: $("#nome_visitante").val(),
      duracao: $("#duracao").val(),
      usa_uma_vez: $("#usa_uma_vez").is(":checked") ? "1" : "0",
    };
    callServer("save_new_visit", data, save_new_visit_callback);
  });

  $("#btn_invite_user").click(function () {
    data = {
      contrato_convite_id: $("#contrato_convite_id").val(),
    };
    callServer("save_new_user_invite", data, save_new_user_invite_callback);
  });

  window.getKey = function () {
    let key = localStorage.getItem("key");
    return key;
  };

  window.doorRequestCallback = function (data) {
    $("#mensagem").text(data.result.message);
  };

  const scanner = new QRScanner("canvas");
  scanner.initCamera();
}

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

function save_new_user_invite_callback(data) {
  if (data.result.errno != "0") {
    alert(data.result.message);
    return;
  }
  share(
    "Convite para Cadastro",
    "Este é o seu link de cadastro do sistema de automação de portaria.\n\n" +
    "Validade do link: "+ data.result.date +".\n\n",
    data.result.url,
    null
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
  $("#page_3").addClass("d-none");
  $("#page_" + index).removeClass("d-none");

  $("a[name='btn_page']").removeClass();
  $("#btn_page_" + index).addClass("selected");
}

function openByHolding(obj) {
  data = {
    key: window.getKey(),
    door: $(obj).attr("data-value"),
  };

  callServer("auth_key_door", data, openByHolding_callback);
}

function openByHolding_callback(data) {
  if (data.result.errno != "0") {
    alert(data.result.message);
    return;
  }

  alert("Porta aberta.");
}
