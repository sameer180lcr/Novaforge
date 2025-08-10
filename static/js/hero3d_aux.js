// Auxiliary 3D: glossy reactive surface with soft specular sweep
(function(){
  const wrap = document.getElementById('hero-3d-aux');
  if(!wrap || !window.THREE) return;
  const { Scene, PerspectiveCamera, WebGLRenderer, PlaneGeometry, ShaderMaterial, Mesh, Clock, sRGBEncoding, ACESFilmicToneMapping, Vector2 } = THREE;
  const scene = new Scene();
  const camera = new PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 3.1);
  const renderer = new WebGLRenderer({ antialias:true, alpha:true, powerPreference:'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputEncoding = sRGBEncoding;
  renderer.toneMapping = ACESFilmicToneMapping;
  wrap.appendChild(renderer.domElement);

  const geo = new PlaneGeometry(3.6, 2.0, 220, 140);
  const uniforms = {
    u_time: { value: 0 },
    u_mouse: { value: new Vector2(0.5,0.5) },
    u_aspect: { value: 1.0 },
  };

  const vert = `
    uniform float u_time; uniform vec2 u_mouse; varying vec3 vPos; varying vec2 vUv; varying float vSpec;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453123); }
    float noise(vec2 p){ vec2 i=floor(p); vec2 f=fract(p); float a=hash(i); float b=hash(i+vec2(1,0)); float c=hash(i+vec2(0,1)); float d=hash(i+vec2(1,1)); vec2 u=f*f*(3.-2.*f); return mix(a,b,u.x)+(c-a)*u.y*(1.-u.x)+(d-b)*u.x*u.y; }
    float fbm(vec2 p){ float v=0.; float a=.5; for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.02; a*=.5; } return v; }
    void main(){
      vUv = uv; vec3 pos = position; float t = u_time*0.3; vec2 p = uv*4.0 + vec2(t, -t);
      float n = fbm(p);
      float cursor = smoothstep(0.45, 0.0, distance(uv, u_mouse));
      float disp = n*0.35 + cursor*0.4;
      pos.z += disp;
      // fake spec based on gradient + cursor
      vSpec = smoothstep(0.6, 1.1, disp + cursor*0.5);
      vPos = pos; gl_Position = projectionMatrix * modelViewMatrix * vec4(pos,1.0);
    }`;
  const frag = `
    precision highp float; varying vec3 vPos; varying vec2 vUv; varying float vSpec;
    void main(){
      float vign = smoothstep(0.95, 0.4, length(vUv-0.5));
      vec3 base = vec3(0.98);
      vec3 col = base * (0.82 + 0.35*vSpec) * vign;
      gl_FragColor = vec4(col, 1.0);
    }`;

  const mat = new ShaderMaterial({ uniforms, vertexShader: vert, fragmentShader: frag });
  const mesh = new Mesh(geo, mat); scene.add(mesh);

  function resize(){ const r = wrap.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); camera.aspect = r.width/r.height; camera.updateProjectionMatrix(); uniforms.u_aspect.value = camera.aspect; }
  window.addEventListener('resize', resize); resize();

  const clock = new Clock();
  function tick(){ uniforms.u_time.value = clock.getElapsedTime(); renderer.render(scene, camera); requestAnimationFrame(tick); }
  requestAnimationFrame(tick);

  window.addEventListener('mousemove', (e)=>{ const r = wrap.getBoundingClientRect(); uniforms.u_mouse.value.set((e.clientX-r.left)/r.width, 1-(e.clientY-r.top)/r.height); });
})();
