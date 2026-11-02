/* Melóradar főoldal — a hírek a data/articles.json fájlból töltődnek, a konfigurációt a build írja (assets/config.js). */
(function(){
const CFG=window.HRM||{topics:[],icons:{}};
const TOPICS=CFG.topics, ICONS=CFG.icons;
const TREND="__trend";
const TMAP=Object.fromEntries(TOPICS.map(t=>[t.k,t]));
const BADGE={3:["b3","Itthon is érint"],2:["b2","Ide is jöhet"],1:["b1","Érdekesség"]};
const MONTHS=["január","február","március","április","május","június","július","augusztus","szeptember","október","november","december"];
const DAYS=["vasárnap","hétfő","kedd","szerda","csütörtök","péntek","szombat"];
const st={topic:"",region:"",minrel:1,q:"",pages:4,news:[],trends:[]};
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeUrl=u=>/^https?:\/\//i.test(u||"")?u:"#";
const aid=a=>"h-"+String(a.id||"").replace(/[^a-z0-9-]/gi,"");
const d=iso=>new Date(iso+"T12:00:00");
const longDate=iso=>{const x=d(iso);return `${x.getFullYear()}. ${MONTHS[x.getMonth()]} ${x.getDate()}., ${DAYS[x.getDay()]}`};
const shortDate=iso=>{const x=d(iso);return `${String(x.getMonth()+1).padStart(2,"0")}.${String(x.getDate()).padStart(2,"0")}.`};
const svg=(name,size,sw)=>`<svg class="ic" aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]||ICONS.globe}</svg>`;
const topicOf=a=>TMAP[a.topic]||TOPICS[0];
const page=a=>esc(a.path||"#");
function banner(a){
  const t=topicOf(a);const [c1,o1,c2,o2]=t.dots||["#fff",.09,"#fff",.06];
  return `<div class="banner" aria-hidden="true" style="background:${t.bg}"><svg class="bg" viewBox="0 0 400 120" preserveAspectRatio="xMidYMid slice"><circle cx="360" cy="10" r="70" fill="${c1}" fill-opacity="${o1}"/><circle cx="30" cy="115" r="48" fill="${c2}" fill-opacity="${o2}"/></svg>${svg(a.icon,56,1.6)}</div>`;
}
const badge=a=>{const [c,l]=BADGE[a.hu_score]||BADGE[1];return `<span class="badge ${c}">${l}</span>`};
const card=a=>`<article class="card" id="${aid(a)}">${banner(a)}
    <div class="body"><div class="row">${badge(a)}<span class="src">${esc(a.region)} · ${esc(a.source)}</span></div>
      <h3><a href="${page(a)}">${esc(a.title)}</a></h3><p>${esc(a.lead)}</p></div>
    <div class="hu"><b>Neked: </b>${esc(a.hu)}</div>
    <div class="foot"><span class="tag">${esc(topicOf(a).nav)}</span><a href="${esc(safeUrl(a.url))}" target="_blank" rel="noopener">Eredeti cikk, ${shortDate(a.published)} →</a></div>
  </article>`;
const lead=a=>`<section class="lead" aria-label="Vezető hír">
    <article class="lead-main" id="${aid(a)}">
      <svg class="deco" aria-hidden="true" width="300" height="300" viewBox="0 0 300 300"><circle cx="150" cy="150" r="150" fill="#37aff0" fill-opacity=".14"/><circle cx="230" cy="70" r="70" fill="#50d7be" fill-opacity=".16"/><g transform="translate(66 66) scale(7)" fill="none" stroke="#fff" stroke-opacity=".85" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">${ICONS[a.icon]||ICONS.globe}</g></svg>
      <div class="row">${badge(a)}<span class="meta">${esc(a.topic)} · ${esc(a.region)} · ${esc(a.source)}</span></div>
      <h1><a href="${page(a)}">${esc(a.title)}</a></h1>
      <p>${esc(a.lead)}</p>
      <div class="btns"><a class="btn-light" href="${page(a)}">Tovább a hírhez</a><a class="btn-ghost" href="${esc(safeUrl(a.url))}" target="_blank" rel="noopener">Eredeti cikk</a></div>
    </article>
    <aside class="lead-hu">
      <span class="tile">${svg("globe",24,2)}</span>
      <span class="label">Mit jelent ez neked?</span>
      <p>${esc(a.hu)}</p>
    </aside>
  </section>`;
function stats(list){
  const s=list.filter(a=>a.stat&&a.stat.value).slice(0,3);
  if(!s.length)return "";
  return `<section class="sec" aria-label="A nap számai"><div class="sec-head"><h2>A nap számai <small>a mai hírekből, kattintásra a hírhez ugrik</small></h2></div>
  <div class="stats">${s.map(a=>`<a class="stat" href="#${aid(a)}">
      <span class="row"><span class="mini" style="background:${topicOf(a).bg}">${svg(a.icon,16,2)}</span><span class="ctx">${esc(a.region)} · ${esc(topicOf(a).nav)}</span></span>
      <b>${esc(a.stat.value)}</b>
      <span class="lbl">${esc(a.stat.label)}</span>
      <span class="from">A hírből: <em>${esc(a.title)}</em></span>
    </a>`).join("")}</div></section>`;
}
const trendCard=a=>`<article class="trend" id="${aid(a)}">
    <div class="trend-head"><span class="tile">${svg(a.icon||"trending-up",24,1.8)}</span>
      <div><span class="eyebrow">Munkahelyi trend</span><h3>${esc(a.term)}</h3>${a.term_hu?`<span class="gloss">${esc(a.term_hu)}</span>`:""}</div></div>
    <div class="tbody">
      <p class="ttitle"><a href="${page(a)}">${esc(a.title)}</a></p>
      <div class="blk"><span class="label">Mit jelent?</span><p>${esc(a.what)}</p></div>
      <div class="blk num"><span class="label">A számok</span><p>${esc(a.data)}</p></div>
    </div>
    <div class="hu"><b>Neked: </b>${esc(a.hu)}</div>
    <div class="foot"><span>${esc(a.region)} · ${esc(a.source)}</span><a href="${esc(safeUrl(a.url))}" target="_blank" rel="noopener">Eredeti cikk, ${shortDate(a.published)} →</a></div>
  </article>`;
function trendSection(list,all){
  if(!list.length)return "";
  const shown=all?list:list.slice(0,3);
  return `<section class="sec trends" aria-label="Trendfigyelő">
    <div class="sec-head"><h2>Trendfigyelő</h2>${!all&&list.length>3?`<button type="button" class="link-btn" data-go="${TREND}">Mind a ${list.length} trend →</button>`:""}</div>
    <p class="intro">Munkahelyi jelenségek, amelyekről most mindenki beszél: mit jelentenek, mit mutatnak róluk a friss kutatások, és mit kezdhetsz velük.</p>
    <div class="grid">${shown.map(trendCard).join("")}</div>
  </section>`;
}
const matchQ=(a,q)=>!q||[a.title,a.lead,a.hu,a.source,a.region,a.term,a.term_hu,a.what,a.data].join(" ").toLowerCase().includes(q);
function render(){
  const main=$("#main");const q=st.q.trim().toLowerCase();
  if(!st.news.length&&!st.trends.length){main.innerHTML=`<div class="state">Még nincs hír. Az első adag holnap reggel érkezik.</div>`;return}
  const tr=st.trends.filter(a=>matchQ(a,q)&&(!st.region||a.region===st.region));
  if(st.topic===TREND){main.innerHTML=tr.length?trendSection(tr,true):`<div class="state">Ezekre a szűrőkre nincs trend.</div>`;return}
  const f=st.news.filter(a=>(!st.topic||a.topic===st.topic)&&(!st.region||a.region===st.region)&&(a.hu_score||1)>=st.minrel&&matchQ(a,q));
  if(!f.length&&!(st.topic===""&&tr.length)){main.innerHTML=`<div class="state">Ezekre a szűrőkre nincs találat. Érdemes tágabb témát vagy régiót választani.</div>`;return}
  let html="";
  const days=[...new Set(f.map(a=>a.day))].sort().reverse();
  const byDay=dd=>f.filter(a=>a.day===dd);
  if(days.length){
    const today=byDay(days[0]);
    const top=today.slice().sort((a,b)=>((b.featured?1:0)-(a.featured?1:0))||(b.hu_score-a.hu_score)||b.published.localeCompare(a.published))[0];
    html+=lead(top)+stats(today.filter(a=>a!==top));
    const rest=today.filter(a=>a!==top);
    if(rest.length)html+=`<section class="sec"><div class="sec-head"><h2>További hírek <small>${longDate(days[0])}</small></h2></div><div class="grid">${rest.map(card).join("")}</div></section>`;
  }
  if(st.topic==="")html+=trendSection(tr,false);
  days.slice(1,st.pages).forEach(dd=>{const l=byDay(dd);html+=`<section class="sec"><div class="sec-head"><h2>${longDate(dd)} <small>${l.length} hír</small></h2></div><div class="grid">${l.map(card).join("")}</div></section>`});
  if(days.length>st.pages)html+=`<button type="button" class="more" id="more">Korábbi napok</button>`;
  main.innerHTML=html;
  const m=$("#more");if(m)m.onclick=()=>{st.pages+=4;render()};
}
function setTopic(t){st.topic=t;st.pages=4;buildNav();render();window.scrollTo({top:0})}
function buildNav(){
  $("#nav").innerHTML=[`<button type="button" data-t="" aria-pressed="${!st.topic}">Összes</button>`]
    .concat(TOPICS.map(t=>`<button type="button" data-t="${esc(t.k)}" aria-pressed="${st.topic===t.k}">${esc(t.nav)}</button>`))
    .concat(st.trends.length?[`<button type="button" class="trendbtn" data-t="${TREND}" aria-pressed="${st.topic===TREND}">Trendfigyelő</button>`]:[]).join("");
  $("#minrel").disabled=st.topic===TREND;
}
$("#nav").addEventListener("click",e=>{const b=e.target.closest("button");if(b)setTopic(b.dataset.t)});
$("#main").addEventListener("click",e=>{const b=e.target.closest("[data-go]");if(b)setTopic(b.dataset.go)});
$("#region").onchange=e=>{st.region=e.target.value;st.pages=4;render()};
$("#minrel").onchange=e=>{st.minrel=+e.target.value;st.pages=4;render()};
let tq;$("#q").oninput=e=>{clearTimeout(tq);tq=setTimeout(()=>{st.q=e.target.value;st.pages=4;render()},150)};
if(location.hash==="#trendek")st.topic=TREND;
buildNav();

fetch("data/articles.json?t="+Date.now()).then(r=>{if(!r.ok)throw 0;return r.json()}).then(data=>{
  const all=(data.articles||[]).filter(a=>a&&a.title&&a.day&&a.published).sort((a,b)=>(b.day+b.published).localeCompare(a.day+a.published));
  st.news=all.filter(a=>a.kind!=="trend");
  st.trends=all.filter(a=>a.kind==="trend"&&a.term);
  const latest=st.news[0]?.day;
  const todayCount=st.news.filter(a=>a.day===latest).length;
  $("#dateline").textContent=latest?`${longDate(latest)} · ${todayCount} hír`:"Nincs még hír";
  if(data.updated)$("#upd").textContent="Frissítve "+data.updated.slice(11,16);
  const regs=[...new Set(all.map(a=>a.region).filter(Boolean))].sort((a,b)=>a.localeCompare(b,"hu"));
  $("#region").insertAdjacentHTML("beforeend",regs.map(r=>`<option>${esc(r)}</option>`).join(""));
  buildNav();render();
}).catch(()=>{$("#dateline").textContent="";$("#main").innerHTML=`<div class="state">A hírek most nem tölthetők be. Pár perc múlva érdemes újratölteni az oldalt.</div>`});
})();
