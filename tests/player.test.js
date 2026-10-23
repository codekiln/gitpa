const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
// The site is dependency-free ES modules; this repo's package.json is CommonJS.
const navSource = readFileSync(join(__dirname, '../site/navigation.js'), 'utf8');
const navURL = `data:text/javascript;base64,${Buffer.from(navSource).toString('base64')}`;
const source = readFileSync(join(__dirname, '../site/player.js'), 'utf8').replace("'./navigation.js'", JSON.stringify(navURL));
let chapterTime, clampTime, createPlayer, enhanceEpisode, currentChapter, createEpisodeSession, readEpisode;
before(async () => {
  ({ chapterTime, clampTime, createPlayer, enhanceEpisode, currentChapter, createEpisodeSession, readEpisode } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`));
});

class Audio extends EventTarget {
  readyState = 1;
  duration = 300;
  currentTime = 0;
  paused = true;
  ended = false;
  calls = 0;
  playResult;
  play() { this.calls++; this.paused = false; this.dispatchEvent(new Event('play')); return this.playResult; }
  pause() { this.paused = true; this.emit('pause'); }
  load() { this.readyState = 0; this.currentTime = 0; }
  emit(name) { this.dispatchEvent(new Event(name)); }
}
const tick = () => new Promise(resolve => setTimeout(resolve, 0));

test('only same recording integer fragment links are intercepted', () => {
  const base = 'https://example.com/gitpa/episode/';
  const audio = 'https://cdn.example.com/episode.wav?download=1';
  assert.equal(chapterTime(`${audio}#t=62`, audio, base), 62);
  assert.equal(chapterTime('/full.wav#t=0', '/full.wav', base), 0);
  for (const href of ['https://elsewhere.com/episode.wav#t=2', `${audio}#t=-1`, `${audio}#t=1.5`, `${audio}#t=1,2`, `${audio}#t=1:02`, `${audio}#t=9007199254740992`, `${audio}&x=1#t=2`, audio]) {
    assert.equal(chapterTime(href, audio, base), null, href);
  }
});

test('enhancement does not start playback; chapter click seeks and plays synchronously', () => {
  const audio = new Audio();
  let state;
  const player = createPlayer(audio, value => { state = value; });
  assert.equal(audio.calls, 0);
  assert.equal(state.status, 'Paused');
  player.seek(62, 'A chapter');
  assert.equal(audio.currentTime, 62);
  assert.equal(audio.calls, 1);
  assert.equal(state.chapter, 'A chapter');
  assert.equal(state.status, 'Playing');
  audio.paused = true;
  audio.emit('pause');
  assert.equal(state.status, 'Paused');
});

test('latest pending seek survives metadata loading without restarting paused playback', () => {
  const audio = new Audio();
  audio.readyState = 0;
  const player = createPlayer(audio);
  player.seek(12);
  player.seek(80);
  assert.equal(audio.currentTime, 0);
  assert.equal(audio.calls, 2);
  audio.paused = true;
  audio.readyState = 1;
  audio.emit('loadedmetadata');
  assert.equal(audio.currentTime, 80);
  assert.equal(audio.paused, true);
  assert.equal(audio.calls, 2);
});

test('duration bounds apply both immediately and after metadata arrives', () => {
  assert.equal(clampTime(20, NaN), 20);
  assert.equal(clampTime(20, Infinity), 20);
  const audio = new Audio();
  const player = createPlayer(audio);
  player.seek(999);
  assert.equal(audio.currentTime, 300);
  audio.readyState = 0;
  player.seek(999);
  audio.duration = 50;
  audio.readyState = 1;
  audio.emit('loadedmetadata');
  assert.equal(audio.currentTime, 50);
});

test('rejected stale play promise cannot overwrite a later successful chapter', async () => {
  const audio = new Audio();
  let reject;
  let state;
  const player = createPlayer(audio, value => { state = value; });
  audio.playResult = new Promise((_, fail) => { reject = fail; });
  player.seek(10, 'Old');
  audio.playResult = Promise.resolve();
  player.seek(20, 'New');
  reject(new Error('interrupted'));
  await tick();
  assert.equal(state.chapter, 'New');
  assert.equal(state.status, 'Playing');
});

test('play rejection offers native-control recovery and clears on manual play', async () => {
  const audio = new Audio();
  let state;
  const player = createPlayer(audio, value => { state = value; });
  audio.playResult = Promise.reject(new Error('blocked'));
  player.seek(10);
  await tick();
  assert.match(state.status, /Press play/);
  audio.emit('play');
  assert.equal(state.status, 'Playing');
});

test('media errors clear pending seeks and ignore old play failures', async () => {
  const audio = new Audio();
  let reject;
  let state;
  audio.readyState = 0;
  audio.playResult = new Promise((_, fail) => { reject = fail; });
  const player = createPlayer(audio, value => { state = value; });
  player.seek(20);
  audio.emit('error');
  reject(new Error('load failed'));
  await tick();
  assert.match(state.status, /could not load/);
  audio.readyState = 1;
  audio.emit('loadedmetadata');
  assert.equal(audio.currentTime, 0);
});

test('dispose removes listeners and invalid input never plays', () => {
  const audio = new Audio();
  let updates = 0;
  const player = createPlayer(audio, () => { updates++; });
  for (const time of [-1, 1.5, NaN, Infinity]) assert.equal(player.seek(time), false);
  assert.equal(audio.calls, 0);
  player.dispose();
  audio.emit('playing');
  assert.equal(updates, 1);
  assert.equal(player.seek(10), false);
});

function matches(node, selector) {
  return selector.split(',').some(part => {
    const bits = part.trim().split(/\s+/);
    const token = bits.pop();
    const attr = /\[([^=\]]+)(?:="([^"]+)")?\]/.exec(token);
    const tag = token.replace(/\[.*$/, '');
    if (tag.startsWith('.')) return node.className === tag.slice(1);
    if (node.tagName !== tag) return false;
    if (attr && (!node.hasAttribute(attr[1]) || (attr[2] && node.getAttribute(attr[1]) !== attr[2]))) return false;
    return !bits.length || !!node.parent?.closest(bits.join(' '));
  });
}
class Element extends EventTarget {
  constructor(tagName) {
    super(); this.tagName = tagName; this.children = []; this.attributes = {}; this.style = { setProperty() {} }; this.textContent = '';
    const classes = new Set();
    this.classList = { add: name => classes.add(name), contains: name => classes.has(name), toggle: (name, value) => value ? classes.add(name) : classes.delete(name) };
  }
  append(...children) {
    for (const child of children) {
      if (child.parent) child.parent.children = child.parent.children.filter(item => item !== child);
      child.parent = this;
      this.children.push(child);
    }
  }
  setAttribute(key, value) { this.attributes[key] = value; }
  getAttribute(key) { return this.attributes[key] ?? null; }
  hasAttribute(key) { return key in this.attributes; }
  removeAttribute(key) { delete this.attributes[key]; }
  getBoundingClientRect() { return { height: 100 }; }
  closest(selector) { return matches(this, selector) ? this : this.parent?.closest(selector) || null; }
  querySelectorAll(selector) { return this.children.flatMap(child => [...(matches(child, selector) ? [child] : []), ...child.querySelectorAll(selector)]); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  replaceWith(node) { const i = this.parent.children.indexOf(this); this.parent.children[i] = node; node.parent = this.parent; this.parent = null; }
}
function pageFixture(count = 1) {
  const document = new EventTarget();
  document.baseURI = 'https://example.com/gitpa/episode/';
  document.body = new Element('body');
  document.head = new Element('head');
  const main = new Element('main');
  document.body.append(main);
  const marker = new Element('meta'); marker.setAttribute('name', 'gitpa-episode'); marker.setAttribute('content', '/episode.wav');
  const canonical = new Element('link'); canonical.setAttribute('rel', 'canonical'); canonical.setAttribute('href', '/gitpa/episode/');
  document.head.append(marker, canonical);
  const title = new Element('h1'); title.textContent = 'Episode'; main.append(title);
  const makeAudio = () => {
    const audio = new Audio();
    const element = new Element('audio');
    Object.assign(audio, element);
    for (const method of ['getAttribute', 'setAttribute', 'hasAttribute', 'removeAttribute', 'closest', 'querySelectorAll', 'querySelector', 'replaceWith']) audio[method] = Element.prototype[method];
    audio.setAttribute('src', '/episode.wav');
    return audio;
  };
  const audio = makeAudio();
  const origin = new Element('li');
  if (count) origin.append(audio);
  for (let i = 1; i < count; i++) origin.append(makeAudio());
  main.append(origin);
  const chapterAnchors = new Map();
  for (const [seconds, label] of [[12, '0:12 Chapter'], [20, 'An evolving melody 0:20']]) {
    const heading = new Element('h3'); heading.textContent = label;
    const anchor = new Element('a'); anchor.setAttribute('href', `/episode.wav#t=${seconds}`); anchor.textContent = label;
    heading.append(anchor); main.append(heading); chapterAnchors.set(seconds, anchor);
  }
  document.querySelectorAll = selector => [...document.head.querySelectorAll(selector), ...document.body.querySelectorAll(selector)];
  document.querySelector = selector => document.querySelectorAll(selector)[0] || null;
  document.createElement = name => new Element(name);
  const click = (href, options = {}) => {
    const anchor = chapterAnchors.get(Number(href.split('#t=')[1])) || new Element('a');
    anchor.setAttribute('href', href);
    anchor.textContent = 'Chapter';
    if (options.target) anchor.target = options.target;
    if (options.download) anchor.setAttribute('download', '');
    const event = new Event('click', { cancelable: true });
    Object.defineProperty(event, 'target', { value: anchor });
    Object.defineProperties(event, Object.fromEntries(Object.entries({ button: 0, ...options }).filter(([key]) => key !== 'target').map(([key, value]) => [key, { value }])));
    document.dispatchEvent(event);
    anchor.removeAttribute('download'); anchor.target = '';
    return event;
  };
  return { document, audio, click, origin, main, marker, canonical, makeAudio };
}

test('DOM enhancement moves the original audio once and adds an accessible footer', () => {
  const { document, audio, origin } = pageFixture();
  const player = enhanceEpisode(document);
  assert.equal(player.audio, audio);
  assert.equal(player.footer.children[1], audio);
  assert.equal(document.body.children.includes(audio), false);
  assert.equal(origin.children.includes(audio), false);
  assert.equal(origin.classList.contains('episode-recording-origin'), true);
  assert.equal(player.footer.getAttribute('aria-label'), 'Episode recording');
  assert.equal(audio.controls, true);
  assert.equal(audio.calls, 0);
  assert.equal(enhanceEpisode(document), null);
  assert.equal(enhanceEpisode(pageFixture(2).document), null);
  assert.equal(enhanceEpisode(pageFixture(0).document), null);
});

test('backlink copies do not become episode recordings or chapters', () => {
  const { document, main, audio, makeAudio } = pageFixture();
  const backlinks = new Element('details'); backlinks.className = 'linked-references';
  const copiedHeading = new Element('h3'); copiedHeading.textContent = 'Copied chapter';
  const copiedLink = new Element('a'); copiedLink.setAttribute('href', '/episode.wav#t=14');
  copiedHeading.append(copiedLink);
  const copiedAudio = makeAudio();
  backlinks.append(copiedAudio, copiedHeading); main.append(backlinks);
  const episode = readEpisode(document);
  assert.equal(episode.audio, audio);
  assert.deepEqual(episode.chapters.map(chapter => chapter.seconds), [12, 20]);
  const player = enhanceEpisode(document);
  assert.equal(player.audio, audio);
  assert.equal(copiedAudio.parent, backlinks);
  assert.equal(copiedHeading.id, undefined);
});

test('DOM click handling preserves modified clicks, downloads, other recordings and new tabs', () => {
  const { document, audio, click } = pageFixture();
  const player = enhanceEpisode(document);
  for (const options of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }, { download: true }, { target: '_blank' }]) {
    assert.equal(click('/episode.wav#t=12', options).defaultPrevented, false);
  }
  assert.equal(click('/another.wav#t=12').defaultPrevented, false);
  assert.equal(audio.calls, 0);
  assert.equal(click('/episode.wav#t=12').defaultPrevented, true);
  assert.equal(audio.currentTime, 12);
  assert.equal(audio.calls, 1);
  click('/episode.wav#t=20', { heading: 'An evolving melody 0:20' });
  assert.equal(player.footer.children[0].children[2].textContent, 'An evolving melody 0:20');
  player.dispose();
  assert.equal(click('/episode.wav#t=20').defaultPrevented, false);
  assert.equal(audio.calls, 2);
});

test('playback session retains its origin while current chapter follows native seeking', () => {
  const { audio } = pageFixture();
  const chapters = [{ seconds: 0, href: '/episode/#zero', label: 'Opening' }, { seconds: 20, href: '/episode/#twenty', label: 'Next' }];
  const context = { source: '/episode.wav', url: 'https://example.com/gitpa/episode/', title: 'Episode', chapters };
  let state;
  const session = createEpisodeSession(audio, value => { state = value; });
  session.adopt(context);
  session.activate(context, 0, { href: chapters[0].href, label: 'Opening' });
  audio.currentTime = 24; audio.emit('timeupdate');
  assert.equal(state.current.label, 'Next');
  assert.equal(state.origin.href, '/episode/#zero');
  audio.currentTime = 4; audio.emit('seeked');
  assert.equal(state.current.label, 'Opening');
  assert.equal(state.origin.href, '/episode/#zero');
  assert.equal(currentChapter(chapters, 19).label, 'Opening');
  session.dispose();
});

test('visiting another episode retains the playing audio until explicit selection', () => {
  const fixture = pageFixture();
  const { document, audio, main, marker, canonical, makeAudio } = fixture;
  const player = enhanceEpisode(document);
  fixture.click('/episode.wav#t=12');
  const previousCalls = audio.calls;
  const candidate = makeAudio(); candidate.setAttribute('src', '/another.wav');
  main.append(candidate);
  marker.setAttribute('content', '/another.wav'); canonical.setAttribute('href', '/gitpa/another/');
  player.showPage();
  assert.equal(player.audio, audio);
  assert.equal(audio.getAttribute('src'), '/episode.wav');
  assert.equal(audio.calls, previousCalls);
  assert.equal(main.querySelectorAll('audio').length, 0);
  const button = main.querySelector('button');
  assert.equal(button.textContent, 'Play this episode');
  button.dispatchEvent(new Event('click'));
  assert.equal(player.audio, audio);
  assert.equal(audio.getAttribute('src'), 'https://example.com/another.wav');
  assert.equal(audio.calls, previousCalls + 1);
  player.dispose();
});

test('manual pages with audio do not change episode playback or claim a player', () => {
  const fixture = pageFixture();
  fixture.marker.removeAttribute('content');
  assert.equal(enhanceEpisode(fixture.document), null);
  const initial = pageFixture();
  const player = enhanceEpisode(initial.document);
  initial.click('/episode.wav#t=12');
  initial.marker.removeAttribute('content');
  player.showPage();
  assert.equal(player.audio, initial.audio);
  assert.equal(initial.audio.paused, false);
  player.dispose();
});
