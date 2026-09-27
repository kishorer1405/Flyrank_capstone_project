(function(){
  "use strict";
  const current = document.currentScript;
  if (!current) return;
  const src = new URL(current.src);
  const widgetId = src.searchParams.get("id");
  if (!widgetId) return;
  const apiBase = src.origin;
  const mount = document.createElement("div");
  mount.setAttribute("data-flyrank-widget", widgetId);
  current.parentNode.insertBefore(mount, current.nextSibling);
  const shadow = mount.attachShadow ? mount.attachShadow({mode:"open"}) : mount;
  const style=document.createElement("style");
  style.textContent=`:host{all:initial}.box{font-family:Inter,system-ui,sans-serif;max-width:420px;padding:22px;border:1px solid #dbe3ef;border-radius:16px;background:#fff;box-shadow:0 10px 30px rgba(15,23,42,.08);color:#172033}.title{font-size:20px;font-weight:750;margin:0 0 6px}.desc{color:#64748b;font-size:14px;margin:0 0 16px}.field{margin:12px 0}.field label{display:block;font-size:13px;font-weight:650;margin-bottom:6px}.field input,.field textarea{box-sizing:border-box;width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:9px;font:inherit}.field textarea{min-height:80px;resize:vertical}.btn{width:100%;border:0;border-radius:9px;padding:11px 14px;background:#2563eb;color:#fff;font-weight:700;cursor:pointer}.btn:disabled{opacity:.65;cursor:wait}.msg{font-size:13px;margin-top:10px}.hp{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}`;
  shadow.appendChild(style);
  const box=document.createElement("div"); box.className="box"; shadow.appendChild(box);
  function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
  async function init(){
    try{
      const r=await fetch(apiBase+"/api/v1/public/widgets/"+encodeURIComponent(widgetId)+"/config");
      if(!r.ok) throw new Error("Unable to load widget");
      const c=await r.json();
      box.innerHTML=`<h3 class="title">${esc(c.title)}</h3><p class="desc">${esc(c.description)}</p><form id="f"></form><div id="m" class="msg" role="status"></div>`;
      const form=box.querySelector("#f");
      for(const f of c.fields){
        const wrap=document.createElement("div"); wrap.className="field";
        const label=document.createElement("label"); label.textContent=f.label+(f.required?" *":""); label.htmlFor="fr-"+f.name;
        const el=document.createElement(f.type==="textarea"?"textarea":"input"); el.id="fr-"+f.name; el.name=f.name; el.placeholder=f.placeholder||""; el.required=!!f.required; if(f.type!=="textarea") el.type=f.type;
        wrap.append(label,el); form.appendChild(wrap);
      }
      const hp=document.createElement("input"); hp.className="hp"; hp.name="website"; hp.tabIndex=-1; hp.autocomplete="off"; form.appendChild(hp);
      const btn=document.createElement("button"); btn.className="btn"; btn.type="submit"; btn.textContent=c.button_text; form.appendChild(btn);
      form.addEventListener("submit",async e=>{e.preventDefault();const msg=box.querySelector("#m"); msg.textContent="Sending…"; btn.disabled=true; const data={}; c.fields.forEach(f=>data[f.name]=form.elements[f.name].value); try{const r=await fetch(c.submission_url,{method:"POST",headers:{"Content-Type":"application/json","Idempotency-Key":crypto.randomUUID?crypto.randomUUID():String(Date.now())},body:JSON.stringify({widget_id:c.id,data,honeypot:hp.value})}); const body=await r.json().catch(()=>({})); if(r.status===429) throw new Error("Too many attempts. Please try again shortly."); if(!r.ok) throw new Error(body.detail||"Please check the form and try again."); msg.textContent="Thanks! Your information was received."; form.reset();}catch(err){msg.textContent=err.message||"Something went wrong.";}finally{btn.disabled=false;}});
    }catch(err){box.innerHTML=`<div class="msg">Widget unavailable right now.</div>`;}
  }
  init();
})();
