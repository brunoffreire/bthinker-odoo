
/********************************************************************** */
// Funções comuns
/********************************************************************** */

function redirect(endpoint) {
	window.location.replace(endpoint);
}

function share(title, text, url, callback) {
	if (navigator.share) {
		navigator.share({
			title: title,
			text: text,
			url: url,
		})
			.then(function () {
				if (callback != null) {
					callback();
				}
			});
	}
}

/********************************************************************** */
// Chamadas ao servidor
/********************************************************************** */

function callServer(endpoint, params, callback, ctx = null) {
	
	$.ajax({
		url: "/api/" + endpoint,
		type: "POST",
		dataType: "json",
		contentType: "application/json",
		data: JSON.stringify(params),
		error: function () {
			Swal.fire({
				title: "Erro",
				text: "Ocorreu um erro na comunicação com o servidor.",
				icon: "error"
			  });
		},
		success: function (data) {
			if (callback != null) {
				callback(data, ctx);
			}
		}
	});
}

$(document).ready(function() {	
	$('.toggle-password').on('click', function() {				
		const inputId = $(this).attr('for');
		const passwordField = $('#' + inputId);
		const type = passwordField.attr('type') === 'password' ? 'text' : 'password';
		passwordField.attr('type', type);

		// Alterna o ícone
		$(this).toggleClass('fa-eye fa-eye-slash');
	});
});