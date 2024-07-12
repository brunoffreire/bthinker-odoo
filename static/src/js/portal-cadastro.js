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
    
    var username = $("#username").val();
    var nome = $("#nome").val();
    var email = $("#email").val();
    var celular = $("#celular").val();
    var senha = $("#senha").val();
    var confirma_senha = $("#confirma_senha").val();   
    var termo = $("#termo").prop("checked") ? '1' : '0';
    
    data = callServer('save_user_profile', {
        'username': username,
        'nome': nome,
        'email': email,
        'celular': celular,        
        'senha': senha,
        'confirma_senha': confirma_senha,
        'termo': termo
    }, save_profile_callback);
}

function save_profile_callback(data) {
    if (data.result.errno != '0') {        
        alert("Ocorreu um erro ao gravar.\n" + data.result.message);
        return;
    }

    alert("Dados salvos com sucesso!.\nVocê receberá um e-mail para confirmar sua conta.");
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