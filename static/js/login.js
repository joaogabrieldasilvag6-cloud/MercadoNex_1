const loginForm = document.getElementById("loginForm");
const successMsg = document.getElementById("login-success");

loginForm.addEventListener("submit", function(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const senha = document.getElementById("senha").value;

  if(email === "" || senha === ""){
    alert("Preencha todos os campos!");
    return;
  }

  // Dados do usuário
  const usuario = {
    email: email
  };

  // Salva no navegador
  localStorage.setItem("usuarioLogado", JSON.stringify(usuario));

  successMsg.classList.add("show");
  successMsg.innerHTML = "✅ Login realizado com sucesso!";

  setTimeout(() => {
    window.location.href = "/dashboard/";
  }, 1500);
});