/* Robots hero: lightweight Three.js scene with simple animated robots */
(function(){
  const mount = document.getElementById('hero-3d-robots');
  if(!mount || !window.THREE) return;
  const W = mount.clientWidth || 800;
  const H = mount.clientHeight || 360;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, W/H, 0.1, 100);
  camera.position.set(0.8, 0.9, 4.2);

  const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(W, H);
  mount.appendChild(renderer.domElement);

  // Lighting suitable for light theme
  const hemi = new THREE.HemisphereLight(0xffffff, 0xe9ecf1, 0.8);
  scene.add(hemi);
  const dir = new THREE.DirectionalLight(0xffffff, 0.6);
  dir.position.set(2, 3, 2);
  scene.add(dir);

  // Floor grid (subtle)
  const grid = new THREE.GridHelper(16, 24, 0xCBD5E1, 0xE5E7EB);
  grid.position.y = -1.1;
  scene.add(grid);

  const robots = new THREE.Group();
  scene.add(robots);

  // Industry pods group: showcases AI across verticals
  const pods = new THREE.Group();
  scene.add(pods);

  function makeLabelCanvas(text){
    const c = document.createElement('canvas');
    const ctx = c.getContext('2d');
    const pad = 12; const fs = 28; const font = `600 ${fs}px Inter, Arial`;
    ctx.font = font;
    const w = Math.ceil(ctx.measureText(text).width) + pad*2;
    const h = fs + pad*2;
    c.width = w; c.height = h;
    ctx.fillStyle = 'rgba(255,255,255,0.95)';
    ctx.strokeStyle = 'rgba(0,0,0,0.08)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const r = 16; // rounded rect
    ctx.moveTo(r,0); ctx.lineTo(w-r,0); ctx.quadraticCurveTo(w,0,w,r);
    ctx.lineTo(w,h-r); ctx.quadraticCurveTo(w,h,w-r,h);
    ctx.lineTo(r,h); ctx.quadraticCurveTo(0,h,0,h-r);
    ctx.lineTo(0,r); ctx.quadraticCurveTo(0,0,r,0);
    ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = '#0b0b0b';
    ctx.font = font;
    ctx.fillText(text, pad, fs + (pad/3));
    const tex = new THREE.CanvasTexture(c);
    tex.minFilter = THREE.LinearFilter; tex.magFilter = THREE.LinearFilter;
    const mat = new THREE.SpriteMaterial({map: tex, transparent: true});
    const spr = new THREE.Sprite(mat);
    const scale = 0.0075; // scale canvas px to world units
    spr.scale.set(c.width*scale, c.height*scale, 1);
    return spr;
  }

  function makePod(name, color, build){
    const g = new THREE.Group();
    // base platform
    const base = new THREE.Mesh(new THREE.CylinderGeometry(0.6,0.6,0.08, 40), new THREE.MeshStandardMaterial({color:0xE5E7EB, metalness:0.1, roughness:0.6}));
    base.position.y = -0.88;
    g.add(base);
    // content
    const content = new THREE.Group();
    build(content, color);
    g.add(content);
    // label
    const label = makeLabelCanvas(name);
    label.position.set(0, 0.65, 0);
    g.add(label);
    // subtle glow ring
    const ringGeo = new THREE.RingGeometry(0.68, 0.72, 40);
    const ringMat = new THREE.MeshBasicMaterial({color: 0x60a5fa, opacity:0.25, transparent:true});
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI/2; ring.position.y = -0.84;
    g.add(ring);
    g.userData = {content, label};
    return g;
  }

  // Builders for each industry
  function buildHealthcare(parent, color){
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.26, 24, 18), new THREE.MeshStandardMaterial({color, metalness:0.15, roughness:0.35}));
    parent.add(body);
    const crossMat = new THREE.MeshStandardMaterial({color:0x2563eb, metalness:0.1, roughness:0.4});
    const bar1 = new THREE.Mesh(new THREE.BoxGeometry(0.36,0.08,0.08), crossMat);
    const bar2 = new THREE.Mesh(new THREE.BoxGeometry(0.08,0.36,0.08), crossMat);
    parent.add(bar1,bar2);
  }
  function buildManufacturing(parent, color){
    const gear = new THREE.Mesh(new THREE.TorusGeometry(0.28,0.08, 12, 32), new THREE.MeshStandardMaterial({color, metalness:0.25, roughness:0.25}));
    gear.rotation.x = Math.PI/2; parent.add(gear);
    for(let i=0;i<6;i++){ const tooth = new THREE.Mesh(new THREE.BoxGeometry(0.14,0.06,0.12), gear.material); tooth.position.set(Math.cos(i*Math.PI/3)*0.28, 0.0, Math.sin(i*Math.PI/3)*0.28); parent.add(tooth);}    
  }
  function buildRetail(parent, color){
    const bag = new THREE.Mesh(new THREE.BoxGeometry(0.36,0.34,0.2), new THREE.MeshStandardMaterial({color, metalness:0.1, roughness:0.5}));
    bag.position.y = 0.05; parent.add(bag);
    const handle = new THREE.Mesh(new THREE.TorusGeometry(0.12,0.02, 12, 24), new THREE.MeshStandardMaterial({color:0x2563eb, metalness:0.2, roughness:0.3}));
    handle.position.set(0, 0.26, 0.1); parent.add(handle);
  }
  function buildLogistics(parent, color){
    const truck = new THREE.Group(); parent.add(truck);
    const cab = new THREE.Mesh(new THREE.BoxGeometry(0.22,0.18,0.2), new THREE.MeshStandardMaterial({color:0x2563eb, metalness:0.2, roughness:0.3})); cab.position.set(-0.18, -0.02, 0); truck.add(cab);
    const box = new THREE.Mesh(new THREE.BoxGeometry(0.38,0.2,0.22), new THREE.MeshStandardMaterial({color, metalness:0.1, roughness:0.5})); box.position.set(0.12, -0.01, 0); truck.add(box);
    const wheelMat = new THREE.MeshStandardMaterial({color:0x111827, metalness:0.4, roughness:0.4});
    for(const x of [-0.24, -0.06, 0.16]){ const w = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,0.08, 16), wheelMat); w.rotation.z = Math.PI/2; w.position.set(x, -0.14, 0.12); truck.add(w); const w2 = w.clone(); w2.position.z = -0.12; truck.add(w2);}    
  }
  function buildFinance(parent, color){
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.12,0.36), new THREE.MeshStandardMaterial({color, metalness:0.1, roughness:0.5})); base.position.y = -0.06; parent.add(base);
    const colMat = new THREE.MeshStandardMaterial({color:0xffffff, metalness:0.0, roughness:0.6});
    for(const x of [-0.16,-0.05,0.06,0.17]){ const c = new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,0.28, 20), colMat); c.position.set(x, 0.06, 0); parent.add(c); }
    const roof = new THREE.Mesh(new THREE.ConeGeometry(0.33,0.2, 4), new THREE.MeshStandardMaterial({color:0x111827, metalness:0.1, roughness:0.5})); roof.rotation.y = Math.PI/4; roof.position.y = 0.28; parent.add(roof);
  }

  // Create pods arranged in an arc
  const podDefs = [
    {name:'Healthcare', color:0xf8fafc, build:buildHealthcare},
    {name:'Manufacturing', color:0xf3f4f6, build:buildManufacturing},
    {name:'Retail', color:0xffffff, build:buildRetail},
    {name:'Logistics', color:0xf9fafb, build:buildLogistics},
    {name:'Finance', color:0xf5f5f5, build:buildFinance},
  ];
  const radius = 2.4;
  podDefs.forEach((d,i)=>{
    const pod = makePod(d.name, d.color, d.build);
    const a = (-Math.PI/3) + (i*(Math.PI/6));
    pod.position.set(Math.cos(a)*radius, 0, Math.sin(a)*radius);
    pod.lookAt(0, -0.5, 0);
    pods.add(pod);
  });

  function makeRobot(color){
    const g = new THREE.Group();
    // body
    const body = new THREE.Mesh(
      new THREE.BoxGeometry(0.6, 0.8, 0.35, 1,1,1),
      new THREE.MeshStandardMaterial({color, metalness:0.1, roughness:0.35})
    );
    body.position.y = -0.1;
    g.add(body);
    // head
    const head = new THREE.Mesh(
      new THREE.SphereGeometry(0.22, 20, 16),
      new THREE.MeshStandardMaterial({color: 0x2563eb, metalness:0.2, roughness:0.25})
    );
    head.position.y = 0.45;
    g.add(head);
    // eyes (emissive)
    const eyeMat = new THREE.MeshBasicMaterial({color:0xffffff});
    const eye = new THREE.Mesh(new THREE.BoxGeometry(0.12,0.05,0.02), eyeMat);
    eye.position.set(0, 0.47, 0.19);
    g.add(eye);
    // arms
    const armMat = new THREE.MeshStandardMaterial({color:0x1f2937, metalness:0.1, roughness:0.4});
    const armL = new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,0.5, 10), armMat);
    const armR = armL.clone();
    armL.position.set(-0.42, 0.05, 0);
    armR.position.set(0.42, 0.05, 0);
    g.add(armL, armR);
    // legs
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,0.55, 10), armMat);
    const leg2 = leg.clone();
    leg.position.set(-0.18, -0.65, 0);
    leg2.position.set(0.18, -0.65, 0);
    g.add(leg, leg2);
    // simple tool
    const tool = new THREE.Mesh(new THREE.TorusGeometry(0.12,0.03,16,24), new THREE.MeshStandardMaterial({color:0x60a5fa, metalness:0.3, roughness:0.2}));
    tool.position.set(0.6, 0.1, 0.2);
    g.add(tool);
    // anim state
    g.userData = {armL, armR, tool};
    return g;
  }

  // Setup primitive robots (fallback)
  const writer = makeRobot(0xffffff); writer.position.set(-1.6, -0.2, 0); robots.add(writer);
  const runner = makeRobot(0xf3f4f6); runner.position.set(0, -0.2, -0.2); robots.add(runner);
  const chef   = makeRobot(0xffffff); chef.position.set(1.6, -0.2, 0.1); robots.add(chef);

  // Try to load a humanoid GLB (e.g., Optimus-like). Place file at /static/models/optimus.glb
  if (THREE.GLTFLoader){
    try{
      const loader = new THREE.GLTFLoader();
      loader.load('/static/models/optimus.glb', (gltf)=>{
        // Clear primitives
        robots.clear();
        const base = gltf.scene;
        base.traverse((o)=>{ if(o.isMesh){ o.castShadow=false; o.receiveShadow=false; o.material.depthWrite=true; }});
        base.scale.set(0.9,0.9,0.9);
        // Clone three variants
        const a = base.clone(); a.position.set(-1.6, -0.8, 0); a.rotation.y = Math.PI*0.06; robots.add(a);
        const b = base.clone(); b.position.set(0, -0.8, -0.2); b.rotation.y = -Math.PI*0.06; robots.add(b);
        const c = base.clone(); c.position.set(1.6, -0.8, 0.1); c.rotation.y = Math.PI*0.12; robots.add(c);
        // Simple bob animations handled in animate() by mutating a/b/c
        robots.userData.models = {a,b,c};
      }, undefined, (err)=>{
        // keep fallback
        console.warn('GLB load failed', err);
      });
    }catch(e){ console.warn('GLTF loader error', e); }
  }

  // Props: desk and kitchen counter
  const desk = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.06, 0.6), new THREE.MeshStandardMaterial({color:0xE5E7EB, metalness:0.05, roughness:0.7}));
  desk.position.set(-1.6, -0.55, 0);
  scene.add(desk);
  const counter = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.06, 0.6), new THREE.MeshStandardMaterial({color:0xE5E7EB, metalness:0.05, roughness:0.7}));
  counter.position.set(1.6, -0.55, 0);
  scene.add(counter);

  let t = 0;
  function animate(){
    requestAnimationFrame(animate);
    t += 0.02;
    // If GLB loaded, do subtle bob and idle rotations on clones
    const mdl = robots.userData.models;
    if(mdl){
      mdl.a.position.y = -0.8 + Math.sin(t*1.3)*0.02;
      mdl.b.position.y = -0.8 + Math.sin(t*1.5 + 1.2)*0.02;
      mdl.c.position.y = -0.8 + Math.sin(t*1.1 + 2.1)*0.02;
      mdl.a.rotation.y += 0.002;
      mdl.b.rotation.y -= 0.002;
      mdl.c.rotation.y += 0.003;
    } else {
      // fallback primitive animations
      const wa = writer.userData; if(wa){ wa.armL.rotation.x = Math.sin(t*8)*0.6 - 0.4; wa.armR.rotation.x = Math.cos(t*8)*0.6 - 0.4; }
      const ra = runner.userData; if(ra){ runner.position.x = Math.sin(t)*0.6; ra.armL.rotation.x = Math.sin(t*10)*0.8; ra.armR.rotation.x = Math.cos(t*10)*0.8; }
      const ca = chef.userData;   if(ca){ ca.tool.rotation.z = t*3; ca.armR.rotation.x = Math.sin(t*5)*0.5; ca.armL.rotation.x = Math.cos(t*5)*0.3; }
      robots.rotation.y = Math.sin(t*0.1)*0.06;
    }
    // Animate pods: gentle hover and label sway
    pods.children.forEach((pod, idx)=>{
      const tt = t + idx*0.6;
      pod.position.y = Math.sin(tt*1.2)*0.025;
      pod.userData.content.rotation.y = Math.sin(tt*0.7)*0.15;
      if(pod.userData.label){ pod.userData.label.position.y = 0.65 + Math.sin(tt*0.9)*0.02; }
    });
    renderer.render(scene, camera);
  }
  animate();

  // Pointer parallax
  mount.addEventListener('mousemove', (e)=>{
    const r = mount.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    camera.position.x = 0.8 + x * 0.8;
    camera.position.y = 0.9 - y * 0.6;
    camera.lookAt(0, -0.2, 0);
  });

  // Resize
  const ro = new ResizeObserver(()=>{
    const w = mount.clientWidth || W;
    const h = mount.clientHeight || H;
    renderer.setSize(w, h);
    camera.aspect = w/h;
    camera.updateProjectionMatrix();
  });
  ro.observe(mount);
})();
