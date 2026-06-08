const VERSION = "0.5.0";
const SURFACE = "WEB_SANCTUM_OPERATIONAL_SPINE_AND_WARP_V0_5";
let snapshot = null;
let quality = "Performance";
let bridgeMode = "probing";
let paletteOpen = false;
let currentPage = "sanctum";
window.__SANCTUM_READY = false;
const $ = (id) => document.getElementById(id);
function setText(id, text){ const el=$(id); if(el) el.textContent = text; }
function toast(msg){ const t=$("toast"); if(!t) return; t.textContent=msg; t.classList.add("show"); setTimeout(()=>t.classList.remove("show"),2500); }
function renderContour(){
  const c = snapshot?.contour || {};
  setText("contour", `${c.current_contour || "MAIN_OR_UNKNOWN"} · ${quality} · branch:${c.branch || "unknown"} · head:${(c.head||"unknown").slice(0,10)}`);
  setText("contourText", c.current_contour || "read-only surface");
  setText("taskText", snapshot?.task?.id || "NO_ACTIVE_TASK");
  setText("warpText", snapshot?.warp?.mode || "NO_WARP_SELECTED");
  const sp = snapshot?.warp?.stage_progress || {done:0,total:0}; setText("stageText", `${sp.done || 0} / ${sp.total || 0}`);
  setText("nextText", snapshot?.task?.next_action || "Create WARP or register taskpack");
  const op = $("operatorText"); if(op) op.textContent = JSON.stringify(snapshot, null, 2);
  const ws = $("warpStatus"); if(ws) ws.textContent = JSON.stringify(snapshot?.warp || {}, null, 2);
}
function renderFlow(){
  const labels=["INTAKE","TASKPACK","ASTRA GATE","WARP START","WORK","STAGE PASS","VALIDATE","REPORT","OWNER ACCEPT","PROMOTE"];
  const root=$("flowNodes"); if(!root) return; root.innerHTML="";
  const active = Math.min(4, labels.length-1);
  labels.forEach((label,i)=>{ const d=document.createElement("div"); d.className="node"+(i===active?" active":""); d.innerHTML=`<div class="dot"></div><label>${label}</label>`; root.appendChild(d); });
}
function renderOrbit(){
  const root=$("orbit"); if(!root) return; root.innerHTML="";
  const names=["MECHANICUS","ASTRONOMICON","ADMINISTRATUM","INQUISITION","OFFICIO","FREELANCE","TRADING"];
  const coords=[[65,22],[70,66],[78,42],[55,78],[30,72],[18,48],[22,26]];
  names.forEach((n,i)=>{const e=document.createElement("div"); e.className="orb"; e.textContent=n; e.style.left=coords[i][0]+"%"; e.style.top=coords[i][1]+"%"; root.appendChild(e);});
}
function showPage(page){
  currentPage=page;
  document.querySelectorAll(".page").forEach(e=>e.classList.remove("active"));
  document.querySelectorAll(".nav button[data-page]").forEach(e=>e.classList.toggle("active", e.dataset.page===page));
  const el=$("page-"+page); if(el) el.classList.add("active");
  toast(`Page: ${page}`);
}
async function loadSnapshot(){
  try{
    const r = await fetch("/api/snapshot", {cache:"no-store"});
    if(r.ok){ snapshot = await r.json(); bridgeMode = "online"; setText("bridgePill","bridge: actions enabled"); }
    else throw new Error("api snapshot not ok");
  }catch(e){
    const r = await fetch("imperium_snapshot.json", {cache:"no-store"}); snapshot = await r.json(); bridgeMode = "static"; setText("bridgePill","bridge: static snapshot");
  }
  snapshot.surface = SURFACE;
  renderContour(); renderFlow(); renderOrbit();
  window.__SANCTUM_READY = true;
}
async function runAction(action){
  const payload={action};
  if(action === "register_taskpack_pc") payload.zip_path = $("taskZipPath")?.value || "";
  try{
    const r = await fetch("/api/action", {method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify(payload)});
    if(!r.ok) throw new Error(`HTTP ${r.status}`);
    const data=await r.json();
    const text=JSON.stringify(data,null,2);
    const targets={register_taskpack_pc:"registrationTrace",create_warp:"warpStatus",start_work:"warpStatus",validate_warp:"validationTrace",build_report_bundle:"reportTrace",run_playwright:"playwrightTrace",run_playwright_screenshots:"playwrightTrace",mechanicus_register_tool:"mechanicusTrace",mechanicus_list_tools:"mechanicusTrace"};
    setText(targets[action]||"operatorText", text);
    toast(data.message || data.status || action);
  }catch(e){
    toast(`actions disabled: command copied for ${action}`);
    const cmd = action.replaceAll("_","-");
    navigator.clipboard?.writeText(cmd).catch(()=>{});
  }
}
const commands = [
  {label:"Go Sanctum", kind:"page", page:"sanctum"},{label:"Go WARP", kind:"page", page:"warp"},{label:"Go Task Register", kind:"page", page:"register"},{label:"Go Astronomicon", kind:"page", page:"astronomicon"},{label:"Go Mechanicus", kind:"page", page:"mechanicus"},{label:"Go Validation", kind:"page", page:"validation"},{label:"Go Reports", kind:"page", page:"reports"},{label:"Go Playwright", kind:"page", page:"playwright"},
  {label:"Create WARP", kind:"action", action:"create_warp"},{label:"Start Work", kind:"action", action:"start_work"},{label:"Export Task Form", kind:"action", action:"export_task_template"},{label:"Run Playwright", kind:"action", action:"run_playwright"}
];
function rankCommand(c,q){ q=q.toLowerCase(); const l=c.label.toLowerCase(); let score=0; if(c.kind==="page") score+=100; if(l.includes(q)) score+=50; if(l.startsWith("go "+q)) score+=80; if(l.endsWith(q)) score+=20; return score; }
function renderPalette(){
  const q=$("paletteSearch")?.value || ""; const list=$("paletteList"); if(!list) return; list.innerHTML="";
  const filtered=commands.filter(c=>c.label.toLowerCase().includes(q.toLowerCase())||c.page===q.toLowerCase()).sort((a,b)=>rankCommand(b,q)-rankCommand(a,q));
  filtered.forEach((c,i)=>{const item=document.createElement("div"); item.className="paletteItem"+(i===0?" selected":""); item.textContent=c.label; item.dataset.index=String(commands.indexOf(c)); item.onclick=()=>executeCommand(c); list.appendChild(item);});
}
function executeCommand(c){ if(!c) return; closePalette(); if(c.kind==="page") showPage(c.page); else runAction(c.action); }
function executeFirstPaletteItem(){ const first=document.querySelector("#paletteList .paletteItem"); if(!first) return; const idx=Number(first.dataset.index); executeCommand(commands[idx]); }
function openPalette(){ paletteOpen=true; $("commandPalette")?.classList.remove("hidden"); $("paletteSearch")?.focus(); renderPalette(); }
function closePalette(){ paletteOpen=false; $("commandPalette")?.classList.add("hidden"); }
function cycleQuality(){ const modes=["Performance","Balanced","Cinematic"]; quality=modes[(modes.indexOf(quality)+1)%modes.length]; document.body.dataset.quality=quality.toLowerCase(); setText("qualityButton",`Quality: ${quality}`); renderContour(); }
function wire(){
  document.querySelectorAll("button[data-page]").forEach(b=>b.addEventListener("click",()=>showPage(b.dataset.page)));
  document.querySelectorAll("button[data-action]").forEach(b=>b.addEventListener("click",()=>runAction(b.dataset.action)));
  $("qualityButton")?.addEventListener("click",cycleQuality); $("paletteButton")?.addEventListener("click",openPalette); $("copySnapshot")?.addEventListener("click",()=>navigator.clipboard?.writeText(JSON.stringify(snapshot,null,2)));
  $("paletteSearch")?.addEventListener("input",renderPalette); $("paletteSearch")?.addEventListener("keydown",ev=>{ if(ev.key==="Enter"){ev.preventDefault(); executeFirstPaletteItem();} if(ev.key==="Escape"){closePalette();} });
  document.addEventListener("keydown",ev=>{ if((ev.ctrlKey||ev.metaKey)&&ev.key.toLowerCase()==="k"){ev.preventDefault(); openPalette();} if(paletteOpen&&ev.key==="Escape") closePalette(); });
}
let last=performance.now(), frames=[]; function frame(now){ const dt=now-last; last=now; frames.push(dt); if(frames.length>50) frames.shift(); const avg=frames.reduce((a,b)=>a+b,0)/frames.length; const fps=Math.round(1000/avg); const jitter=(Math.max(...frames)-Math.min(...frames)).toFixed(1); setText("framePill",`frame pacing: ${fps} fps · jitter ${jitter}ms`); requestAnimationFrame(frame); }
wire(); loadSnapshot(); requestAnimationFrame(frame);
