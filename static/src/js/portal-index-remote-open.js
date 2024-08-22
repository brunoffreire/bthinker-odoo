$(document).ready(function () {

  $(".button-door-offline").on("click", function (e) {
    Swal.fire({
      title: "Aviso",
      text: "Porta indisponível no momento.",
      icon: "warning",
    });
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
});

function openByHolding(obj) {
  data = {
    door: $(obj).attr("data-value"),
    method: "remoto",
  };

  callServer("auth_user_door", data, openByHolding_callback, obj);
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
