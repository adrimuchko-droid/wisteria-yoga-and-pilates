(()=>{const b=document.body,D=b.dataset,$=(s,r=document)=>[...r.querySelectorAll(s)];
const ls={get:k=>{try{return localStorage.getItem(k)}catch(_){return null}},set:(k,v)=>{try{localStorage.setItem(k,v)}catch(_){}}};
const nb=$('.burger')[0],nav=document.getElementById('nav');
nb&&nb.addEventListener('click',()=>{nb.setAttribute('aria-expanded',nav.classList.toggle('open'))});
if(ls.get('wis-hl')==='off')b.classList.add('clean');
$('[data-hl-toggle]').forEach(x=>x.addEventListener('click',()=>{b.classList.toggle('clean');ls.set('wis-hl',b.classList.contains('clean')?'off':'on')}));
function loadGA(){if(!D.ga||window.__ga)return;window.__ga=1;const s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(D.ga);document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',D.ga,{anonymize_ip:true})}
function loadMap(el){if(el.querySelector('iframe'))return;const i=document.createElement('iframe');i.src=el.dataset.map;i.loading='lazy';i.title=el.dataset.title||'Map';i.referrerPolicy='no-referrer-when-downgrade';el.innerHTML='';el.appendChild(i)}
const cc=document.getElementById('cc');
function apply(){if(ls.get('wis-consent')==='yes'){loadGA();$('[data-map]').forEach(loadMap)}}
if(cc){if(!ls.get('wis-consent'))cc.hidden=false;
$('[data-cc]',cc).forEach(x=>x.addEventListener('click',()=>{ls.set('wis-consent',x.dataset.cc);cc.hidden=true;apply()}));
$('[data-cc-open]').forEach(x=>x.addEventListener('click',()=>{cc.hidden=false}))}
$('[data-map-load]').forEach(x=>x.addEventListener('click',()=>loadMap(x.closest('[data-map]'))));
apply();
$('[data-track]').forEach(a=>a.addEventListener('click',()=>{window.gtag&&gtag('event','cta_click',{cta:a.dataset.track})}));
$('form[data-form]').forEach(f=>f.addEventListener('submit',async e=>{e.preventDefault();const m=f.querySelector('.msg');m.className='msg';
if(f.querySelector('[name=_gotcha]').value)return;if(!f.checkValidity()){f.reportValidity();return}
const d=Object.fromEntries(new FormData(f));delete d._gotcha;
if(D.endpoint){try{const r=await fetch(D.endpoint,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(d)});if(!r.ok)throw 0;f.reset();m.textContent=f.dataset.ok;m.classList.add('ok');window.gtag&&gtag('event','generate_lead',{form_id:f.dataset.form})}catch(_){m.textContent=f.dataset.err;m.classList.add('bad')}}
else if(D.email){const body=Object.entries(d).filter(([k])=>k[0]!=='_').map(([k,v])=>k+': '+v).join('\n');location.href='mailto:'+D.email+'?subject='+encodeURIComponent('Wisteria – '+f.dataset.form)+'&body='+encodeURIComponent(body)}
else{m.textContent=f.dataset.noconf;m.classList.add('bad')}}));
})();
