const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
let navigationURL, sameDocument, latestRequest, legacyResolver, createNavigator;
before(async () => {
  const source = readFileSync(join(__dirname, '../site/navigation.js'), 'utf8');
  ({ navigationURL, sameDocument, latestRequest, legacyResolver, createNavigator } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`));
});
const response = (html = 'new', extra = {}) => ({ ok: true, text: async () => html, ...extra });
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const tick = () => new Promise(resolve => setTimeout(resolve, 0));

test('only same-origin site HTML is enhanced, with query and fragment preserved', () => {
  const base = 'https://example.com/gitpa/episode/';
  assert.equal(navigationURL('../?q=x#part', base).href, 'https://example.com/gitpa/?q=x#part');
  assert.ok(navigationURL('/gitpa/page.html', base));
  for (const href of ['https://other.com/gitpa/', '/elsewhere/', '/gitpa/file.wav', '/gitpa/file.json', 'mailto:hello@example.com', '/gitpa-not/a/']) assert.equal(navigationURL(href, base), null);
  assert.ok(sameDocument(`${base}#a`, `${base}#b`));
  assert.equal(sameDocument(`${base}?q=1`, base), false);
});

test('latest request ignores stale success even when fetch ignores abort', async () => {
  const a = deferred(); const b = deferred(); const applied = [];
  const requests = latestRequest(url => url === 'a' ? a.promise : b.promise);
  const old = requests.run('a', html => applied.push(html));
  const current = requests.run('b', html => applied.push(html));
  b.resolve(response('latest')); await current;
  a.resolve(response('stale')); assert.equal(await old, false);
  assert.deepEqual(applied, ['latest']);
});

test('stale failure and disposal cannot replace the current page', async () => {
  const pending = deferred(); const requests = latestRequest(() => pending.promise);
  const result = requests.run('/page/', () => assert.fail('must not commit'));
  requests.cancel(); pending.reject(new Error('aborted'));
  assert.equal(await result, false);
});

test('HTTP and non-HTML failures never invoke commit', async () => {
  for (const fetched of [{ ok: false, status: 503 }, response('x', { headers: { get: () => 'audio/wav' } })]) {
    await assert.rejects(latestRequest(async () => fetched).run('/page/', () => assert.fail('must not commit')));
  }
});

test('legacy routes normalize names, share map loading, and retry failed loads', async () => {
  let calls = 0;
  const resolve = legacyResolver(async () => { calls++; return { ok: true, json: async () => ({ 'café/one': 'episode/' }) }; }, 'https://example.com');
  const target = new URL('https://example.com/gitpa/#/page/%20Cafe%CC%81%2FOne%2F%20');
  assert.equal((await resolve(target)).href, 'https://example.com/gitpa/episode/');
  await resolve(target); assert.equal(calls, 1);
  await assert.rejects(resolve(new URL('https://example.com/gitpa/#/page/unknown')));
  let attempts = 0;
  const retry = legacyResolver(async () => { if (++attempts === 1) throw new Error('offline'); return { ok: true, json: async () => ({ one: 'one/' }) }; }, 'https://example.com');
  await assert.rejects(retry(new URL('https://example.com/gitpa/#/page/one')));
  assert.equal((await retry(new URL('https://example.com/gitpa/#/page/one'))).pathname, '/gitpa/one/');
});

class Node extends EventTarget {
  constructor(name, owner) { super(); this.name = name; this.owner = owner; this.children = []; this.attrs = {}; this.textContent = name; }
  append(...nodes) { this.children.push(...nodes); }
  prepend(node) { this.children.unshift(node); }
  remove() { this.removed = true; }
  setAttribute(key, value) { this.attrs[key] = value; }
  hasAttribute(key) { return key in this.attrs; }
  removeAttribute(key) { delete this.attrs[key]; }
  getAttribute(key) { return this.attrs[key] ?? null; }
  querySelectorAll() { return []; }
  replaceWith(node) { this.owner.nodes[this.name] = node; node.owner = this.owner; }
  focus() { this.focused = true; }
  scrollIntoView() { this.scrolled = true; }
}
function fixture(fetcher = async () => response()) {
  const doc = new EventTarget();
  doc.nodes = {};
  for (const name of ['main', 'nav']) doc.nodes[name] = new Node(name, doc);
  doc.head = new Node('head', doc); doc.title = 'Old';
  doc.querySelector = selector => doc.nodes[selector] || null;
  doc.querySelectorAll = selector => doc.nodes[selector] ? [doc.nodes[selector]] : [];
  doc.importNode = node => new Node(node.name, doc);
  doc.createElement = name => new Node(name, doc);
  const fragment = new Node('part', doc);
  doc.getElementById = id => id === 'part' ? fragment : null;
  doc.getElementsByName = () => [];
  const win = new EventTarget();
  win.location = new URL('https://example.com/gitpa/');
  win.scrollX = 0; win.scrollY = 10;
  win.scrollTo = (x, y) => { win.scrollX = x; win.scrollY = y; };
  win.fetch = fetcher;
  win.history = { state: null, scrollRestoration: 'auto', entries: [],
    replaceState(state, _, url) { this.state = state; win.location = new URL(url); },
    pushState(state, _, url) { this.state = state; this.entries.push({ state, url }); win.location = new URL(url); },
  };
  win.DOMParser = class { parseFromString(html) { return { title: html, querySelector: name => ['main', 'nav'].includes(name) ? new Node(name, doc) : null }; } };
  return { doc, win, fragment };
}

test('shell swaps main/nav and title while leaving footer ownership to the player', async () => {
  const { doc, win } = fixture();
  const original = doc.nodes.main;
  let called = 0;
  const navigator = createNavigator({ document: doc, window: win, onPage: ({ url }) => { called++; assert.equal(url.pathname, '/gitpa/one/'); assert.notEqual(doc.nodes.main, original); } });
  assert.equal(win.gitpaNavigate, navigator.navigate);
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  assert.equal(doc.title, 'new'); assert.equal(called, 1);
  assert.equal(win.location.pathname, '/gitpa/one/');
  navigator.dispose(); assert.equal(win.history.scrollRestoration, 'auto');
});

test('shared backlink controls initialize after each main replacement before page hooks and fragment focus', async () => {
  const { doc, win, fragment } = fixture();
  const initialized = [];
  win.logseqGardenerInitBacklinks = root => {
    assert.equal(root, doc.nodes.main);
    initialized.push(root);
  };
  fragment.focus = () => assert.equal(initialized.at(-1), doc.nodes.main);
  const navigator = createNavigator({ document: doc, window: win, onPage: () => {
    assert.equal(initialized.at(-1), doc.nodes.main);
  } });
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  assert.equal(await navigator.navigate('/gitpa/two/#part'), true);
  assert.equal(initialized.length, 2);
  assert.notEqual(initialized[0], initialized[1]);
  await navigator.navigate('#part');
  assert.equal(initialized.length, 2);
  navigator.dispose();
});

test('failed fetch preserves content and creates explicit native recovery', async () => {
  const { doc, win } = fixture(async () => { throw new Error('offline'); });
  const original = doc.nodes.main;
  const navigator = createNavigator({ document: doc, window: win });
  assert.equal(await navigator.navigate('/gitpa/failure/'), false);
  assert.equal(doc.nodes.main, original); assert.equal(win.location.pathname, '/gitpa/');
  const recovery = original.children[0];
  assert.equal(recovery.attrs.role, 'alert');
  assert.equal(recovery.children[1].attrs['data-native-navigation'], '');
  assert.equal(recovery.children[1].href, 'https://example.com/gitpa/failure/');
});

test('same-document fragments focus without fetch and Back restores saved scroll', async () => {
  let fetched = 0;
  const { doc, win, fragment } = fixture(async () => { fetched++; return response(); });
  const navigator = createNavigator({ document: doc, window: win });
  const initialState = win.history.state;
  await navigator.navigate('#part');
  assert.equal(fetched, 0); assert.equal(fragment.focused, true); assert.equal(fragment.scrolled, true);
  win.scrollY = 99;
  win.location = new URL('https://example.com/gitpa/');
  await navigator.navigate(win.location.href, { pop: true, state: initialState });
  assert.equal(win.scrollY, 10);
});

test('initial chapter fragment scrolls and focuses IDs assigned before shell setup', () => {
  const { doc, win, fragment } = fixture();
  win.location = new URL('https://example.com/gitpa/#part');
  createNavigator({ document: doc, window: win });
  assert.equal(fragment.focused, true);
  assert.equal(fragment.scrolled, true);
});

test('Gardener reveals fragment ancestors before soft-navigation focus and scroll', async () => {
  let fetched = 0, revealed = false, calls = 0;
  const { doc, win, fragment } = fixture(async () => { fetched++; return response(); });
  const originalMain = doc.nodes.main;
  win.logseqGardenerRevealFragment = (hash, options) => {
    assert.equal(hash, '#part');
    assert.deepEqual(options, { scroll: false });
    assert.notEqual(doc.nodes.main, originalMain);
    assert.equal(win.location.hash, '#part');
    revealed = true; calls++;
  };
  fragment.focus = () => { assert.equal(revealed, true); };
  fragment.scrollIntoView = () => { assert.equal(revealed, true); };
  const navigator = createNavigator({ document: doc, window: win });
  assert.equal(await navigator.navigate('/gitpa/one/#part'), true);
  assert.equal(fetched, 1);
  revealed = false;
  assert.equal(await navigator.navigate('#part'), true);
  assert.equal(fetched, 1);
  assert.equal(calls, 2);
  navigator.dispose();
});

test('initial legacy hash leaves route handling to the legacy bootstrap', () => {
  const { doc, win, fragment } = fixture();
  win.location = new URL('https://example.com/gitpa/#/page/old');
  createNavigator({ document: doc, window: win });
  assert.equal(fragment.focused, undefined);
  assert.equal(win.scrollY, 10);
});

test('failed Back preserves its destination entry and current content', async () => {
  let offline = false;
  const { doc, win } = fixture(async () => {
    if (offline) throw new Error('offline');
    return response();
  });
  const navigator = createNavigator({ document: doc, window: win });
  await navigator.navigate('/gitpa/b/');
  const destination = { state: win.history.state, url: win.location.href };
  await navigator.navigate('/gitpa/c/');
  const currentMain = doc.nodes.main;
  offline = true;
  // Simulate the browser moving its history cursor from C back to B.
  win.location = new URL(destination.url);
  win.history.state = destination.state;
  await navigator.navigate(win.location.href, { pop: true, state: destination.state });
  assert.equal(win.location.href, destination.url);
  assert.equal(win.history.state, destination.state);
  assert.equal(doc.nodes.main, currentMain);
  assert.equal(currentMain.children[0].children[1].href, destination.url);
  // Forward still reaches C, and a later Back can load the original B entry.
  offline = false;
  await navigator.navigate('/gitpa/c/', { pop: true, state: win.history.entries[1].state });
  await navigator.navigate(destination.url, { pop: true, state: destination.state });
  assert.equal(win.history.entries[0].url, destination.url);
});

test('pending legacy map cannot override a newer ordinary navigation', async () => {
  const map = deferred();
  const { doc, win } = fixture(async url => url.endsWith('.json') ? map.promise : response('current'));
  const navigator = createNavigator({ document: doc, window: win });
  const old = navigator.navigate('/gitpa/#/page/old');
  await navigator.navigate('/gitpa/current/');
  map.resolve({ ok: true, json: async () => ({ old: 'old/' }) });
  assert.equal(await old, false);
  assert.equal(win.location.pathname, '/gitpa/current/'); assert.equal(doc.title, 'current');
});

test('click policy preserves modified, external, download and bypass links', async () => {
  let fetched = 0;
  const { doc, win } = fixture(async () => { fetched++; return response(); });
  createNavigator({ document: doc, window: win });
  const click = (attrs = {}, modifiers = {}) => {
    const anchor = new Node('a', doc);
    anchor.attrs = { href: '/gitpa/page/', ...attrs };
    anchor.target = attrs.target; anchor.rel = attrs.rel;
    const event = new Event('click', { cancelable: true });
    Object.defineProperties(event, Object.fromEntries(Object.entries({ button: 0, target: { closest: () => anchor }, ...modifiers }).map(([key, value]) => [key, { value }])));
    doc.dispatchEvent(event); return event;
  };
  for (const attrs of [{ download: '' }, { 'data-native-navigation': '' }, { target: '_blank' }, { rel: 'external noopener' }, { href: '/gitpa/recording.wav' }, { href: 'https://elsewhere.com/gitpa/' }]) assert.equal(click(attrs).defaultPrevented, false);
  for (const modifiers of [{ button: 1 }, { metaKey: true }, { ctrlKey: true }, { shiftKey: true }, { altKey: true }]) assert.equal(click({}, modifiers).defaultPrevented, false);
  assert.equal(fetched, 0);
  assert.equal(click().defaultPrevented, true);
  await tick(); assert.equal(fetched, 1);
});
