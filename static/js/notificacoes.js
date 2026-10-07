document.addEventListener("DOMContentLoaded",()=>{
    const wrapper=document.getElementById("notificationWrapper");
    const button=document.getElementById("notificationButton");
    const panel=document.getElementById("notificationPanel");
    const list=document.getElementById("notificationList");
    const dot=document.getElementById("notificationDot");
    const countLabel=document.getElementById("notificationCountLabel");
    const markAll=document.getElementById("markAllNotifications");
    if(!wrapper||!button||!panel||!list)return;

    let cache=[];
    let loaded=false;

    function csrf(){
        const item=document.cookie.split(";").map(v=>v.trim()).find(v=>v.startsWith("csrftoken="));
        return item?decodeURIComponent(item.substring(10)):document.querySelector("[name=csrfmiddlewaretoken]")?.value||"";
    }

    function iconFor(type){
        const icons={
            estoque:"fa-boxes-stacked",
            validade:"fa-calendar-days",
            fiado:"fa-money-bill-wave",
            financeiro:"fa-chart-line"
        };
        return icons[type]||"fa-bell";
    }

    function updateIndicator(unread){
        dot.classList.toggle("show",unread>0);
        countLabel.textContent=unread===1?"1 não lida":`${unread} não lidas`;
    }

    function render(items){
        cache=items;
        if(!items.length){
            list.innerHTML='<div class="notification-empty"><i class="fa-regular fa-bell-slash"></i><strong>Nenhuma notificação</strong><span>Tudo certo por enquanto.</span></div>';
            return;
        }

        list.innerHTML=items.map(item=>`
            <article class="notification-item ${item.lida?"":"unread"}" data-id="${item.id}" data-url="${item.url||""}">
                <div class="notification-item-icon ${item.tipo}"><i class="fa-solid ${iconFor(item.tipo)}"></i></div>
                <div class="notification-item-content">
                    <div class="notification-item-head"><strong class="notification-item-title">${escapeHtml(item.titulo)}</strong><span class="notification-item-time">${escapeHtml(item.criada_em)}</span></div>
                    <p class="notification-item-message">${escapeHtml(item.mensagem)}</p>
                </div>
                ${item.lida?"":"<span class=\"notification-unread-dot\"></span>"}
            </article>
        `).join("");

        list.querySelectorAll(".notification-item").forEach(item=>item.addEventListener("click",()=>abrirNotificacao(item)));
    }

    function escapeHtml(value){
        return String(value??"").replace(/[&<>'"]/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#039;","\"":"&quot;"}[char]));
    }

    async function carregar(){
        try{
            const response=await fetch("/notificacoes/",{headers:{"X-Requested-With":"XMLHttpRequest"}});
            const data=await response.json();
            if(!response.ok||!data.sucesso)throw new Error();
            loaded=true;
            updateIndicator(data.nao_lidas||0);
            render(data.notificacoes||[]);
        }catch(error){
            if(!loaded)list.innerHTML='<div class="notification-empty"><i class="fa-solid fa-triangle-exclamation"></i><strong>Não foi possível carregar</strong><span>Tente novamente em instantes.</span></div>';
        }
    }

    async function marcarComoLida(id){
        try{
            await fetch(`/notificacoes/${id}/ler/`,{method:"POST",headers:{"X-CSRFToken":csrf(),"X-Requested-With":"XMLHttpRequest"}});
        }catch(error){}
    }

    async function abrirNotificacao(item){
        const id=item.dataset.id;
        const url=item.dataset.url;
        await marcarComoLida(id);
        item.classList.remove("unread");
        item.querySelector(".notification-unread-dot")?.remove();
        const cached=cache.find(notification=>String(notification.id)===String(id));
        if(cached)cached.lida=true;
        const unread=cache.filter(notification=>!notification.lida).length;
        updateIndicator(unread);
        if(url)window.location.href=url;
    }

    function abrir(){
        panel.hidden=false;
        button.setAttribute("aria-expanded","true");
        carregar();
    }

    function fechar(){
        panel.hidden=true;
        button.setAttribute("aria-expanded","false");
    }

    button.addEventListener("click",event=>{
        event.stopPropagation();
        panel.hidden?abrir():fechar();
    });

    markAll.addEventListener("click",async event=>{
        event.stopPropagation();
        try{
            const response=await fetch("/notificacoes/ler-todas/",{method:"POST",headers:{"X-CSRFToken":csrf(),"X-Requested-With":"XMLHttpRequest"}});
            const data=await response.json();
            if(!response.ok||!data.sucesso)throw new Error();
            cache.forEach(item=>item.lida=true);
            updateIndicator(0);
            render(cache);
        }catch(error){}
    });

    document.addEventListener("click",event=>{
        if(!wrapper.contains(event.target))fechar();
    });

    document.addEventListener("keydown",event=>{
        if(event.key==="Escape")fechar();
    });

    carregar();
    setInterval(carregar,60000);
});
