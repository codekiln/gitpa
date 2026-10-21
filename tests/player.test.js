const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
// The site is dependency-free ES modules; this repo's package.json is CommonJS.
const source = readFileSync(join(__dirname, '../site/player.js'), 'utf8');
let chapterTime, clampTime, createPlayer, enhanceEpisode;
before(async () => {
  ({ chapterTime, clampTime, createPlayer, enhanceEpisode } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`));
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

class Element {
  constructor(tagName) { this.tagName = tagName; this.children = []; this.attributes = {}; this.style = { setProperty() {} }; this.classList = { add() {} }; this.textContent = ''; }
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
  getBoundingClientRect() { return { height: 100 }; }
  closest(selector) { return selector === 'a[href]' && this.tagName === 'a' ? this : null; }
}
function pageFixture(count = 1) {
  const document = new EventTarget();
  document.baseURI = 'https://example.com/gitpa/episode/';
  document.body = new Element('body');
  const audio = new Audio();
  Object.assign(audio, { attributes: { src: '/episode.wav' }, getAttribute: Element.prototype.getAttribute, setAttribute: Element.prototype.setAttribute });
  const origin = new Element('li');
  const originClasses = new Set();
  origin.classList = { add: name => originClasses.add(name), contains: name => originClasses.has(name) };
  origin.append(audio);
  document.body.append(origin);
  audio.closest = selector => selector === 'li' ? origin : null;
  document.querySelectorAll = () => Array(count).fill(audio);
  document.querySelector = () => document.body.children.find(item => item.className === 'episode-player') || null;
  document.createElement = name => new Element(name);
  const click = (href, options = {}) => {
    const anchor = new Element('a');
    anchor.setAttribute('href', href);
    anchor.textContent = 'Chapter';
    if (options.heading) {
      const heading = new Element('h3');
      heading.textContent = options.heading;
      const closest = anchor.closest.bind(anchor);
      anchor.closest = selector => selector === 'h1, h2, h3, h4, h5, h6' ? heading : closest(selector);
    }
    if (options.target) anchor.target = options.target;
    if (options.download) anchor.setAttribute('download', '');
    const event = new Event('click', { cancelable: true });
    Object.defineProperty(event, 'target', { value: anchor });
    Object.defineProperties(event, Object.fromEntries(Object.entries({ button: 0, ...options }).filter(([key]) => key !== 'target').map(([key, value]) => [key, { value }])));
    document.dispatchEvent(event);
    return event;
  };
  return { document, audio, click, origin };
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
  assert.equal(player.footer.children[0].children[1].textContent, 'An evolving melody 0:20');
  player.dispose();
  assert.equal(click('/episode.wav#t=20').defaultPrevented, false);
  assert.equal(audio.calls, 2);
});
