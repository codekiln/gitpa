// Throwaway prototype for issue 164: an illuminated initial whose vine grows
// through the episode. It reads the chapter timestamps from the page, so the
// garden is a map of the session as well as an ornament. Plain script, so the
// HTML works from file:// with no server.
(() => {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const TAU = Math.PI * 2;
  const C = 60;                       // centre of the 120 × 120 tile
  const THETA0 = Math.PI * 0.75;      // root at the lower-left corner
  const SWEEP = TAU * 0.9;            // the vine stops short of its own root
  const INK = {
    vellum: '#efe4c9', vellumEdge: '#d9c7a0', sepia: '#3d3326', madder: '#a8503f',
    leaf: '#6d8a6c', leafDark: '#3f5c4d', vine: '#4a5f45', lapis: '#2c4766',
    gold: '#c9a24a', goldLight: '#f0d68a', goldDeep: '#93702a', ghost: '#8a8f99'
  };
  let uid = 0;

  // ---- seeded hand -------------------------------------------------------
  function hash(value) {
    let h = 2166136261;
    for (const ch of value) h = Math.imul(h ^ ch.codePointAt(0), 16777619);
    return h >>> 0;
  }
  function rng(seed) {
    return () => {
      seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // A slow tremor: the drift of a hand over a long stroke.
  function tremor(rand, strength) {
    const waves = [1, 2.3, 5.1].map((f, i) => ({ f: f * (2 + rand() * 3), p: rand() * TAU, a: strength / (i + 1) }));
    return x => waves.reduce((sum, w) => sum + w.a * Math.sin(x * w.f + w.p), 0);
  }

  // ---- geometry ----------------------------------------------------------
  function rim(theta, r) {
    const c = Math.cos(theta), s = Math.sin(theta);
    return [C + r * Math.sign(c) * Math.abs(c) ** 0.55, C + r * Math.sign(s) * Math.abs(s) ** 0.55];
  }
  function frameAt(u, r) {
    const th = THETA0 + u * SWEEP, d = 0.002;
    const p = rim(th, r), a = rim(th - d, r), b = rim(th + d, r);
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const len = Math.hypot(tx, ty) || 1; tx /= len; ty /= len;
    let nx = ty, ny = -tx;
    if (nx * (p[0] - C) + ny * (p[1] - C) < 0) { nx = -nx; ny = -ny; }
    return { p, t: [tx, ty], n: [nx, ny] };
  }
  function smooth(points) {
    if (points.length < 2) return '';
    const f = n => n.toFixed(2);
    let d = `M${f(points[0][0])} ${f(points[0][1])}`;
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i - 1] || points[i], p1 = points[i], p2 = points[i + 1], p3 = points[i + 2] || p2;
      d += `C${f(p1[0] + (p2[0] - p0[0]) / 6)} ${f(p1[1] + (p2[1] - p0[1]) / 6)} ${f(p2[0] - (p3[0] - p1[0]) / 6)} ${f(p2[1] - (p3[1] - p1[1]) / 6)} ${f(p2[0])} ${f(p2[1])}`;
    }
    return d;
  }
  function wobbleLine(rand, pts, jitter) {
    const out = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const [x1, y1] = pts[i], [x2, y2] = pts[i + 1];
      const steps = Math.max(2, Math.round(Math.hypot(x2 - x1, y2 - y1) / 9));
      for (let s = 0; s < steps; s++) {
        const k = s / steps;
        out.push([x1 + (x2 - x1) * k + (rand() - 0.5) * jitter, y1 + (y2 - y1) * k + (rand() - 0.5) * jitter]);
      }
    }
    out.push(pts[pts.length - 1]);
    return smooth(out);
  }

  // ---- svg helpers -------------------------------------------------------
  function el(name, attrs = {}, parent) {
    const node = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) if (v != null) node.setAttribute(k, v);
    if (parent) parent.append(node);
    return node;
  }

  // ---- reading the episode from the page ---------------------------------
  function parseTime(text) {
    const parts = text.trim().split(':').map(Number);
    return parts.reduce((acc, n) => acc * 60 + n, 0);
  }
  function readEpisode(main) {
    const chapters = [...main.querySelectorAll('h4')].map((h, i) => {
      const stamp = h.querySelector('a');
      return { i, node: h, t: parseTime(stamp.textContent), title: h.textContent.replace(stamp.textContent, '').trim() };
    });
    const durationText = main.querySelector('[data-duration]')?.textContent.match(/\d+:\d\d/);
    const duration = durationText ? parseTime(durationText[0]) : (chapters.at(-1)?.t || 0) * 1.1;
    chapters.forEach((ch, i) => { ch.end = chapters[i + 1]?.t ?? duration; });
    const spirit = (words) => chapters.find(ch => words.test(ch.title));
    return {
      duration, chapters,
      hush: spirit(/\b(hush|silence|quiet)\b/i),
      beacon: spirit(/\b(high g|beacon|star)\b/i),
      light: spirit(/\b(major|light)\b/i),
      voice: spirit(/\b(afterword|spoken)\b/i)
    };
  }

  // ---- the drawing -------------------------------------------------------
  function draw(letter, episode, seed, opts = {}) {
    const mini = !!opts.mini;
    const rand = rng(seed);
    const id = `pc${++uid}`;
    const R = 44;
    const svg = el('svg', { viewBox: '0 0 120 120', 'aria-hidden': 'true', focusable: 'false', class: 'pc-art' });
    const defs = el('defs', {}, svg);

    // Vellum grain, ink bleed, and gilding.
    const grain = el('filter', { id: `${id}-grain`, x: 0, y: 0, width: 1, height: 1 }, defs);
    el('feTurbulence', { type: 'fractalNoise', baseFrequency: 0.9, numOctaves: 3, seed: seed % 997 }, grain);
    el('feColorMatrix', { values: '0 0 0 0 0.36  0 0 0 0 0.27  0 0 0 0 0.15  0 0 0 -1.1 0.62' }, grain);
    el('feComposite', { in2: 'SourceGraphic', operator: 'in' }, grain);
    const bleed = el('filter', { id: `${id}-bleed`, x: -0.05, y: -0.05, width: 1.1, height: 1.1 }, defs);
    el('feTurbulence', { type: 'turbulence', baseFrequency: 1.4, numOctaves: 2, seed: (seed >>> 3) % 991, result: 'n' }, bleed);
    el('feDisplacementMap', { in: 'SourceGraphic', in2: 'n', scale: mini ? 0.7 : 1.1 }, bleed);
    const gold = el('linearGradient', { id: `${id}-gold`, x1: 0, y1: 0, x2: 1, y2: 1 }, defs);
    [[0, INK.goldLight], [0.45, INK.gold], [0.7, INK.goldDeep], [1, INK.goldLight]].forEach(([o, c]) => el('stop', { offset: o, 'stop-color': c }, gold));
    const lapis = el('radialGradient', { id: `${id}-lapis`, cx: 0.4, cy: 0.35, r: 0.8 }, defs);
    [[0, '#4d6f94'], [1, INK.lapis]].forEach(([o, c]) => el('stop', { offset: o, 'stop-color': c }, lapis));

    // The leaf of vellum, its ruled border drawn by hand.
    const edge = [[4, 4], [116, 4], [116, 116], [4, 116], [4, 4]];
    const tile = wobbleLine(rand, edge, 1.1) + 'Z';
    el('path', { d: tile, fill: INK.vellum }, svg);
    el('path', { d: tile, fill: '#000', filter: `url(#${id}-grain)` }, svg);
    const bleedGroup = el('g', { filter: `url(#${id}-bleed)` }, svg);
    el('path', { d: tile, fill: 'none', stroke: INK.sepia, 'stroke-width': 1.6, class: 'pc-ink', 'data-u': 0 }, bleedGroup);
    el('path', { d: wobbleLine(rand, [[8, 8], [112, 8], [112, 112], [8, 112], [8, 8]], 0.9), fill: 'none', stroke: INK.madder, 'stroke-width': 0.6, class: 'pc-ink', 'data-u': 0 }, bleedGroup);

    // The tuning dial behind the letter: a shortwave set in the dark.
    if (!mini) {
      const dial = el('g', { fill: 'none', stroke: `url(#${id}-gold)` }, bleedGroup);
      el('circle', { cx: C, cy: C, r: 27, 'stroke-width': 0.7, class: 'pc-fade', 'data-u': 0.02 }, dial);
      el('circle', { cx: C, cy: C, r: 30.5, 'stroke-width': 0.45, 'stroke-dasharray': '0.5 1.7', class: 'pc-fade', 'data-u': 0.02 }, dial);
      el('circle', { cx: C, cy: C, r: 26, fill: '#d7e0d8', 'fill-opacity': 0.55, stroke: 'none', class: 'pc-fade', 'data-u': 0.01 }, dial);
      for (const ch of episode.chapters) {
        const th = THETA0 + (ch.t / episode.duration) * SWEEP;
        const [x1, y1] = [C + 27.5 * Math.cos(th), C + 27.5 * Math.sin(th)];
        const [x2, y2] = [C + 30 * Math.cos(th), C + 30 * Math.sin(th)];
        el('line', { x1, y1, x2, y2, stroke: INK.goldDeep, 'stroke-width': 0.6, class: 'pc-fade', 'data-u': ch.t / episode.duration, 'data-ch': ch.i }, dial);
      }
    }

    // Two strands braided around the frame: the A and B sides of the crossfader.
    const strandOf = (phase, wobble) => u => {
      const f = frameAt(u, R);
      const off = (mini ? 1.6 : 2.6) * Math.sin(u * TAU * (mini ? 5 : 8) + phase) + wobble(u * 6);
      return [f.p[0] + f.n[0] * off, f.p[1] + f.n[1] * off];
    };
    const strands = [strandOf(0, tremor(rand, 0.45)), strandOf(Math.PI, tremor(rand, 0.45))];
    if (mini) strands.pop();
    const hush = episode.hush ? [episode.hush.t / episode.duration, episode.hush.end / episode.duration] : null;
    const pieces = hush ? [[0, hush[0], false], [hush[0], hush[1], true], [hush[1], 1, false]] : [[0, 1, false]];
    const vines = el('g', { fill: 'none', 'stroke-linecap': 'round' }, bleedGroup);
    strands.forEach((at, s) => {
      for (const [a, b, ghostly] of pieces) {
        const pts = [];
        const n = Math.max(4, Math.round((b - a) * 260));
        for (let k = 0; k <= n; k++) pts.push(at(a + (b - a) * (k / n)));
        el('path', ghostly
          ? { d: smooth(pts), stroke: INK.ghost, 'stroke-width': 0.7, 'stroke-dasharray': '0.3 2.1', class: 'pc-fade', 'data-u': a }
          : { d: smooth(pts), stroke: s ? INK.leafDark : INK.vine, 'stroke-width': s ? 1.0 : 1.35, class: 'pc-ink', 'data-u': a, 'data-u2': b }, vines);
      }
    });

    // The root and seed at 00:00.
    const root = frameAt(0, R);
    const seedAt = [root.p[0] - root.t[0] * 2.5, root.p[1] - root.t[1] * 2.5];
    const roots = el('g', { stroke: INK.sepia, 'stroke-width': 0.5, fill: 'none' }, bleedGroup);
    for (let k = 0; k < 3; k++) {
      const ang = Math.atan2(-root.t[1], -root.t[0]) + (k - 1) * 0.6;
      const pts = [seedAt];
      for (let j = 1; j <= 4; j++) pts.push([seedAt[0] + Math.cos(ang + j * 0.25 * (k - 1 || 0.4)) * j * 1.6, seedAt[1] + Math.sin(ang + j * 0.3) * j * 1.6]);
      el('path', { d: smooth(pts), class: 'pc-ink', 'data-u': 0 }, roots);
    }
    el('ellipse', { cx: seedAt[0], cy: seedAt[1], rx: 2.2, ry: 1.5, fill: INK.madder, stroke: INK.sepia, 'stroke-width': 0.5, transform: `rotate(${Math.atan2(root.t[1], root.t[0]) * 180 / Math.PI} ${seedAt[0]} ${seedAt[1]})` }, el('g', { class: 'pc-pop pc-pop--c', 'data-u': 0 }, bleedGroup));

    // A leaf for every chapter, at its own moment on the vine.
    const leaves = el('g', {}, bleedGroup);
    for (const ch of episode.chapters) {
      if (episode.hush && ch === episode.hush) continue;
      const u = ch.t / episode.duration;
      const at = strands[ch.i % strands.length](u);
      const f = frameAt(u, R);
      const out = ch.i % 2 === 0 ? 1 : -1;
      const tilt = 0.55 * (rand() * 0.6 + 0.7);
      const ang = Math.atan2(f.n[1] * out + f.t[1] * tilt, f.n[0] * out + f.t[0] * tilt) * 180 / Math.PI;
      const weight = Math.min(1, (ch.end - ch.t) / 240);
      const L = (mini ? 4.5 : 6) + weight * (mini ? 3 : 6.5) * (out > 0 ? 1 : 0.75);
      const W = L * (0.34 + rand() * 0.1);
      const j = () => (rand() - 0.5) * L * 0.12;
      const g = el('g', { transform: `translate(${at[0].toFixed(2)} ${at[1].toFixed(2)}) rotate(${ang.toFixed(1)})`, class: 'pc-leaf' }, leaves);
      const inner = el('g', { class: 'pc-pop', 'data-u': u, 'data-ch': ch.i }, g);
      el('path', { d: `M0 0L1.4 0`, stroke: INK.vine, 'stroke-width': 0.6 }, inner);
      el('path', {
        d: `M1.2 0C${(L * 0.3 + j()).toFixed(2)} ${(-W + j()).toFixed(2)} ${(L * 0.78 + j()).toFixed(2)} ${(-W * 0.75).toFixed(2)} ${L.toFixed(2)} ${j().toFixed(2)}C${(L * 0.75 + j()).toFixed(2)} ${(W * 0.8).toFixed(2)} ${(L * 0.3 + j()).toFixed(2)} ${(W + j()).toFixed(2)} 1.2 0Z`,
        fill: ch.i % 3 === 2 ? INK.leafDark : INK.leaf, stroke: INK.sepia, 'stroke-width': 0.45
      }, inner);
      el('path', { d: `M1.4 0Q${(L * 0.5).toFixed(2)} ${(W * 0.15).toFixed(2)} ${(L * 0.9).toFixed(2)} 0`, fill: 'none', stroke: INK.vellum, 'stroke-width': 0.35, 'stroke-opacity': 0.8 }, inner);
      if (!mini && ch.i % 4 === 1) {
        for (let b = 0; b < 3; b++) el('circle', { cx: (-1.2 - b * 0.9).toFixed(2), cy: ((b - 1) * 1.6 * -out).toFixed(2), r: 0.8, fill: INK.madder, stroke: INK.sepia, 'stroke-width': 0.25 }, inner);
      }
    }

    // Spirits called up by the chapter titles.
    const marks = el('g', {}, bleedGroup);
    const inwardAt = (u, depth) => { const f = frameAt(u, R - depth); return { p: f.p, n: f.n, t: f.t }; };
    if (episode.hush) {
      const u = (episode.hush.t + episode.hush.end) / 2 / episode.duration;
      const { p } = inwardAt(u, mini ? 6 : 9);
      const w = el('g', { transform: `translate(${p[0].toFixed(2)} ${p[1].toFixed(2)}) scale(${mini ? 0.7 : 1})`, class: 'pc-fade pc-wisp', 'data-u': u, 'data-ch': episode.hush.i }, marks);
      el('path', { d: 'M-2.6 3.6C-3 -0.5 -2 -3.4 0 -3.4S3 -0.5 2.6 3.6L1.6 2.6 0.6 3.8 -0.4 2.6 -1.5 3.8Z', fill: '#f6efdf', 'fill-opacity': 0.9, stroke: INK.ghost, 'stroke-width': 0.4 }, w);
      el('circle', { cx: -0.9, cy: -0.9, r: 0.42, fill: INK.lapis }, w);
      el('circle', { cx: 0.9, cy: -0.9, r: 0.42, fill: INK.lapis }, w);
    }
    if (episode.beacon && !mini) {
      const u = episode.beacon.t / episode.duration;
      const { p } = inwardAt(u, 9.5);
      const s = el('g', { class: 'pc-pop pc-pop--c', 'data-u': u, 'data-ch': episode.beacon.i }, el('g', { transform: `translate(${p[0].toFixed(2)} ${p[1].toFixed(2)})` }, marks));
      let d = '';
      for (let k = 0; k < 16; k++) {
        const a = (k / 16) * TAU, r = k % 2 ? 1.1 : 3.4;
        d += `${k ? 'L' : 'M'}${(Math.cos(a) * r).toFixed(2)} ${(Math.sin(a) * r).toFixed(2)}`;
      }
      el('path', { d: d + 'Z', fill: `url(#${id}-gold)`, stroke: INK.goldDeep, 'stroke-width': 0.3 }, s);
      for (let k = 0; k < 8; k++) {
        const a = (k / 8) * TAU + 0.2;
        el('line', { x1: Math.cos(a) * 4.2, y1: Math.sin(a) * 4.2, x2: Math.cos(a) * 5.6, y2: Math.sin(a) * 5.6, stroke: INK.gold, 'stroke-width': 0.3 }, s);
      }
    }
    if (episode.light) {
      const u = episode.light.t / episode.duration;
      const { p } = inwardAt(u, mini ? 4 : 6.5);
      const fl = el('g', { transform: `scale(${mini ? 0.7 : 1}) rotate(${(rand() * 72).toFixed(0)})` }, el('g', { class: 'pc-pop pc-pop--c', 'data-u': u, 'data-ch': episode.light.i }, el('g', { transform: `translate(${p[0].toFixed(2)} ${p[1].toFixed(2)})` }, marks)));
      for (let k = 0; k < 5; k++) el('ellipse', { cx: 0, cy: -2.1, rx: 1.35, ry: 2.2, transform: `rotate(${k * 72})`, fill: `url(#${id}-gold)`, stroke: INK.goldDeep, 'stroke-width': 0.3 }, fl);
      el('circle', { r: 1.1, fill: INK.madder, stroke: INK.sepia, 'stroke-width': 0.3 }, fl);
    }
    if (episode.voice && !mini) {
      const u = episode.voice.t / episode.duration;
      const f = frameAt(u, R);
      const at = strands[0](u);
      const ang = Math.atan2(-f.n[1], -f.n[0]);
      const pod = el('g', { transform: `translate(${at[0].toFixed(2)} ${at[1].toFixed(2)}) rotate(${(ang * 180 / Math.PI).toFixed(1)})` }, el('g', { class: 'pc-pop', 'data-u': u, 'data-ch': episode.voice.i }, marks));
      el('path', { d: 'M0 0C1.5 -2.4 4.5 -2.2 5.2 0C4.5 2.2 1.5 2.4 0 0Z', fill: INK.madder, stroke: INK.sepia, 'stroke-width': 0.4 }, pod);
      el('path', { d: 'M1.2 0L4.4 0', stroke: INK.goldLight, 'stroke-width': 0.4 }, pod);
      [3, 5, 7].forEach((r, k) => {
        const a = 0.6;
        el('path', {
          d: `M${(5.2 + r * Math.cos(-a)).toFixed(2)} ${(r * Math.sin(-a)).toFixed(2)}A${r} ${r} 0 0 1 ${(5.2 + r * Math.cos(a)).toFixed(2)} ${(r * Math.sin(a)).toFixed(2)}`,
          fill: 'none', stroke: INK.gold, 'stroke-width': 0.45 - k * 0.08, 'stroke-dasharray': k ? '0.6 0.8' : null, class: 'pc-wave'
        }, pod);
      });
    }

    // The playhead: a spark that travels the vine while the recording plays.
    const spark = el('circle', { r: 1.6, fill: INK.goldLight, stroke: INK.goldDeep, 'stroke-width': 0.3, class: 'pc-spark', opacity: 0 }, svg);
    spark.place = (time) => {
      const u = Math.min(1, Math.max(0, time / episode.duration));
      const [x, y] = strands[0](u);
      spark.setAttribute('cx', x.toFixed(2)); spark.setAttribute('cy', y.toFixed(2));
      spark.setAttribute('opacity', 1);
    };

    // The letter, lapis edged in gold, with one tendril crossing in front of it.
    const glyph = el('g', { class: 'pc-letter' }, svg);
    const lower = letter !== letter.toUpperCase();
    const size = (mini ? 58 : 64) * (lower ? 1.2 : 1);
    const common = { x: C, y: C + size * (lower ? 0.22 : 0.34), 'text-anchor': 'middle', 'font-size': size, 'font-family': "Georgia, 'Times New Roman', serif", 'font-weight': 700 };
    el('text', { ...common, x: C + 1.3, y: common.y + 1.3, fill: INK.goldDeep }, glyph).textContent = letter;
    el('text', { ...common, fill: `url(#${id}-lapis)`, stroke: `url(#${id}-gold)`, 'stroke-width': 1.1, 'paint-order': 'stroke' }, glyph).textContent = letter;
    if (!mini) {
      const start = strands[1](0.04);
      // It reaches in from the vine, then curls once over the letter's foot.
      const pts = [start];
      const cx = C - 17, cy = C + 21, turns = 1.75;
      const a0 = Math.atan2(start[1] - cy, start[0] - cx);
      for (let k = 0; k <= 28; k++) {
        const a = a0 - (k / 28) * turns * TAU;
        const r = 7.5 * (1 - k / 34);
        pts.push([cx + Math.cos(a) * r + (rand() - 0.5) * 0.3, cy + Math.sin(a) * r + (rand() - 0.5) * 0.3]);
      }
      const front = el('g', { filter: `url(#${id}-bleed)` }, svg);
      el('path', { d: smooth(pts), fill: 'none', stroke: INK.vine, 'stroke-width': 0.9, 'stroke-linecap': 'round', class: 'pc-ink', 'data-u': 0.05, 'data-u2': 0.25 }, front);
    }
    return { svg, spark };
  }

  // ---- placing initials on the page (mirrors production's targeting) -----
  function placeInitial(container, build, chapter) {
    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (node.parentElement.closest('button, svg, .pc-initial')) return NodeFilter.FILTER_REJECT;
        const link = node.parentElement.closest('a');
        if (link && /^\d/.test(link.textContent.trim())) return NodeFilter.FILTER_REJECT;
        return /\p{L}/u.test(node.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    const node = walker.nextNode();
    if (!node) return null;
    const match = /\p{L}/u.exec(node.data);
    const wrap = document.createElement('span');
    wrap.className = 'pc-initial' + (chapter ? ' pc-initial--chapter' : '');
    const { svg, spark } = build(match[0]);
    wrap.append(svg);
    const sr = document.createElement('span');
    sr.className = 'pc-initial__letter';
    sr.textContent = match[0];
    wrap.append(sr);
    const rest = node.splitText(match.index);
    rest.deleteData(0, match[0].length);
    rest.parentNode.insertBefore(wrap, rest);
    return { wrap, svg, spark };
  }

  // The vine grows in episode order; leaves open as it reaches them.
  function grow(svg, ms = 5200) {
    // Cancel the previous growth, but leave the wisp's drift and the pod's call running.
    for (const a of svg.getAnimations({ subtree: true })) if (!(a instanceof CSSAnimation)) a.cancel();
    const at = node => Number(node.dataset.u || 0) * ms * 0.9;
    svg.querySelectorAll('.pc-ink').forEach(path => {
      const len = path.getTotalLength();
      const span = (Number(path.dataset.u2 || path.dataset.u || 0) - Number(path.dataset.u || 0)) * ms * 0.9;
      path.animate([{ strokeDasharray: `${len} ${len}`, strokeDashoffset: len }, { strokeDasharray: `${len} ${len}`, strokeDashoffset: 0 }],
        { duration: Math.max(500, span), delay: at(path), easing: 'linear', fill: 'backwards' });
    });
    svg.querySelectorAll('.pc-pop').forEach(node => node.animate(
      [{ transform: 'scale(0)', opacity: 0 }, { transform: 'scale(1.15)', opacity: 1, offset: 0.7 }, { transform: 'scale(1)', opacity: 1 }],
      { duration: 650, delay: at(node) + 120, easing: 'ease-out', fill: 'backwards' }));
    svg.querySelectorAll('.pc-fade').forEach(node => node.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 1400, delay: at(node), fill: 'backwards' }));
    svg.querySelectorAll('.pc-letter').forEach(node => node.animate(
      [{ opacity: 0, filter: 'blur(3px)' }, { opacity: 1, filter: 'blur(0)' }], { duration: 1600, delay: ms * 0.25, easing: 'ease-out', fill: 'backwards' }));
  }

  const style = document.createElement('style');
  style.textContent = `
    .pc-initial { position: relative; float: left; width: 6.6rem; height: 6.6rem; margin: .2rem .85rem .2rem 0;
      filter: drop-shadow(2px 3px 2px #2e344040); line-height: 1; }
    .pc-initial--chapter { float: none; display: inline-block; width: 3.6rem; height: 3.6rem; vertical-align: middle; margin: 0 .2rem 0 .35rem; }
    .pc-initial svg { width: 100%; height: 100%; display: block; overflow: visible; }
    .pc-initial__letter { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
    .pc-pop { transform-box: fill-box; transform-origin: 0 50%; transition: filter .25s; } .pc-pop--c { transform-origin: 50% 50%; }
    [data-ch].is-lit { filter: drop-shadow(0 0 1.6px #f0d68a) drop-shadow(0 0 .6px #c9a24a); }
    .pc-wisp { animation: pc-drift 6s ease-in-out infinite; }
    @keyframes pc-drift { 50% { translate: 0 -1.2px; opacity: .75; } }
    .pc-wave { animation: pc-call 2.4s ease-in-out infinite; }
    .pc-wave:nth-of-type(3) { animation-delay: .3s; } .pc-wave:nth-of-type(4) { animation-delay: .6s; }
    @keyframes pc-call { 0%, 100% { opacity: .25; } 50% { opacity: 1; } }
    .pc-spark { filter: drop-shadow(0 0 1.5px #f0d68a); transition: cx .3s linear, cy .3s linear; }
    @media (max-width: 480px) { .pc-initial { width: 5rem; height: 5rem; } .pc-initial--chapter { width: 3rem; height: 3rem; } }
    @media (prefers-reduced-motion: reduce) { .pc-wisp, .pc-wave { animation: none; } }
  `;
  document.head.append(style);

  // ---- wiring ------------------------------------------------------------
  const main = document.querySelector('main');
  const pageId = document.querySelector('meta[name="gitpa-episode"]').content;
  const episode = readEpisode(main);
  const audio = main.querySelector('audio');
  let salt = 0;
  let placed = [];

  function render() {
    for (const p of placed) p.wrap.replaceWith(p.wrap.querySelector('.pc-initial__letter').textContent);
    placed = [];
    const headings = [...main.querySelectorAll('h2')];
    const find = name => headings.find(h => h.textContent.trim().toLowerCase() === name)?.parentElement;
    const annotation = find('ceremonial annotations')?.querySelector(':scope > ul > li');
    const chapter = find('chapters')?.querySelector(':scope > ul > li > h3');
    const seed = hash(pageId) + salt * 7919;
    if (annotation) placed.push(placeInitial(annotation, ch => draw(ch, episode, seed), false));
    if (chapter) placed.push(placeInitial(chapter, ch => draw(ch, episode, seed + 1, { mini: true }), true));
    placed = placed.filter(Boolean);
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce) placed.forEach((p, i) => grow(p.svg, i ? 3600 : 5200));
    if (audio.currentTime) placed.forEach(p => p.spark.place(audio.currentTime));
  }

  function light(i, on) {
    for (const p of placed) p.svg.querySelectorAll(`[data-ch="${i}"]`).forEach(n => n.classList.toggle('is-lit', on));
    episode.chapters[i]?.node.classList.toggle('is-lit', on);
  }
  for (const ch of episode.chapters) {
    ch.node.addEventListener('mouseenter', () => light(ch.i, true));
    ch.node.addEventListener('mouseleave', () => light(ch.i, false));
  }
  main.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#t="]');
    if (!link) return;
    event.preventDefault();
    audio.currentTime = Number(link.getAttribute('href').slice(3));
    audio.play().catch(() => {});
  });
  audio.addEventListener('timeupdate', () => {
    placed.forEach(p => p.spark.place(audio.currentTime));
    const now = episode.chapters.findLast(ch => ch.t <= audio.currentTime);
    episode.chapters.forEach(ch => light(ch.i, ch === now));
  });

  document.getElementById('regrow').addEventListener('click', () => placed.forEach((p, i) => grow(p.svg, i ? 3600 : 5200)));
  document.getElementById('hand').addEventListener('click', () => { salt += 1; render(); });
  document.getElementById('theme').addEventListener('click', () => {
    const root = document.documentElement;
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
  });
  if (matchMedia('(prefers-color-scheme: dark)').matches) document.documentElement.dataset.theme = 'dark';
  render();
})();
