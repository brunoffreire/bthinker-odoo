   
// Setup the QR Scanner when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    window.getKey = function(){
        let params = new URLSearchParams(window.location.search);
        let key = params.get("key");
        return key;

    }  
  });