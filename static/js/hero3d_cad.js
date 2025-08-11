/* Lightweight CAD-like wireframe viewer for #hero-3d-cad */
(function(){
  const mount = document.getElementById('hero-3d-cad');
  if(!mount) return;
  const W = mount.clientWidth || mount.offsetWidth || 600;
  const H = mount.clientHeight || 360;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, W/H, 0.1, 100);
  camera.position.set(0.8, 0.8, 3.2);

  const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(W, H);
  mount.appendChild(renderer.domElement);

  // Grid + axes feel (subtle, light theme aware)
  const grid = new THREE.GridHelper(10, 20, 0xCBD5E1, 0xE5E7EB);
  grid.position.y = -1.1;
  scene.add(grid);

  // Wireframe objects
  const group = new THREE.Group();
  scene.add(group);

  const mat = new THREE.MeshBasicMaterial({color: 0x2563eb, wireframe:true});
  const geo1 = new THREE.TorusKnotGeometry(0.6, 0.18, 160, 24);
  const knot = new THREE.Mesh(geo1, mat);
  group.add(knot);

  const geo2 = new THREE.BoxGeometry(1.1, 0.4, 0.8, 8, 2, 6);
  const box = new THREE.Mesh(geo2, new THREE.MeshBasicMaterial({color: 0x1f2937, wireframe:true}));
  box.position.set(-1.2, -0.2, 0);
  group.add(box);

  const ambient = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambient);

  let t = 0;
  function animate(){
    requestAnimationFrame(animate);
    t += 0.01;
    knot.rotation.x = t * 0.8;
    knot.rotation.y = t * 0.6;
    box.rotation.y = t * 0.3;
    group.rotation.z = Math.sin(t*0.3)*0.05;
    renderer.render(scene, camera);
  }
  animate();

  // Resize handling
  const ro = new ResizeObserver(()=>{
    const w = mount.clientWidth;
    const h = mount.clientHeight || (mount.getBoundingClientRect().width * 0.6);
    renderer.setSize(w, h);
    camera.aspect = w/h;
    camera.updateProjectionMatrix();
  });
  ro.observe(mount);

  // Cursor parallax
  mount.addEventListener('mousemove', (e)=>{
    const r = mount.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    camera.position.x = 0.8 + x * 0.6;
    camera.position.y = 0.8 - y * 0.6;
    camera.lookAt(0,0,0);
  });
})();
