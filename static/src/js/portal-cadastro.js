function checkUsername(){
    username_message = $("#username_message");
    username_message.text = "";

    var username = $("#username_profile").val();
    data = callServer('check_username_profile', {
        'username':username
    }, checkUsername_callback);
}

function checkUsername_callback(data){
    strClass = "text-danger";
    if (data.result.errno == '0') {
        strClass = "text-success";
    }
    
    username_message = $("#username_message");
    username_message.removeClass();
    username_message.addClass(strClass);
    username_message.text(data.result.message);
}

function save_profile() {
    
    $('#btn_save').prop('disabled', true);
    
    var username = $("#username").val();
    var nome = $("#nome").val();
    var email = $("#email").val();
    var celular = $("#celular").val();
    var senha = $("#senha").val();
    var confirma_senha = $("#confirma_senha").val();   
    var termo = $("#termo").prop("checked") ? '1' : '0';

    let params = new URLSearchParams(window.location.search);
    let hash = params.get("hash");
    
    data = callServer('save_user_profile', {
        'username': username,
        'nome': nome,
        'email': email,
        'celular': celular,        
        'senha': senha,
        'confirma_senha': confirma_senha,
        'termo': termo,
        'hash': hash
    }, save_profile_callback);
}

function save_profile_callback(data) {
    
    $('#btn_save').prop('disabled', false);
    
    if (data.result.errno != '0') {        
        Swal.fire({
            title: "Erro ao gravar",
            text: data.result.message,
            icon: "error"
          });

        return;
    }
    
    Swal.fire({
        title: "Sucesso",
        text: "Dados salvos com sucesso! Você receberá um e-mail para confirmar sua conta.",
        icon: "success"
      });

    redirect("/virtualkey");
}

function toggle_password() {

    do_change = $("#chk_change_password").is(':checked');
    $("#password_div").addClass('d-none');

    if (do_change) {
        $("#password_div").removeClass('d-none');
    }
}

$(document).ready(function() {
    $("#terms_agree:checkbox:checked").removeAttr("checked", "");

    $("#btn_save").on('click', function() {
        save_profile();
    });

    $("#chk_change_password").on('click', function () {
        toggle_password();
    });

});