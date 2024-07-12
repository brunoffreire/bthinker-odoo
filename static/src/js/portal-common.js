
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

function callServer(endpoint, params, callback) {
	
	$.ajax({
		url: "/virtualkey/" + endpoint,
		type: "POST",
		dataType: "json",
		contentType: "application/json",
		data: JSON.stringify(params),
		error: function () {
			alert('Erro na comunicação com o servidor.');
		},
		success: function (data) {
			if (callback != null) {
				callback(data);
			}
		}
	});
}