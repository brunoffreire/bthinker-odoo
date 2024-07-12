function login() {
    
    username = $("#username").val();
    senha = $("#senha").val();

    callServer('do_user_login', {
        'username': username,
        'senha': senha
    }, login_callback);
}

function login_callback(data) {
    if (data.result.errno != '0') {        
        alert("Ocorreu um erro.\n" + data.result.message);
        return;
    }

    remember_me = $("#rememberMe").is(':checked');
    if (remember_me) {
        localStorage.setItem("user", data.result.user);
        localStorage.setItem("hash", data.result.hash);
        localStorage.setItem("key", data.result.key);
    }

    redirect("/virtualkey/index");
}

$(document).ready(function() {
    $("#btn_login").click(function() {
        login();
    });

    $("#btn_login, #username, #senha").keypress(function(ev) {
        if (ev.keyCode == 13) {
            login();
        }
    });
});