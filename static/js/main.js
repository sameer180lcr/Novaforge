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
