(function(){
  if(!window.Chart) return;

  function mkBar(ctx, cfg){
    return new Chart(ctx, {
      type: 'bar',
      data: { labels: cfg.labels, datasets: [{ label: cfg.title, data: cfg.data, borderRadius: 6, backgroundColor: '#64d2ff' }] },
      options: {
        responsive: true,
        plugins: { legend: { display:false }, title:{ display:false } },
        scales: { x:{ grid:{ display:false } }, y:{ grid:{ color:'#eee' }, beginAtZero:true } }
      }
    });
  }

  function mkLine(ctx, cfg){
    return new Chart(ctx, {
      type: 'line',
      data: { labels: cfg.labels, datasets: [{ label: cfg.title, data: cfg.data, borderColor: '#a78bfa', backgroundColor: 'rgba(167,139,250,0.15)', fill:true, tension:0.35 }] },
      options: {
        responsive: true,
        plugins: { legend: { display:false }, title:{ display:false } },
        scales: { x:{ grid:{ display:false } }, y:{ grid:{ color:'#eee' }, beginAtZero:true } }
      }
    });
  }

  function mkRadar(ctx, cfg){
    return new Chart(ctx, {
      type: 'radar',
      data: { labels: cfg.labels, datasets: [{ label: cfg.title, data: cfg.data, borderColor:'#64d2ff', backgroundColor:'rgba(100,210,255,0.2)', pointBackgroundColor:'#64d2ff' }] },
      options: { responsive:true, plugins:{ legend:{ display:false } } }
    });
  }

  let charts = window.industryCharts;
  if(!charts){
    const dataEl = document.getElementById('charts-data');
    if(dataEl){
      try { charts = JSON.parse(dataEl.textContent || '{}'); }
      catch(e){ charts = {}; }
    } else {
      charts = {};
    }
  }
  Object.keys(charts).forEach((key)=>{
    const cfg = charts[key];
    const el = document.getElementById('chart-'+key);
    if(!cfg || !el) return;
    const type = (cfg.type||'').toLowerCase();
    const ctx = el.getContext('2d');
    if(type === 'line') return mkLine(ctx, cfg);
    if(type === 'radar') return mkRadar(ctx, cfg);
    return mkBar(ctx, cfg);
  });
})();
