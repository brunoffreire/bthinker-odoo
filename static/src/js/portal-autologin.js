$(document).ready(function () {
  hash_login();
});

function hash_login() {
  let user = localStorage.getItem("user");
  let hash = localStorage.getItem("hash");
  let auto_login = localStorage.getItem("auto_login");

  data = {
    user: user,
    hash: hash,
    auto_login: auto_login,
  };

  callServer("do_hash_login", data, hash_login_callback);
}

function hash_login_callback(data) {
  if (data.result.errno == "0") {
    redirect("/virtualkey/index");
  }
  redirect("/virtualkey/login");
}
