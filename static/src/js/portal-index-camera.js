$(document).ready(function () {
  $("#camera_id").change(function () {
    var guid = $(this).val();
    requestCameraDoorList(guid);
    requestCameraFeed(guid);
  });
});

function requestCameraDoorList(guid) {
  data = { guid: guid };
  $("#camera_buttons").empty();
  callServer("get_camera_doors", data, (data) => {
    if (data.result.errno != 0) {
      Swal.fire({
        title: "Erro",
        text: data.result.message,
        icon: "error",
      });
      return;
    }

    var html = "";
    data.result.portas.forEach((porta) => {
      html += `<div class="row">`;
      html += `<button type="button" class="button${
        porta["state"] == 1 ? "-primary" : ""
      } button-camera-${
        porta["state"] == 1 ? "online" : "offline"
      }" data-value="${porta["guid"]}">${porta["nome"]}`;
      html += `	<i class="door-button-icon fas ${
        porta["state"] == 1 ? "fa-lock-open" : "fa-ban"
      }"></i>`;
      html += `</button>`;
      html += `</div>`;
    });
    $("#camera_buttons").html(html);
    setCameraButtons();
  });
}

function setCameraButtons() {
  $(".button-camera-offline").on("click", function (e) {
    Swal.fire({
      title: "Aviso",
      text: "Porta indisponível no momento.",
      icon: "warning",
    });
  });

  $(".button-camera-online").on("mousedown touchstart", function (e) {
    e.preventDefault();

    const $button = $(this);
    let progress = 0;
    let progressInterval;

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
}

function requestCameraFeed(guid) {
  
  if (window.videoCamera !== null && window.videoCamera !== undefined) {
    window.videoCamera.stop();
    window.videoCamera = null;
  }

  $("#camera_view").empty();
  $div = $("<div>", {    
    class:"camera-container"
  }).appendTo("#camera_view");

  window.videoCamera = new VideoCamera(guid, $div);
  window.videoCamera.start();
}

class VideoCamera {
  guid;
  container;
  canvas;  
  canvasContext;
  socket;  
  timer;

  constructor(guid, container) {
    this.guid = guid;
    this.container = container;
    this.started = false;    
  }

  showMessage(html) {
    $(this.container).empty();
    $(this.container).html(`<div id="camera_label">${html}</div>`);
  }

  start() {
    
    this.showMessage("Conectando ao servidor...");
    
    let previousImageURL = null;

    this.socket = new WebSocket(
      `wss://www.bthinker.com.br:8300/camera?guid=${this.guid}`
    );
    this.socket.binaryType = "arraybuffer";

    this.socket.onopen = () => {
      this.socket.send("START");
    };

    this.socket.onmessage = (event) => {
      
      if (typeof event.data === "string") {
        const msg = JSON.parse(event.data);

        switch (msg.errno) {
          case 0: {
            
            switch (msg.message){
              case "FEED_STARTED":{
                this.showMessage("Conexão estabelecida. Aguarde...");
                this.timer = setInterval(()=>{
                  this.socket.send("NEXT");
                }, 100);
                break;
              }

              case "FEED_READY":{
                $(this.container).empty();
                this.canvas = $("<canvas>", {
                  id: "videoCanvas",
                }).appendTo($(this.container));

                this.canvasContext = this.canvas[0].getContext("2d");                
                break;

              }

            }

            break;
          }

          case 1: {
            //this.showMessage(msg.message);
            this.stop();
            break;
          }

        }
        return;
      } 

      if (event.data instanceof ArrayBuffer) {
        const blob = new Blob([event.data], { type: "image/jpeg" });
        const img = new Image();

        img.onload = () => {
          this.canvasContext.drawImage(
            img,
            0,
            0,
            img.naturalWidth,
            img.naturalHeight,
            0,
            0,
            img.naturalWidth,
            img.naturalHeight*0.85
          );

          if (previousImageURL) {
            URL.revokeObjectURL(previousImageURL);
          }

          previousImageURL = img.src;
        };
        img.src = URL.createObjectURL(blob);
      }
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket Error: ", error);
    };

    this.socket.onclose = () => {
      clearInterval(this.timer);
      this.showMessage(`Conexão com servidor encerrada.<br/><br/><a href="javascript:requestCameraFeed('${this.guid}')">Tentar novamente</a>`);
      if (previousImageURL) {
        URL.revokeObjectURL(previousImageURL);
      }
    };
  }

  stop() {
    clearInterval(this.timer);
    if(this.socket !== null && this.socket !== undefined){
      this.socket.close();
    }
    this.socket = null;
  }
}
