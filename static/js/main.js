function showToast(msg){
  const t = document.getElementById('toast');
  if(!t) return;
  t.textContent = msg || 'Done';
  t.classList.add('show');
  setTimeout(()=> t.classList.remove('show'), 2000);
}

// Subtle parallax on hero art
(function(){
  const art = document.querySelector('.hero-art');
  if(!art) return;
  const orbs = art.querySelectorAll('.orb, .ring');
  window.addEventListener('mousemove', (e)=>{
    const x = (e.clientX / window.innerWidth - 0.5) * 10;
    const y = (e.clientY / window.innerHeight - 0.5) * 10;
    orbs.forEach((el, i)=>{
      el.style.transform = `translate(${x*(i+1)}px, ${y*(i+1)}px)`;
    });
  });
})();

// Industries ticker -> use case panel interactions
(function(){
  const map = {
    'Finance': [
      'LLM co-pilot for analyst research and report drafting',
      'Real-time fraud triage and transaction explanation',
      'Automated KYC document parsing with human-in-the-loop'
    ],
    'Healthcare': [
      'Clinical note summarization and ICD coding suggestions',
      'Patient triage chat with symptom extraction',
      'Prior authorization letter drafting'
    ],
    'E‑commerce': [
      'Product description generation at scale',
      'Conversational shopping assistants',
      'Return reason analysis and routing'
    ],
    'Gaming': [
      'Dynamic NPC dialog and quest generation',
      'Toxicity detection and moderation assistance',
      'Player support chat automation'
    ],
    'Education': [
      'Personalized tutoring and lesson plan drafting',
      'Quiz generation and grading rubrics',
      'Course content localization'
    ],
    'Legal': [
      'Contract clause extraction and risk highlights',
      'Case law retrieval-augmented answers',
      'Intake to engagement letter drafting'
    ],
    'Media': [
      'Headline variants and SEO briefs',
      'Interview transcript summarization',
      'Multilingual captioning assistance'
    ],
    'Robotics': [
      'Natural-language task planning to actions',
      'Error explanation and operator guidance',
      'Procedure summarization from logs'
    ],
    'Logistics': [
      'Shipment exception triage and messaging',
      'Route note summarization and ETA explanations',
      'SOP assistant for warehouse operations'
    ],
    'SaaS': [
      'In-app AI help and workflow assistants',
      'Support ticket summarization and reply drafts',
      'Changelog and release notes generation'
    ],
    'GovTech': [
      'Citizen service chat with policy-grounded answers',
      'Form intake classification and routing',
      'Grant application summarization'
    ]
  };

  const panel = document.querySelector('.usecase-panel');
  if(!panel) return;
  const titleSpan = panel.querySelector('.uc-industry');
  const list = panel.querySelector('.uc-list');

  function updatePanel(industry){
    titleSpan.textContent = industry;
    const items = map[industry] || ['No examples available yet.'];
    list.innerHTML = items.map(x=>`<li>${x}</li>`).join('');
    showToast(`${industry} use cases`);
  }

  document.querySelectorAll('.ticker .ticker-item').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const ind = btn.getAttribute('data-industry');
      if(!ind) return;
      updatePanel(ind);
    });
  });
})();

// Copy to clipboard for code templates
(function(){
  function getPrevCode(btn){
    // If data-target-prev, find previous sibling <pre><code>
    let node = btn.previousElementSibling;
    while(node && !(node.tagName === 'PRE' && node.querySelector('code'))){ node = node.previousElementSibling; }
    return node ? node.querySelector('code') : null;
  }
  function copyText(text){
    if(navigator.clipboard && navigator.clipboard.writeText){ return navigator.clipboard.writeText(text); }
    const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); return Promise.resolve();
  }
  document.querySelectorAll('.copy-btn').forEach(btn=>{
    btn.addEventListener('click', async ()=>{
      const code = getPrevCode(btn);
      if(!code) return;
      try{ await copyText(code.innerText); showToast('Copied'); }
      catch(_){ showToast('Copy failed'); }
    });
  });
})();

// Haptics-like click feedback and micro-animations
(function(){
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(prefersReduced) return;
  function vibrate(ms){ try { if(navigator.vibrate) navigator.vibrate(ms); } catch(_){} }
  function pressAnim(el){
    if(prefersReduced || !window.gsap){ el.style.transform = 'scale(0.97)'; return; }
    gsap.killTweensOf(el);
    gsap.to(el, { duration: 0.08, scale: 0.97, ease: 'power2.out' });
  }
  function releaseAnim(el){
    if(prefersReduced || !window.gsap){ el.style.transform = ''; return; }
    gsap.killTweensOf(el);
    gsap.to(el, { duration: 0.18, scale: 1, ease: 'power3.out' });
  }
  function bind(el){
    el.addEventListener('pointerdown', ()=>{ pressAnim(el); vibrate(10); });
    el.addEventListener('pointerup',   ()=>{ releaseAnim(el); });
    el.addEventListener('pointerleave',()=>{ releaseAnim(el); });
    el.addEventListener('keydown', (e)=>{ if(e.key==='Enter' || e.key===' '){ pressAnim(el); vibrate(5); }});
    el.addEventListener('keyup',   (e)=>{ if(e.key==='Enter' || e.key===' '){ releaseAnim(el); }});
  }
  document.querySelectorAll('.btn, .magnetic, button, [role="button"]').forEach(bind);
})();

// Reveal on scroll
(function(){
  const els = document.querySelectorAll('.card, .product-card, .glass, .section-head, .hero-copy');
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{
      if(e.isIntersecting){
        e.target.style.transition = 'transform .6s ease, opacity .6s ease';
        e.target.style.transform = 'translateY(0)';
        e.target.style.opacity = '1';
        io.unobserve(e.target);
      }
    })
  }, {threshold: 0.12});
  els.forEach(el=>{
    el.style.opacity = '0';
    el.style.transform = 'translateY(12px)';
    io.observe(el);
  })
})();

// Cursor spotlight & magnetic buttons
(function(){
  const spot = document.querySelector('.cursor-spot');
  let rafId = 0, tx = 0, ty = 0, cx = 0, cy = 0;
  function loop(){
    cx += (tx - cx) * 0.12; cy += (ty - cy) * 0.12;
    if(spot){ spot.style.transform = `translate(${cx}px, ${cy}px)`; spot.style.opacity = 1; }
    rafId = requestAnimationFrame(loop);
  }
  window.addEventListener('mousemove', (e)=>{ tx = e.clientX - 210; ty = e.clientY - 210; if(!rafId) rafId = requestAnimationFrame(loop); });
  window.addEventListener('mouseleave', ()=>{ if(spot) spot.style.opacity = 0; cancelAnimationFrame(rafId); rafId = 0; });

  document.querySelectorAll('.magnetic').forEach(btn=>{
    let rId = 0;
    function onMove(e){
      const rect = btn.getBoundingClientRect();
      const x = (e.clientX - rect.left - rect.width/2) * 0.15;
      const y = (e.clientY - rect.top - rect.height/2) * 0.15;
      btn.style.transform = `translate(${x}px, ${y}px)`;
    }
    btn.addEventListener('mouseenter', ()=>{ rId = 1; });
    btn.addEventListener('mousemove', onMove);
    btn.addEventListener('mouseleave', ()=>{ btn.style.transform = 'translate(0,0)'; rId = 0; });
  });
})();

// Smooth page transition for internal links
(function(){
  const overlay = document.querySelector('.page-transition');
  if(!overlay) return;
  function isInternal(a){
    return a.host === location.host && !a.hasAttribute('target');
  }
  document.addEventListener('click', (e)=>{
    const a = e.target.closest('a');
    if(!a || !isInternal(a)) return;
    if(a.getAttribute('href').startsWith('#')) return;
    e.preventDefault();
    overlay.classList.add('show');
    setTimeout(()=>{ window.location.href = a.href; }, 320);
  });
})();

// Command Palette (Ctrl+K)
(function(){
  const modal = document.getElementById('cmdp');
  const input = document.getElementById('cmdp-input');
  const results = document.getElementById('cmdp-results');
  if(!modal || !input || !results) return;
  const pages = [
    {k:'Home', t:'Page', url:'/'},
    {k:'Models', t:'Page', url:'/products'},
    {k:'Pricing', t:'Page', url:'/pricing'},
    {k:'Compare', t:'Page', url:'/compare'},
    {k:'Playground', t:'Page', url:'/playground'},
    {k:'Contact', t:'Page', url:'/contact'},
    {k:'Testimonials', t:'Page', url:'/testimonials'},
    {k:'Support', t:'Page', url:'/support'}
  ];
  let catalog = [];
  async function ensureCatalog(){
    if(catalog.length) return catalog;
    try{
      const r = await fetch('/api/catalog', {cache:'no-store'});
      const data = await r.json();
      if(Array.isArray(data)){
        catalog = data.map(p=>({k:p.name, t:(p.type||'model').toUpperCase(), url:`/product/${encodeURIComponent(p.id)}`}));
      }
    }catch(_){/* noop */}
    return catalog;
  }
  function open(){ modal.classList.add('open'); modal.setAttribute('aria-hidden','false'); setTimeout(()=> input.focus(), 10); input.select(); render(''); }
  function close(){ modal.classList.remove('open'); modal.setAttribute('aria-hidden','true'); input.value=''; results.innerHTML=''; }
  function itemTpl(it){ return `<div class="result" data-url="${it.url}"><span class="k">${it.k}</span><span class="t">${it.t}</span></div>` }
  async function render(q){
    const cats = await ensureCatalog();
    const pool = pages.concat(cats);
    const qq = (q||'').toLowerCase().trim();
    const list = qq ? pool.filter(x=> (x.k+" "+x.t).toLowerCase().includes(qq)) : pool.slice(0, 12);
    results.innerHTML = list.map(itemTpl).join('') || '<div class="muted">No results</div>';
  }
  input.addEventListener('input', (e)=> render(e.target.value));
  results.addEventListener('click', (e)=>{
    const row = e.target.closest('.result');
    if(!row) return;
    const url = row.getAttribute('data-url');
    if(url){ window.location.href = url; }
  });
  window.addEventListener('keydown', (e)=>{
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k'){
      e.preventDefault(); open();
    } else if(e.key === 'Escape'){
      if(modal.classList.contains('open')) close();
    }
  });
  window.CmdP = { open, close };
})();

// Back to top
(function(){
  const btn = document.getElementById('back-to-top');
  if(!btn) return;
  function onScroll(){ btn.style.display = window.scrollY > 400 ? 'inline-block' : 'none'; }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
  btn.addEventListener('click', ()=>{ window.scrollTo({ top:0, behavior:'smooth' }); });
})();

// Compare selection on /products
(function(){
  const bar = document.getElementById('compare-bar');
  const go = document.getElementById('compare-go');
  const clr = document.getElementById('compare-clear');
  const cnt = document.getElementById('compare-count');
  const checks = document.querySelectorAll('.compare-select');
  if(!bar || !go || !clr || checks.length===0) return;
  let selected = [];
  function sync(){
    cnt.textContent = `${selected.length} selected`;
    bar.classList.toggle('show', selected.length>0);
    go.disabled = !(selected.length===2);
  }
  function setCheckedFor(pid, checked){
    document.querySelectorAll(`.compare-select[value="${CSS.escape(pid)}"]`).forEach(c=> c.checked = checked);
  }
  checks.forEach(chk=>{
    // Prevent navigating when clicking the pill inside product-card link
    const label = chk.closest('label');
    if(label){ label.addEventListener('click', (e)=> e.stopPropagation()); }
    chk.addEventListener('change', ()=>{
      const pid = chk.value;
      const idx = selected.indexOf(pid);
      if(chk.checked){
        if(selected.length >= 2){
          // replace the first if it exists, or uncheck
          chk.checked = false; showToast('Pick at most 2'); return;
        }
        if(idx===-1) selected.push(pid);
      } else {
        if(idx!==-1) selected.splice(idx,1);
      }
      sync();
    });
  });
  go.addEventListener('click', ()=>{
    if(selected.length!==2) return;
    const [a,b] = selected;
    window.location.href = `/compare?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`;
  });
  clr.addEventListener('click', ()=>{ selected = []; document.querySelectorAll('.compare-select').forEach(c=> c.checked=false); sync(); });
  sync();
})();
