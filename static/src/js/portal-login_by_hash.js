document.addEventListener("DOMContentLoaded", (event) => {
  
  function init() {
    let user = localStorage.getItem("user");
    let hash = localStorage.getItem("hash");
    let key = localStorage.getItem("key");

    data = {
        'user':user,
        'hash':hash,
        'key':key
    };
    
    callServer('do_hash_login', data, init_callback);
  }

  function init_callback(data){
    var location = window.location.href;
    var url = location.substring(0, location.lastIndexOf("/") + 1);

    if(data.result.errno != '0'){
        redirect(url + '/login');
        return;
    }
    redirect(url);
  }

  init();
});
