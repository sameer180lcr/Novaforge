// Edge glow on product thumbnails using canvas filter effect
(function(){
  const cards = document.querySelectorAll('.product-card .product-media');
  cards.forEach(card =>{
    card.addEventListener('mousemove', (e)=>{
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left)/r.width; const y = (e.clientY - r.top)/r.height;
      const dx = Math.abs(x-0.5), dy = Math.abs(y-0.5);
      const edge = Math.max(0, 0.9 - Math.sqrt(dx*dx+dy*dy)*2.2);
      card.style.boxShadow = `inset 0 0 0 1px rgba(255,255,255,0.2), 0 0 28px rgba(255,255,255,${edge*0.35})`;
      card.style.transform = `translateY(-2px)`;
    });
    card.addEventListener('mouseleave', ()=>{
      card.style.boxShadow = 'inset 0 0 0 1px rgba(255,255,255,0.12)';
      card.style.transform = 'translateY(0)';
    });
  });
})();
