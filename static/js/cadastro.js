
const cadastroForm = document.getElementById("cadastroForm");
const senhaInput = document.getElementById("cad-senha");
const confirmarSenha = document.getElementById("confirmar-senha");
const strengthBar = document.getElementById("strength-bar");
const successCadastro = document.getElementById("cadastro-success");

senhaInput.addEventListener("input", () => {
  const senha = senhaInput.value;
  let strength = 0;

  if(senha.length >= 4) strength += 25;
  if(senha.length >= 6) strength += 25;
  if(/[A-Z]/.test(senha)) strength += 25;
  if(/[0-9]/.test(senha)) strength += 25;

  strengthBar.style.width = strength + "%";

  if(strength <= 25){
    strengthBar.style.background = "red";
  } else if(strength <= 50){
    strengthBar.style.background = "orange";
  } else if(strength <= 75){
    strengthBar.style.background = "gold";
  } else {
    strengthBar.style.background = "green";
  }
});

cadastroForm.addEventListener("submit", function(event){
  event.preventDefault();

  if(senhaInput.value !== confirmarSenha.value){
    alert("As senhas não coincidem!");
    return;
  }

  successCadastro.classList.add("show");
  successCadastro.innerHTML = "✅ Conta criada com sucesso!";

  setTimeout(() => {
    window.location.href = "/login/";
}, 2000);
});
