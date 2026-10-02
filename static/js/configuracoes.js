document.addEventListener("DOMContentLoaded",()=>{
    const root=document.querySelector("[data-configuracoes]");
    if(!root)return;

    const STORAGE_KEY="mercadonex_configuracoes";
    const defaults={tema:"claro",fonte:"medium",compacto:false,animacoes:true,estoque:true,fiado:true};
    const saveUrl="{% url 'salvar_configuracoes' %}";
    const temaOptions=document.querySelectorAll("[data-theme-option]");
    const fontOptions=document.querySelectorAll("[data-font-size]");
    const compactMode=document.getElementById("compactMode");
    const animationsMode=document.getElementById("animationsMode");
    const stockNotifications=document.getElementById("stockNotifications");
    const debtNotifications=document.getElementById("debtNotifications");
    const btnSalvar=document.getElementById("btnSalvarConfig");
    const btnRestaurar=document.getElementById("btnRestaurar");
    const saveBar=document.getElementById("configSaveBar");
    const saveMessage=document.getElementById("configSaveMessage");

    function carregarConfig(){
        try{
            const salvo=JSON.parse(localStorage.getItem(STORAGE_KEY));
            return {...defaults,...(salvo||{})};
        }catch(e){return {...defaults};}
    }

    let config=carregarConfig();

    function aplicarConfig(){
        document.body.classList.toggle("mn-compact",!!config.compacto);
        document.body.classList.toggle("mn-no-animations",!config.animacoes);
        document.body.classList.toggle("mn-font-small",config.fonte==="small");
        document.body.classList.toggle("mn-font-large",config.fonte==="large");
        document.body.classList.toggle("mn-dark",config.tema==="escuro");

        temaOptions.forEach(option=>{
            const ativo=option.dataset.themeOption===config.tema;
            option.classList.toggle("selected",ativo);
            const input=option.querySelector("input");
            if(input)input.checked=ativo;
        });

        fontOptions.forEach(option=>option.classList.toggle("active",option.dataset.fontSize===config.fonte));
        if(compactMode)compactMode.checked=!!config.compacto;
        if(animationsMode)animationsMode.checked=!!config.animacoes;
        if(stockNotifications)stockNotifications.checked=!!config.estoque;
        if(debtNotifications)debtNotifications.checked=!!config.fiado;
    }

    function salvarLocalmente(){
        localStorage.setItem(STORAGE_KEY,JSON.stringify(config));
    }

    function mostrarMensagem(texto,tipo="saved"){
        if(saveMessage)saveMessage.textContent=texto;
        if(saveBar){
            saveBar.classList.remove("saved","error");
            saveBar.classList.add(tipo);
            clearTimeout(mostrarMensagem.timer);
            mostrarMensagem.timer=setTimeout(()=>saveBar.classList.remove("saved","error"),2200);
        }
    }

    function csrfToken(){
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value||getCookie("csrftoken");
    }

    function getCookie(name){
        const item=document.cookie.split(";").map(c=>c.trim()).find(c=>c.startsWith(name+"="));
        return item?decodeURIComponent(item.substring(name.length+1)):"";
    }

    async function salvarServidor(){
        const response=await fetch(saveUrl,{
            method:"POST",
            headers:{"Content-Type":"application/json","X-CSRFToken":csrfToken(),"X-Requested-With":"XMLHttpRequest"},
            body:JSON.stringify(config)
        });
        let data={};
        try{data=await response.json();}catch(e){}
        if(!response.ok||data.sucesso===false)throw new Error(data.mensagem||"Não foi possível salvar no servidor.");
        return data;
    }

    function alterar(campo,valor){
        config[campo]=valor;
        aplicarConfig();
        salvarLocalmente();
        mostrarMensagem("Alteração aplicada. Clique em salvar para registrar no servidor.");
    }

    temaOptions.forEach(option=>option.addEventListener("click",()=>alterar("tema",option.dataset.themeOption)));
    fontOptions.forEach(option=>option.addEventListener("click",()=>alterar("fonte",option.dataset.fontSize)));
    compactMode?.addEventListener("change",()=>alterar("compacto",compactMode.checked));
    animationsMode?.addEventListener("change",()=>alterar("animacoes",animationsMode.checked));
    stockNotifications?.addEventListener("change",()=>alterar("estoque",stockNotifications.checked));
    debtNotifications?.addEventListener("change",()=>alterar("fiado",debtNotifications.checked));

    btnSalvar?.addEventListener("click",async()=>{
        btnSalvar.disabled=true;
        btnSalvar.innerHTML='<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
        try{
            salvarLocalmente();
            await salvarServidor();
            mostrarMensagem("Configurações salvas com sucesso!","saved");
        }catch(error){
            console.error(error);
            mostrarMensagem("Salvas apenas neste navegador. Verifique o servidor.","error");
        }finally{
            setTimeout(()=>{
                btnSalvar.disabled=false;
                btnSalvar.innerHTML='<i class="fa-solid fa-floppy-disk"></i>Salvar alterações';
            },450);
        }
    });

    btnRestaurar?.addEventListener("click",async()=>{
        if(!confirm("Restaurar todas as configurações para o padrão?"))return;
        config={...defaults};
        aplicarConfig();
        salvarLocalmente();
        mostrarMensagem("Padrões restaurados. Salvando no servidor...");
        try{
            await salvarServidor();
            mostrarMensagem("Configurações restauradas e salvas!","saved");
        }catch(error){
            console.error(error);
            mostrarMensagem("Padrões restaurados neste navegador.","error");
        }
    });

    aplicarConfig();
});