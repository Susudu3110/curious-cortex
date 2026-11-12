// WHY YOUR BRAIN ONLY CRINGES AT 3 AM — shot list (Deep Dive 3D).
// Worlds: (A) night bedroom, (B) x-ray body + glowing brain, (C) inside the brain (neuron macro).
// A shot: { id, at, note, draw(lt, d, t, blit) }. cut(i) = just before line i, Wd('word', i) = when that word is said.
import * as THREE from 'three';
import { ctx, W, H, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import { camera, lightRig } from './core/engine.js';
import { Human } from './core/human.js';
import * as SETS from './core/sets.js';
import { label, pill, warning } from './core/look2d.js';
import { ellipsoid, capsule, rbox, smin, smax, ssub, sphere, mesh, noise3, rgb } from './core/sdf.js';

const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const lerpV = (a, b, k) => a.clone().lerp(b, k);
function screen(p, cam) { const v = p.clone().project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }
const std = (color, rough = 0.7, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: rough, ...extra });
const shadowed = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
function sdfMesh(f, b, step, mat) { return shadowed(new THREE.Mesh(mesh(f, b, step), mat)); }
function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }

// ── sculpted brain (shared geometry, built once) ──────────────────────────
let _brainGeo = null;
function brainGeo() {
  if (_brainGeo) return _brainGeo;
  const folds = (p) => 0.0035 * Math.sin(p[0] * 62) * Math.sin(p[2] * 54 + p[1] * 30) + 0.0025 * Math.sin(p[1] * 78 + p[0] * 40);
  const f = (p) => {
    let d = ellipsoid(p, [0, 0.02, -0.005], [0.105, 0.082, 0.115]);
    d = smin(d, ellipsoid(p, [0, 0.06, 0.05], [0.088, 0.055, 0.06]), 0.05);            // frontal lobe
    d = smin(d, ellipsoid(p, [0, 0.05, -0.07], [0.08, 0.05, 0.05]), 0.05);             // occipital
    d = smin(d, ellipsoid(p, [0, -0.075, -0.025], [0.055, 0.032, 0.05]), 0.025);       // cerebellum
    d = smin(d, capsule(p, [0, -0.055, 0.03], [0, -0.115, 0.06], 0.016), 0.012);       // brainstem
    d += folds(p) * 0.9 + 0.0022 * noise3(p[0] * 42, p[1] * 42, p[2] * 42);             // cortex grooves + organic wobble
    return d;
  };
  const P = rgb('#D98CA0'), DK = rgb('#B06A80');
  _brainGeo = mesh(f, [[-0.12, -0.13, -0.15], [0.12, 0.13, 0.16]], 0.0035, (p) => {
    const n = 0.5 + 0.5 * noise3(p[0] * 30, p[1] * 30, p[2] * 30);
    return [P[0] + (DK[0] - P[0]) * n, P[1] + (DK[1] - P[1]) * n, P[2] + (DK[2] - P[2]) * n];
  });
  return _brainGeo;
}
function brainMesh(scale = 1) {
  const mat = new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.45, clearcoat: 0.5, clearcoatRoughness: 0.4, emissive: new THREE.Color('#C4607E'), emissiveIntensity: 0.12 });
  const g = new THREE.Group();
  const m = new THREE.Mesh(brainGeo(), mat); m.scale.setScalar(scale); m.castShadow = true; g.add(m);
  const amg = [];
  for (const s of [-1, 1]) {
    const a = new THREE.Mesh(new THREE.SphereGeometry(0.016 * scale, 20, 14), new THREE.MeshStandardMaterial({ color: '#FF4D4D', emissive: '#FF2E2E', emissiveIntensity: 0.9, roughness: 0.3 }));
    a.position.set(s * 0.032 * scale, 0.01 * scale, 0.055 * scale); g.add(a); amg.push(a);
  }
  return { group: g, mat, amg };
}

// ── NIGHT BEDROOM ─────────────────────────────────────────────────────────
function bedroom(E) {
  const scene = new THREE.Scene();
  scene.environment = E.envMap; scene.environmentIntensity = 0.06;
  scene.background = new THREE.Color('#0A0E1C'); scene.fog = new THREE.Fog('#0A0E1C', 6, 18);
  const floor = shadowed(new THREE.Mesh(new THREE.PlaneGeometry(16, 16), std('#3A3446', 0.8))); floor.rotation.x = -Math.PI / 2; scene.add(floor);
  const wallM = std('#262C44', 0.9);
  const back = shadowed(new THREE.Mesh(new THREE.BoxGeometry(16, 5, 0.2), wallM)); back.position.set(0, 2.5, -2.6); scene.add(back);
  const side = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.2, 5, 10), wallM)); side.position.set(-3.4, 2.5, 1); scene.add(side);
  // window with night sky (material animates day/night)
  const skyMat = new THREE.MeshBasicMaterial({ color: '#0B1830' });
  const sky = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.35), skyMat); sky.position.set(1.6, 2.1, -2.49); scene.add(sky);
  const stars = canvasTex(256, 256, (g) => { g.fillStyle = '#0B1830'; g.fillRect(0, 0, 256, 256); for (let i = 0; i < 90; i++) { const x = Math.random() * 256, y = Math.random() * 256, r = Math.random() * 1.6 + 0.4; g.fillStyle = `rgba(230,240,255,${0.3 + Math.random() * 0.7})`; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); } });
  const skyN = new THREE.MeshBasicMaterial({ map: stars, transparent: true, opacity: 1 });
  const skyNMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.69, 1.34), skyN); skyNMesh.position.set(1.6, 2.1, -2.485); scene.add(skyNMesh);
  const frM = std('#4A4358', 0.5); for (const [w, h, x, y] of [[1.85, 0.08, 1.6, 2.82], [1.85, 0.08, 1.6, 1.38], [0.08, 1.52, 0.66, 2.1], [0.08, 1.52, 2.54, 2.1]]) { const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.12), frM)); b.position.set(x, y, -2.5); scene.add(b); }
  // bed: frame + mattress + sculpted duvet + pillows
  const bed = new THREE.Group(); scene.add(bed);
  const wood = std('#6B4A36', 0.6);
  bed.add(shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.22, 2.5), wood))).children.at(-1).position.set(0, 0.11, 0);
  const headboard = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.85, 0.12), wood)); headboard.position.set(0, 0.6, -1.28); bed.add(headboard);
  const matt = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.28, 0.2, 2.36), std('#E8E4DC', 0.8))); matt.position.set(0, 0.32, 0); bed.add(matt);
  const duvet = sdfMesh((p) => { let d = rbox(p, [0, 0.12, 0.1], [0.62, 0.09, 0.95], 0.09); d += 0.02 * noise3(p[0] * 6, p[1] * 8, p[2] * 6); return d; }, [[-0.66, -0.02, -0.95], [0.66, 0.28, 1.12]], 0.02, std('#5A6480', 0.85)); duvet.position.set(0, 0.42, 0.12); bed.add(duvet);
  for (const s of [-1, 1]) { const pil = sdfMesh((p) => { let d = ellipsoid(p, [0, 0, 0], [0.30, 0.08, 0.20]); d += 0.008 * noise3(p[0] * 14, p[1] * 14, p[2] * 14); return d; }, [[-0.34, -0.1, -0.24], [0.34, 0.1, 0.24]], 0.015, std('#EFEAE0', 0.9)); pil.position.set(s * 0.3, 0.52, -0.95); bed.add(pil); }
  // nightstand + phone (glowing screen + its light)
  const stand = shadowed(new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.5, 0.42), std('#4A3A55', 0.7))); stand.position.set(1.0, 0.25, -1.05); scene.add(stand);
  const phone = new THREE.Mesh(new THREE.BoxGeometry(0.075, 0.16, 0.008), new THREE.MeshBasicMaterial({ color: '#BFE3FF' })); phone.position.set(1.0, 0.56, -0.84); phone.rotation.x = 0.5; scene.add(phone);
  const pLight = new THREE.PointLight('#BFD9FF', 3.2, 2.4, 1.6); pLight.position.set(1.0, 0.62, -0.8); scene.add(pLight);
  const moon = lightRig(scene, { key: '#9FB8E8', keyI: 2.4, keyPos: [2.8, 3.4, -3.4], target: [0, 0.9, 0], rimCol: '#5A6F9E', rimI: 0.9, sky: '#3A4468', ground: '#221E2E', hemiI: 0.55, shadowBox: 3 });
  const sun = new THREE.DirectionalLight('#FFE2B8', 0); sun.position.set(-2.4, 3.6, 1.6); scene.add(sun);
  const dayFill = new THREE.HemisphereLight('#FFF4E2', '#6B5A48', 0);
  scene.add(dayFill);
  const lights = { moon, sun, dayFill, skyN, skyMat, phone, pLight };
  return {
    scene, lights,
    /** day 0..1: swap moonlight for morning sun, night sky for bright sky, screen off */
    update(day) {
      moon.key.intensity = lerp(2.4, 0.25, day); moon.rim.intensity = lerp(0.9, 0.2, day);
      sun.intensity = 5.2 * day; dayFill.intensity = 1.4 * day;
      skyN.opacity = 1 - day; skyMat.color.set('#0B1830').lerp(new THREE.Color('#CFE8FA'), day);
      scene.background = new THREE.Color('#0A0E1C').lerp(new THREE.Color('#E8DCCB'), day);
      scene.fog.color.copy(scene.background);
      pLight.intensity = lerp(3.2, 0, day); phone.material.color.set('#BFE3FF').lerp(new THREE.Color('#33445A'), day);
      scene.environmentIntensity = lerp(0.06, 0.3, day);
    },
  };
}

// ── X-RAY STAGE (with glowing brain in the head) ──────────────────────────
function xray(E) {
  const X = SETS.xrayStage(E);
  const xh = new Human({ face: false });
  const xmat = SETS.xrayMaterial();
  xh.setBodyMaterial(xmat);
  xh.parts.filter((p) => p.parent === xh.head).forEach((p) => { p.material = xmat; p.castShadow = false; });
  xh.group.position.set(0, 0, 0); X.scene.add(xh.group);
  const br = brainMesh(1.0); br.group.position.set(0, 1.70, 0); X.scene.add(br.group);
  return { scene: X.scene, xh, xmat, br, update() {} };
}

// ── INSIDE THE BRAIN (neuron macro world) ─────────────────────────────────
function neuro(E) {
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#2A0510'); scene.fog = new THREE.FogExp2('#3A0812', 0.14);
  scene.add(new THREE.HemisphereLight('#FF8A9A', '#30030A', 0.7));
  const l1 = new THREE.PointLight('#FFB0A0', 13, 10, 1.6); scene.add(l1);
  // neurons: nodes + links
  const nodes = [[0, 0, 0, 0.30], [0.9, 0.5, -0.6, 0.14], [-0.8, 0.3, -0.9, 0.12], [0.5, -0.6, -1.1, 0.13], [-0.5, -0.5, -0.4, 0.11], [1.2, -0.2, -1.6, 0.15], [-1.1, -0.15, -1.5, 0.12], [0.15, 0.8, -1.5, 0.12], [1.0, 0.9, -2.3, 0.14], [-0.4, 1.0, -2.4, 0.11], [0.6, 0.2, -2.8, 0.13], [-1.0, 0.6, -2.9, 0.12]];
  const nodeM = [], NM = new THREE.MeshPhysicalMaterial({ color: '#FF6E8A', roughness: 0.35, clearcoat: 0.7, emissive: '#FF4E6E', emissiveIntensity: 0.35 });
  nodes.forEach(([x, y, z, r], i) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16), NM.clone()); m.position.set(x, y, z); scene.add(m); nodeM.push(m); });
  const linkM = new THREE.MeshPhysicalMaterial({ color: '#B8283A', roughness: 0.4, emissive: '#5A0A18', emissiveIntensity: 0.5 });
  const links = [[0, 1], [0, 2], [0, 4], [1, 3], [2, 4], [1, 5], [2, 6], [0, 7], [5, 8], [7, 8], [7, 9], [5, 10], [8, 10], [6, 11]];
  links.forEach(([a, b]) => {
    const va = new THREE.Vector3(...nodes[a].slice(0, 3)), vb = new THREE.Vector3(...nodes[b].slice(0, 3));
    const mid = va.clone().add(vb).multiplyScalar(0.5), len = va.distanceTo(vb);
    const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, len, 12), linkM);
    cyl.position.copy(mid); cyl.lookAt(vb); cyl.rotateX(Math.PI / 2); scene.add(cyl);
  });
  const mem = nodeM[0], win = nodeM[4], pain = nodeM[3];
  win.material = new THREE.MeshPhysicalMaterial({ color: '#7CF29A', roughness: 0.35, emissive: '#3ED472', emissiveIntensity: 0.5 });
  pain.material = new THREE.MeshPhysicalMaterial({ color: '#FFF0F0', roughness: 0.2, clearcoat: 1, emissive: '#FFFFFF', emissiveIntensity: 0.25 });
  // travelling signal
  const sig = new THREE.Mesh(new THREE.SphereGeometry(0.09, 18, 12), new THREE.MeshBasicMaterial({ color: '#FFD0D8' })); sig.visible = false; scene.add(sig);
  const memP = new THREE.Vector3(), painP = new THREE.Vector3();
  return {
    scene, light: l1,
    update(t, { fire = 0, signal = 0, winDim = 0 } = {}) {
      nodeM.forEach((m, i) => { m.material.emissiveIntensity = 0.16 + 0.13 * Math.sin(t * 2.6 + i * 1.7); });
      win.material.emissiveIntensity = lerp(0.5, 0.03, winDim); win.material.color.lerpColors(new THREE.Color('#7CF29A'), new THREE.Color('#5A3A4A'), winDim);
      mem.material.emissiveIntensity = 0.25 + fire * 0.95 * (0.6 + 0.4 * Math.sin(t * 9));
      mem.material.color.set('#FF4E6E').lerp(new THREE.Color('#FF2020'), fire);
      pain.material.emissiveIntensity = 0.18 + signal * 1.15;
      sig.visible = signal > 0.001;
      memP.set(...nodes[0].slice(0, 3)); painP.set(...nodes[3].slice(0, 3));
      sig.position.lerpVectors(memP, painP, signal);
      l1.position.set(0.3, 0.4, -0.6 - signal * 0.8);
    },
  };
}

export function buildShots(E) {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.08);
  const cam = camera(30);
  const BLOOK = { aperture: 0.004, maxblur: 0.012, bloom: 0.25, vignette: 0.5 };
  const XLOOK = { aperture: 0.0015, bloom: 0.55, bloomThreshold: 0.4, vignette: 0.45 };
  const NLOOK = { aperture: 0.005, maxblur: 0.014, bloom: 0.32, bloomThreshold: 0.68, focus: 2.6 };

  const BED = bedroom(E), hero = new Human({});
  const X = xray(E);
  const NR = neuro(E);
  const CYAN = new THREE.Color('#4FD1E8'), RED = new THREE.Color('#FF3B3B');

  // person sitting in bed: seat top 0.42 → hips 0.66 above seat
  const SEAT = 0.42, SITZ = -0.35;
  hero.group.position.set(0, SEAT, SITZ); BED.scene.add(hero.group);
  hero.hips.position.y = 0.66;
  const sitPose = (q = {}) => { hero.hips.position.y = 0.66; hero.pose({ hipL: [86, 0, 4], hipR: [88, 0, 4], knL: 86, knR: 88, elL: 24, elR: 24, shL: [8, 0, 8], shR: [8, 0, 8], ...q }); };
  const FACE = V3(0, 1.85, SITZ + 0.02);

  // 1 · HOOK: 3 AM, phone glow, the 2019 memory slams in
  { const st = cut(0), mem = Wd('2019', 0) - st;
    add({ id: 'S01', at: st, note: 'night bedroom, face lit by phone, red flash on 2019', draw(lt, d, t, blit) {
      sitPose({ spine: [-6, 0, 0], head: [2, 0, 0], lid: 0.25, look: [0, 3] });
      BED.update(0); BED.lights.phone.material.color.set(mem && lt >= mem ? '#FF6A6A' : '#BFE3FF');
      const zoom = eio(lt / d);
      cam.position.copy(lerpV(V3(1.15, 2.0, 0.75), V3(0.75, 1.9, 0.35), zoom)); cam.lookAt(FACE);
      E.render(BED.scene, cam, { ...BLOOK, focus: cam.position.distanceTo(FACE) }); blit();
      pill('3:00 AM', 540, 330, eob(seg(lt, 0.1, 0.4)), '#FFD43B');
      if (lt >= mem) { const a = Math.exp(-(lt - mem) * 6); ctx.fillStyle = `rgba(214,40,57,${0.28 * a})`; ctx.fillRect(0, 0, W, H); }
    } });
    cue(st, 'whoosh'); cue(st + 0.1, 'pop', { gain: 0.5 }); cue(st + mem, 'thud', { gain: 0.6 }); }

  // 2 · why only at night? (pull back + orbit, question hangs)
  { const st = cut(1);
    add({ id: 'S02', at: st, note: 'pull back, person looks up, WHY AT NIGHT label', draw(lt, d, t, blit) {
      sitPose({ spine: [-10, 0, 0], head: [-14, 0, 0], lid: 0.1, look: [0, -6] });
      BED.update(0);
      const a = lerp(0.95, 1.35, eio(lt / d));
      cam.position.set(SITZ + 0.4 + Math.sin(a) * 1.7, 1.95, SITZ + Math.cos(a) * 1.7); cam.lookAt(0, 1.5, SITZ);
      E.render(BED.scene, cam, { ...BLOOK, focus: 1.7 }); blit();
      label('WHY AT NIGHT?', 770, 470, 540, 900, eob(seg(lt, 0.25, 0.5)));
    } });
    cue(st, 'whoosh'); }

  // 3 · all day it's busy (daylight floods in; PEOPLE PHONE NOISE pills)
  { const st = cut(2), pw = ['people', 'phone', 'noise'].map((w) => Wd(w, 2) - st);
    add({ id: 'S03', at: st, note: 'daylight version, pills pop on each word', draw(lt, d, t, blit) {
      const day = eio(seg(lt, 0, 0.7));
      sitPose({ spine: [-4, 0, 0], head: [-6, 6 * Math.sin(lt * 2), 0], lid: -0.2, look: [4, -2] });
      BED.update(day);
      cam.position.copy(lerpV(V3(-1.1, 2.0, 0.9), V3(-0.75, 1.85, 0.5), eio(lt / d))); cam.lookAt(0, 1.6, SITZ);
      E.render(BED.scene, cam, { ...BLOOK, focus: 1.4 }); blit();
      const items = [['PEOPLE', 250, 640], ['PHONE', 820, 760], ['NOISE', 270, 980]];
      items.forEach(([txt, x, y], i) => pill(txt, x, y, eob(seg(lt, pw[i], pw[i] + 0.3)) * (1 + 0.05 * Math.sin(lt * 6 + i * 2)), i === 1 ? '#FFD43B' : '#FFFFFF'));
    } });
    cue(st, 'whoosh'); pw.forEach((w) => cue(st + w, 'pop', { gain: 0.45 })); }

  // 4 · the default mode network wakes up (x-ray, brain begins to glow)
  { const st = cut(3), net = Wd('network', 3) - st;
    add({ id: 'S04', at: st, note: 'x-ray body, brain lights up in the head', draw(lt, d, t, blit) {
      X.xh.pose({ spine: [-2, 0, 0], head: [-6, 0, 0] });
      const g = seg(lt, 0.2, 1.1);
      X.br.mat.emissiveIntensity = 0.12 + g * 0.8;
      X.br.amg.forEach((a) => (a.material.emissiveIntensity = 0.9 + g * 1.2));
      cam.position.copy(lerpV(V3(0.9, 1.5, 2.6), V3(0.5, 1.72, 1.5), eio(lt / d))); cam.lookAt(0, 1.7, 0);
      E.render(X.scene, cam, { ...XLOOK, focus: cam.position.distanceTo(V3(0, 1.7, 0)) }); blit();
      const [lx, ly] = screen(V3(0.09, 1.78, 0.02), cam);
      label('DEFAULT MODE NETWORK', 720, 480, lx, ly, net && lt >= net ? eob(seg(lt, net, net + 0.3)) : 0);
    } });
    cue(st, 'whoosh'); cue(st + 0.35, 'sparkle', { gain: 0.6 }); }

  // 5 · it replays your own life (brain fills frame, memory panels orbit)
  { const st = cut(4);
    const panels = new THREE.Group(); panels.visible = false;
    for (let i = 0; i < 5; i++) {
      const pm = new THREE.Mesh(new THREE.PlaneGeometry(0.11, 0.07), new THREE.MeshBasicMaterial({ color: '#BFE8FF', transparent: true, opacity: 0.35, side: THREE.DoubleSide }));
      pm.position.set(Math.cos(i * 1.26) * 0.23, 0.02 * Math.sin(i * 3), Math.sin(i * 1.26) * 0.23); pm.lookAt(0, 0, 0); panels.add(pm);
    }
    X.scene.add(panels);
    add({ id: 'S05', at: st, note: 'brain close-up, memory panels orbit like film frames', draw(lt, d, t, blit) {
      panels.rotation.y = lt * 0.9; panels.position.set(0, 1.70, 0); panels.visible = true;
      X.br.mat.emissiveIntensity = 0.42 + 0.08 * Math.sin(lt * 4);
      const a = eio(lt / d);
      cam.position.set(Math.sin(0.6 + a * 0.8) * 0.85, 1.70 + 0.08 * Math.sin(lt * 0.7), Math.cos(0.6 + a * 0.8) * 0.85 + 0.1); cam.lookAt(0, 1.70, 0);
      E.render(X.scene, cam, { ...XLOOK, focus: 0.85, aperture: 0.003, bloom: 0.3, bloomThreshold: 0.65 }); blit();
      label('REPLAYING YOUR LIFE', 300, 430, 620, 560, eob(seg(lt, 0.25, 0.5)));
    } });
    cue(st, 'whoosh'); cue(st + 0.2, 'slide', { dur: cut(5) - st - 0.2, gain: 0.4 }); }

  // 6 · not the wins — it hunts your mistakes (macro: win node dims, red nodes fire)
  { const st = cut(5), wins = Wd('wins', 5) - st, hunt = Wd('hunts', 5) - st;
    add({ id: 'S06', at: st, note: 'inside the brain: win node fades, mistake nodes fire red', draw(lt, d, t, blit) {
      const fireK = hunt && lt >= hunt ? 1 : 0;
      NR.update(t, { winDim: eio(seg(lt, wins, wins + 0.8)), fire: fireK * (0.6 + 0.4 * Math.sin(lt * 9)) });
      const a = eio(lt / d);
      cam.position.set(Math.sin(0.4 + a * 0.5) * 1.9, 0.35 + 0.1 * Math.sin(lt * 0.8), Math.cos(0.4 + a * 0.5) * 1.9 - 1.1); cam.lookAt(0, 0, -1.1);
      E.render(NR.scene, cam, { ...NLOOK, focus: 1.9 }); blit();
      pill('WINS: OFF', 240, 600, eob(seg(lt, wins, wins + 0.3)) * 0.9, '#7CF29A');
      pill('MISTAKES: ON', 810, 700, eob(seg(lt, hunt, hunt + 0.3)), '#FF5A5A');
    } });
    cue(st, 'whoosh'); cue(st + wins, 'plop', { gain: 0.4 }); cue(st + hunt, 'alarm', { dur: cut(6) - st - hunt, gain: 0.5 }); }

  // 7 · negativity bias (memory node pulses like an alarm)
  { const st = cut(6);
    add({ id: 'S07', at: st, note: 'memory node pulsing red, NEGATIVITY BIAS label', draw(lt, d, t, blit) {
      const p = 0.5 + 0.5 * Math.sin(lt * 7);
      NR.update(t, { fire: 0.5 + 0.5 * p });
      const a = eio(lt / d);
      cam.position.set(Math.sin(1.2 + a * 0.6) * 1.35, 0.25, Math.cos(1.2 + a * 0.6) * 1.35 - 0.7); cam.lookAt(0, 0, -0.7);
      E.render(NR.scene, cam, { ...NLOOK, focus: 1.3 }); blit();
      const [lx, ly] = screen(V3(0, 0.35, -0.7), cam);
      label('NEGATIVITY BIAS', 300, 420, lx, ly, eob(seg(lt, 0.25, 0.5)));
    } });
    cue(st, 'whoosh'); cue(st + 0.15, 'alarm', { dur: cut(7) - st - 0.15, gain: 0.4 }); }

  // 8 · same circuits as pain (signal travels memory → pain node, flare + warning)
  { const st = cut(7), circuits = Wd('circuits', 7) - st, pain = Wd('pain', 7) - st;
    add({ id: 'S08', at: st, note: 'red signal travels to the pain node, it flares white', draw(lt, d, t, blit) {
      const sigK = eio(seg(lt, circuits, pain));
      NR.update(t, { fire: lt < pain ? 0.9 : 0.4, signal: sigK });
      const a = eio(lt / d);
      cam.position.set(Math.sin(0.2 + a * 0.4) * 2.0, 0.15, Math.cos(0.2 + a * 0.4) * 2.0 - 1.3); cam.lookAt(0, -0.15, -1.3);
      E.render(NR.scene, cam, { ...NLOOK, focus: 2.0 }); blit();
      const [px, py] = screen(V3(0.5, -0.6, -1.1), cam);
      if (lt >= pain) { warning(540, 1180, eob(seg(lt, pain, pain + 0.3)) * 0.8); label('SAME AS PAIN', 260, 500, px, py, eob(seg(lt, pain, pain + 0.35))); }
    } });
    cue(st + circuits, 'zip', { dur: pain - circuits, gain: 0.55 }); cue(st + pain, 'slam', { gain: 0.65 }); }

  // 9 · it's not a sign (pull back out: brain dims, bedroom returns, person lies back)
  { const st = cut(8);
    add({ id: 'S09', at: st, note: 'bedroom night again, person settles back into the pillow', draw(lt, d, t, blit) {
      X.br.mat.emissiveIntensity = Math.max(0.12, 0.9 * (1 - eio(seg(lt, 0, 0.8))));
      sitPose({ spine: [4 * seg(lt, 0.2, 1.2), 0, 0], head: [8 * seg(lt, 0.2, 1.2), 0, 0], lid: lerp(0.2, 0.55, eio(seg(lt, 0.2, 1.2))), look: [0, 2] });
      BED.update(0); BED.lights.moon.key.intensity += 1.1; BED.lights.pLight.intensity = 1.1;
      cam.position.copy(lerpV(V3(0.2, 2.1, 1.6), V3(0.1, 1.95, 1.05), eio(lt / d))); cam.lookAt(0, 1.7, SITZ);
      E.render(BED.scene, cam, { ...BLOOK, focus: 1.2 }); blit();
      label('IT’S NOT A SIGN', 300, 400, 640, 520, eob(seg(lt, 0.3, 0.55)));
    } });
    cue(st, 'whoosh'); }

  // 10 · just a buggy security check (calm close-up, eyes close, warm fade)
  { const st = cut(9);
    add({ id: 'S10', at: st, note: 'face close-up: small smirk, eyes drift closed', draw(lt, d, t, blit) {
      const k = eio(lt / d);
      sitPose({ spine: [-14, 0, 0], head: [4 * k, 0, 0], lid: lerp(0.15, 1.0, seg(lt, d * 0.45, d * 0.9)), look: [0, lerp(2, -4, k)] });
      BED.update(0); BED.lights.pLight.intensity = lerp(0, 0.7, k); BED.lights.phone.material.color.set('#BFE3FF').multiplyScalar(0.4);
      cam.position.copy(lerpV(V3(0.65, 1.95, 0.65), V3(0.45, 1.88, 0.32), eio(lt / d))); cam.lookAt(FACE);
      E.render(BED.scene, cam, { ...BLOOK, focus: cam.position.distanceTo(FACE), warm: lerp(0.02, 0.1, k) }); blit();
      pill('JUST A BUG', 540, 1350, eob(seg(lt, 0.25, 0.5)) * (1 - seg(lt, d * 0.85, d)), '#FFD43B');
    } });
    cue(st, 'pop', { gain: 0.4 }); cue(st + d10(), 'sparkle', { gain: 0.5 }); }

  function d10() { return T.dur - cut(9) - 0.6; }
  return { shots: S, cues: CUES };
}
