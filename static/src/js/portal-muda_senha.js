
function save_profile() {
    
    var senha = $("#senha").val();
    var confirma_senha = $("#confirma_senha").val();   

    let params = new URLSearchParams(window.location.search);
    let hash = params.get("hash");
    
    data = callServer('update_user_password', {
        'senha': senha,
        'confirma_senha': confirma_senha,
        'hash': hash
    }, save_profile_callback);
}

function save_profile_callback(data) {
    if (data.result.errno != '0') {        
        alert("Ocorreu um erro ao gravar.\n" + data.result.message);
        return;
    }

    alert(data.result.message);
    redirect("/virtualkey/login");
}

$(document).ready(function() {
    $("#btn_save").on('click', function() {
        save_profile();
    });
});