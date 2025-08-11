// Three.js 3D hero: shader plane with noise-driven displacement & rim glow
(function(){
  const wrap = document.getElementById('hero-3d');
  if(!wrap || !window.THREE) return;
  const { Scene, PerspectiveCamera, WebGLRenderer, PlaneGeometry, ShaderMaterial, Mesh, Clock, sRGBEncoding, ACESFilmicToneMapping, Vector2 } = THREE;

  const scene = new Scene();
  const camera = new PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 3.2);

  const renderer = new WebGLRenderer({ antialias:true, alpha:true, powerPreference:'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputEncoding = sRGBEncoding;
  renderer.toneMapping = ACESFilmicToneMapping;
  wrap.appendChild(renderer.domElement);

  const geo = new PlaneGeometry(3.8, 2.2, 240, 160);
  const uniforms = {
    u_time: { value: 0 },
    u_mouse: { value: new Vector2(0.0, 0.0) },
    u_aspect: { value: 1.0 },
  };

  const vert = `
    uniform float u_time; uniform vec2 u_mouse; varying vec3 vPos; varying vec3 vNorm; varying vec2 vUv;
    // Simple fbm noise
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453123); }
    float noise(vec2 p){
      vec2 i = floor(p); vec2 f = fract(p);
      float a = hash(i);
      float b = hash(i + vec2(1.0, 0.0));
      float c = hash(i + vec2(0.0, 1.0));
      float d = hash(i + vec2(1.0, 1.0));
      vec2 u = f*f*(3.0-2.0*f);
      return mix(a, b, u.x) + (c - a)*u.y*(1.0 - u.x) + (d - b)*u.x*u.y;
    }
    float fbm(vec2 p){ float v=0.0; float a=0.5; for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.02; a*=0.5; } return v; }
    void main(){
      vUv = uv;
      vec3 pos = position;
      vec2 p = uv * 4.0;
      float t = u_time*0.25;
      float wave = fbm(p + vec2(t, -t)) * 0.45;
      float cursor = smoothstep(0.35, 0.0, distance(uv, u_mouse));
      float disp = wave + cursor*0.35;
      pos.z += disp;
      vPos = pos; vNorm = normal;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos,1.0);
    }
  `;
  const frag = `
    precision highp float; varying vec3 vPos; varying vec3 vNorm; varying vec2 vUv;
    float rim(vec3 n, vec3 v){ return pow(1.0 - max(dot(normalize(n), normalize(v)), 0.0), 2.0); }
    void main(){
      vec3 base = vec3(1.0);
      float vign = smoothstep(0.95, 0.4, length(vUv-0.5));
      float r = rim(vNorm, vec3(0.0,0.0,1.0));
      vec3 col = base * (0.85 + 0.35*r) * vign;
      gl_FragColor = vec4(col, 1.0);
    }
  `;

  const mat = new ShaderMaterial({ uniforms, vertexShader: vert, fragmentShader: frag, wireframe:false });
  const mesh = new Mesh(geo, mat);
  scene.add(mesh);

  function resize(){
    const rect = wrap.getBoundingClientRect();
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
    uniforms.u_aspect.value = camera.aspect;
  }
  window.addEventListener('resize', resize);
  resize();

  const clock = new Clock();
  function tick(){
    uniforms.u_time.value = clock.getElapsedTime();
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  window.addEventListener('mousemove', (e)=>{
    const rect = wrap.getBoundingClientRect();
    uniforms.u_mouse.value.x = (e.clientX - rect.left) / rect.width;
    uniforms.u_mouse.value.y = 1.0 - (e.clientY - rect.top) / rect.height;
  });
})();
