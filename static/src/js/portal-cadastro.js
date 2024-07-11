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
    
    var username = $("#username_profile").val();
    var name = $("#name_profile").val();
    var email = $("#email_profile").val();
    var mobile = $("#mobile_profile").val();
    var password = $("#password_profile").val();
    var confirm_password = $("#confirm_password_profile").val();   
    var term_agree = $("#terms_agree").prop("checked") ? '1' : '0';
    
    data = callServer('save_user_profile', {
        'username': username,
        'name': name,
        'email': email,
        'celular': mobile,        
        'senha': password,
        'confirma_senha': confirm_password,
        'agree': term_agree
    }, save_profile_callback);
}

function save_profile_callback(data) {
    if (data.result.errno != '0') {
        Swal.fire({
			title: '<h6>Ocorreu um erro ao gravar</h6>',
			html: data.result.message,
			icon: 'error'
        })
    }else{
        Swal.fire({
			title: '<h6>Cadastro realizado com sucesso</h6>',
			html: 'Você receberá um e-mail para confirmar sua conta.',
			icon: 'success', 
			showDenyButton: false,
			timer: 2500
        }).then(() =>{
            location.replace("/virtualkey")
        })
    }
    
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