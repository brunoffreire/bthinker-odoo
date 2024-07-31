document.addEventListener("DOMContentLoaded", (event) => {
  hash_login();
});

function openMenu() {
  $("#sideMenu").css("left", "0");
}

function closeMenu() {
  $("#sideMenu").css("left", "-250px");
}

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
  $(".button-door-offline").on("click", function (e) {
    Swal.fire({
      title: "Aviso",
      text: "Porta indisponível no momento.",
      icon: "warning",
    });
  });

  $("#busca_relatorio").on("click", function (e) {
    searchReport(0);
  });

  $(".button-door-online").on("mousedown touchstart", function (e) {
    const $button = $(this);

    let progress = 0;
    let progressInterval;

    e.preventDefault();

    progressInterval = setInterval(function () {
      progress += 18;
      $button.css(
        "background",
        `linear-gradient(to right, green ${progress}%, #33C3F0 ${progress}%)`
      );

      if (progress >= 100) {
        clearInterval(progressInterval);
        openByHolding($button);
        $button.css(
          "background",
          "linear-gradient(to right, green 100%, #33C3F0 100%)"
        );
      }
    }, 500);

    $button.on(
      "mouseup mouseleave touchend touchcancel",
      function resetButton() {
        clearInterval(progressInterval);
        $button.css(
          "background",
          "linear-gradient(to right, green 0%, #33C3F0 0%)"
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

  showPage(1);
}

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
  $("#page_4").addClass("d-none");
  $("#page_" + index).removeClass("d-none");

  if (index == 0) {
    $("#canvas-container").empty();
    var canvas = $("<canvas>", {
      id: "canvas",
    });
    $("#canvas-container").append(canvas);

    let scanner = new QRScanner("canvas", sendDoorRequest);
    scanner.initCamera();
    window.scanner = scanner;
  } else {
    if (window.scanner) {
      window.scanner.stopCamera();
    }
    $("#canvas-container").empty();
  }

  closeMenu();
}

function sendDoorRequest(door) {
  if (door == "") {
    return;
  }

  let key = localStorage.getItem("key");
  let data = { door: door, key: key, method: "qrcode" };
  callServer("auth_key_door", data, sendDoorRequest_callback);
}

function sendDoorRequest_callback(data) {
  $("#mensagem").text(data.result.message);
}

function openByHolding(obj) {
  data = {
    key: localStorage.getItem("key"),
    door: $(obj).attr("data-value"),
    method: "remoto",
  };

  callServer("auth_key_door", data, openByHolding_callback, obj);
}

function openByHolding_callback(data, obj) {
  $(obj).css("background", "linear-gradient(to right, green 0%, #33C3F0 0%)");

  if (data.result.errno != "0") {
    Swal.fire({
      title: "Erro",
      text: data.result.message,
      icon: "error",
    });
    return;
  }

  Swal.fire({
    title: "Informação",
    text: "Porta aberta.",
    icon: "success",
  });
}

function searchReport(report_page) {
  data = {
    contrato_relatorio: $("#contrato_relatorio").val(),
    periodo_relatorio: $("#periodo_relatorio").val(),
    nome_relatorio: $("#nome_relatorio").val(),
    page: report_page,
  };

  callServer("search_report_records", data, searchReport_callback, report_page);
}

function searchReport_callback(data, report_page) {
  if (data.result.errno != 0) {
    $("#last-access-records").text(data.result.message);
    return;
  }

  $("#last-access-records").height(
    $(window).height() - $("#last-access-records").offset().top - 30
  );

  var divContainer = $("#last-access-records");

  // Se a tabela não existir, crie-a
  if ($("#report-table").length === 0) {
    var table = $("<table>").attr("id", "report-table");
    var thead = $("<thead>");
    var headerRow = $("<tr>");
    headerRow.append($("<th>").text("Informações"));
    headerRow.append($("<th>").text("Data e Hora"));
    thead.append(headerRow);
    table.append(thead);
    table.append($("<tbody>"));
    divContainer.append(table);
  } else {
    var table = $("#report-table");
  }

  var tbody = table.find("tbody");
  if (report_page === 0) {
    tbody.empty();
  }  

  data.result.data.forEach(function (item) {
    var row = $("<tr>");
    row.append(
      $("<td>").html(
        "<span class='nome'>" +
          item.nome +
          "</span><br>" +
          "<span class='porta'>" +
          item.porta +
          "</span><br>" +
          "<span class='metodo'>" +
          item.metodo +
          "</span>"
      )
    );
    row.append(
      $("<td>").html(
        "<span class='data'>" +
          item.data +
          "</span><br>" +
          "<span class='hora'>" +
          item.hora +
          "</span><br>" +
          "<span class='resultado'>" +
          item.resultado +
          "</span>"
      )
    );
    tbody.append(row);
  });

  divContainer.off("scroll").on("scroll", function () {
    if (
      divContainer.scrollTop() + divContainer.innerHeight() >=
      divContainer[0].scrollHeight
    ) {
      if (data.result.count <= 0) {
        return;
      }

      report_page++;
      searchReport(report_page);
    }
  });
}
