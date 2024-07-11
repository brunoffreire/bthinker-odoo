
/********************************************************************** */
// Funções comuns
/********************************************************************** */

function redirect(endpoint) {
	window.location.replace(endpoint);
}

function start_load() {
	$(".loader-bg").removeClass('invisible');
	$(".loader-bg").addClass('visible');
}

function end_load() {
	$(".loader-bg").removeClass('visible');
	$(".loader-bg").addClass('invisible');
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
	//start_load();
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