// GPU-friendly particle field with line connections
(function(){
  const canvas = document.getElementById('bg-canvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  let dpr = Math.min(window.devicePixelRatio || 1, 2);
  let w, h, particles = [], lastT = 0;
  const PCOUNT = 120; // balanced for perf

  function resize(){
    w = window.innerWidth; h = window.innerHeight;
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    canvas.width = Math.floor(w * dpr); canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function rand(a,b){ return a + Math.random()*(b-a); }

  function init(){
    particles = new Array(PCOUNT).fill(0).map(()=>({
      x: rand(0,w), y: rand(0,h),
      vx: rand(-0.15,0.15), vy: rand(-0.15,0.15),
      r: rand(0.6, 1.6),
    }));
  }

  function step(dt){
    ctx.clearRect(0,0,w,h);
    // draw connections
    for(let i=0;i<particles.length;i++){
      const a = particles[i];
      for(let j=i+1;j<particles.length;j++){
        const b = particles[j];
        const dx=a.x-b.x, dy=a.y-b.y; const d2 = dx*dx+dy*dy;
        if(d2 < 140*140){
          const alpha = Math.max(0, 1 - Math.sqrt(d2)/140) * 0.15;
          ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
        }
      }
    }
    // draw particles
    particles.forEach(p=>{
      p.x += p.vx * dt * 0.06; p.y += p.vy * dt * 0.06;
      if(p.x < -20) p.x = w+20; if(p.x > w+20) p.x = -20;
      if(p.y < -20) p.y = h+20; if(p.y > h+20) p.y = -20;
      const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 16);
      g.addColorStop(0, 'rgba(255,255,255,0.35)');
      g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, p.r*2, 0, Math.PI*2); ctx.fill();
    });
  }

  function animate(t){
    if(!lastT) lastT = t; const dt = Math.min(32, t - lastT); lastT = t;
    step(dt); requestAnimationFrame(animate);
  }

  resize(); init(); requestAnimationFrame(animate);
  window.addEventListener('resize', ()=>{ resize(); init(); });
})();
