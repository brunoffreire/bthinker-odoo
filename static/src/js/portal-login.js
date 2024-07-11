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
        Swal.fire({
			title: '<h6>Um erro ocorreu.</h6>',
			html: data.result.message,
			icon: 'error'
        });
        return;
    }

    remember_me = $("#rememberMe").is(':checked');
    if (remember_me) {
        localStorage.setItem("user", data.result.username);
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