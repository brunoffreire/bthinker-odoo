$(document).ready(function () {
  $("#busca_relatorio").on("click", function (e) {
    searchReport(0);
  });
});

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
