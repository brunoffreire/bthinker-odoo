// URL da API que retorna dados em formato JSON

class QRScanner {
  constructor(canvasId, callback_method = null) {
    this.video = document.createElement("video");
    this.canvasElement = document.getElementById(canvasId);
    this.canvas = this.canvasElement.getContext("2d", {
      willReadFrequently: true,
    });
    this._wait = false;
    this._callback_method = callback_method;
  }

  initCamera() {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then((stream) => {
        this.video.srcObject = stream;
        this.video.setAttribute("playsinline", true); // iOS Safari fullscreen avoidance
        this.video.play();
        requestAnimationFrame(this.tick.bind(this));
      })
      .catch((error) => {
        console.error("Error accessing the camera:", error);
      });
  }

  //Bruno F.
  stopCamera() {
    if (this.video.srcObject) {
      this.video.srcObject = null;
    }

    if (this.stream) {
      this.stream.getTracks().forEach((track) => {
        track.stop();
      });
      this.stream = null;
    }    
  }

  drawLine(begin, end, color) {
    this.canvas.beginPath();
    this.canvas.moveTo(begin.x, begin.y);
    this.canvas.lineTo(end.x, end.y);
    this.canvas.lineWidth = 4;
    this.canvas.strokeStyle = color;
    this.canvas.stroke();
  }

  tick() {
    if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
      this.canvasElement.height = this.video.videoHeight;
      this.canvasElement.width = this.video.videoWidth;
      this.canvas.drawImage(
        this.video,
        0,
        0,
        this.canvasElement.width,
        this.canvasElement.height
      );

      let imageData = this.canvas.getImageData(
        0,
        0,
        this.canvasElement.width,
        this.canvasElement.height
      );

      let code = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: "dontInvert",
      });

      if (code && !this._wait) {
        if (typeof code.data === "string") {
          if (code.data.trim().length > 0) {
            this._wait = true;
            setTimeout(() => (this._wait = false), 3000);
            if(this._callback_method!=null){
              this._callback_method(code.data);
            }
          }
        }
      }
    }
    requestAnimationFrame(this.tick.bind(this));
  }  
}

