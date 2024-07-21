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
        localStorage.setItem("auto_login", remember_me);
    }

    redirect("/virtualkey");
}


function change_password() {        
    username = $("#username").val();
    callServer('change_user_password', {
        'username': username
    }, change_password_callback);
}

function change_password_callback(data) {
    if (data.result.errno != '0') {        
        alert("Ocorreu um erro.\n" + data.result.message);
        return;
    }
    alert("Sucesso!\n\n" + data.result.message);
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

    $("#forgot_password").click(function() {
        var ok = confirm("Deseja receber um e-mail para redefinição de senha?");
        if(!ok){
            return;
        }

        change_password();
    });
});