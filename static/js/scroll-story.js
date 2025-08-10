// Scroll-driven storytelling using GSAP ScrollTrigger
(function(){
  if(!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);

  // Pin the hero and gently animate the hero-3d plane depth on scroll
  const hero = document.querySelector('.hero');
  if(hero){
    gsap.to('.hero-3d', {
      duration: 1,
      ease: 'none',
      scrollTrigger: {
        trigger: hero,
        start: 'top top',
        end: '+=60%',
        scrub: 0.3,
        pin: true,
      },
      onUpdate: (self)=>{
        // Hook for further Three.js depth or uniform tweens if needed
        // e.g., window.__heroUniforms && (window.__heroUniforms.u_time.value += self.getVelocity())
      }
    })
  }

  // Reveal feature cards in sequence
  const cards = document.querySelectorAll('.feature-grid .card');
  cards.forEach((card, i)=>{
    gsap.fromTo(card, {y:30, opacity:0}, {
      y:0, opacity:1, duration:0.6, ease:'power2.out',
      scrollTrigger: { trigger: card, start: 'top 80%' }
    })
  });

  // Section head underline sweep
  document.querySelectorAll('.section-head h2').forEach(h=>{
    const line = document.createElement('span');
    line.style.display='block'; line.style.height='1px'; line.style.background='rgba(255,255,255,0.3)'; line.style.transform='scaleX(0)'; line.style.transformOrigin='left';
    h.parentElement.appendChild(line);
    gsap.to(line, {scaleX:1, duration:0.8, ease:'power2.out', scrollTrigger:{trigger:h, start:'bottom 90%'}})
  })
})();
