const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
let navigationURL, searchPageRoute, sameDocument, latestRequest, legacyResolver, createNavigator, pageScripts;
before(async () => {
  const source = readFileSync(join(__dirname, '../site/navigation.js'), 'utf8');
  ({ navigationURL, searchPageRoute, sameDocument, latestRequest, legacyResolver, createNavigator, pageScripts } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`));
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
  doc.importNode = node => { const copy = new Node(node.name, doc); copy.attrs = { ...node.attrs }; copy.textContent = node.textContent; return copy; };
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
  win.DOMParser = class { parseFromString(html) { return { title: html, head: { querySelectorAll: () => [] }, querySelector: name => ['main', 'nav'].includes(name) ? new Node(name, doc) : null, querySelectorAll: () => [] }; } };
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

test('shared appearance controls initialize on replaced navigation without changing document ownership', async () => {
  const { doc, win } = fixture();
  const original = doc.nodes.nav;
  let calls = 0;
  win.logseqGardenerInitTheme = root => {
    assert.equal(root, doc.nodes.nav);
    assert.notEqual(root, original);
    calls++;
  };
  const navigator = createNavigator({ document: doc, window: win, onPage: () => assert.equal(calls, 1) });
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  assert.equal(calls, 1);
  await navigator.navigate('#part');
  assert.equal(calls, 1);
  navigator.dispose();
});

test('shared outline and property controls initialize before replacement hooks and source focus', async () => {
  const { doc, win, fragment } = fixture();
  const outlines = [], properties = [], allPages = [];
  win.logseqGardenerInitOutline = root => outlines.push(root);
  win.logseqGardenerInitProperties = root => properties.push(root);
  win.logseqGardenerAllPages = { init: root => allPages.push(root) };
  const assertCurrent = () => {
    assert.equal(outlines.at(-1), doc.nodes.main);
    assert.equal(properties.at(-1), doc.nodes.main);
    assert.equal(allPages.at(-1), doc.nodes.main);
  };
  fragment.focus = assertCurrent;
  const navigator = createNavigator({ document: doc, window: win, onPage: assertCurrent });
  assert.deepEqual(outlines, [doc]);
  assert.deepEqual(properties, [doc]);
  await navigator.navigate('/gitpa/one/');
  await navigator.navigate('/gitpa/two/#part');
  assert.equal(outlines.length, 3);
  assert.equal(properties.length, 3);
  assert.equal(allPages.length, 2);
  assert.notEqual(outlines[1], outlines[2]);
  await navigator.navigate('#part');
  assert.equal(outlines.length, 3);
  assert.equal(properties.length, 3);
  assert.equal(allPages.length, 2);
  navigator.dispose();
});

const SHARED_SCRIPTS = ['/gitpa/lsg-shell.js', '/gitpa/bootstrap.js'];
const GRAPH_SCRIPTS = ['/gitpa/lsg-shell.js', '/gitpa/lsg-graph.js', '/gitpa/bootstrap.js'];
const ALL_PAGES_SCRIPTS = ['/gitpa/lsg-shell.js', '/gitpa/lsg-all-pages.js', '/gitpa/bootstrap.js'];
const OTHER_SCRIPTS = ['/gitpa/lsg-shell.js', '/gitpa/other.js', '/gitpa/bootstrap.js'];
const scriptNodes = (doc, sources) => sources.map(src => { const node = new Node('script', doc); node.setAttribute('src', src); return node; });
const styleNodes = (doc, styles = []) => styles.map(({ href, text }) => {
  const node = new Node(href ? 'link' : 'style', doc);
  node.tagName = href ? 'LINK' : 'STYLE';
  if (href) node.setAttribute('href', href);
  else node.textContent = text;
  return node;
});
const appended = (doc, name) => doc.head.children.filter(node => node.name === name);
const HEADER_CONTROLS = ['[data-lsg-left-toggle]', '[data-lsg-search]', '[data-lsg-more]', '[data-lsg-right-toggle]'];
function headerNode(doc, { home }) {
  const header = new Node('.lsg-header', doc);
  header.controls = {};
  for (const selector of HEADER_CONTROLS) {
    const control = new Node(selector, doc);
    // lsg renders these hidden; the shell and search reveal them.
    control.hidden = true;
    if (selector !== '[data-lsg-search]') control.setAttribute('aria-expanded', 'false');
    header.controls[selector] = control;
  }
  if (home) header.controls['a[aria-label="Home"]'] = new Node('home', doc);
  header.querySelector = selector => header.controls[selector] ?? null;
  return header;
}
// Pages keyed by path: the scripts their HTML lists, their head styles and whether their header has a Home button.
function site(pages, current = SHARED_SCRIPTS) {
  const loads = [];
  const { doc, win } = fixture(async url => response(url));
  doc.querySelectorAll = selector => {
    if (selector === 'script[src]') return scriptNodes(doc, current);
    if (selector === 'link[rel="stylesheet"]') return appended(doc, 'link').map(link => ({ href: link.getAttribute('href') }));
    if (selector === 'style') return appended(doc, 'style');
    return doc.nodes[selector] ? [doc.nodes[selector]] : [];
  };
  const importNode = doc.importNode;
  doc.importNode = node => node.name === '.lsg-header' ? node : importNode(node);
  win.DOMParser = class { parseFromString(html) {
    const page = pages[new URL(html).pathname];
    const header = headerNode(doc, page);
    return {
      title: html,
      head: { querySelectorAll: () => styleNodes(doc, page.styles) },
      querySelector: query => query === '.lsg-header' ? header : (['main', 'nav'].includes(query) ? new Node(query, doc) : null),
      querySelectorAll: query => query === 'script[src]' ? scriptNodes(doc, page.scripts) : [],
    };
  } };
  // The fixture replaces location on each history change; record full page loads on whichever is current.
  const watch = () => {
    win.location.assign = url => loads.push(['assign', url]);
    win.location.reload = () => loads.push(['reload', win.location.href]);
  };
  return { doc, win, loads, watch };
}

test('page scripts resolve against the page address', () => {
  const root = { querySelectorAll: () => scriptNodes(null, ['/gitpa/lsg-shell.js', 'lsg-graph.js', 'https://cdn.example.com/x.js']) };
  assert.deepEqual([...pageScripts(root, 'https://example.com/gitpa/graph.html')], [
    'https://example.com/gitpa/lsg-shell.js', 'https://example.com/gitpa/lsg-graph.js', 'https://cdn.example.com/x.js',
  ]);
});

test('a page that lists a script other than Gardener\'s in-place scripts opens with a full page load', async () => {
  const { doc, win, loads, watch } = site({
    '/gitpa/other/': { scripts: OTHER_SCRIPTS, home: true },
    '/gitpa/one/': { scripts: SHARED_SCRIPTS, home: true },
  });
  let shown = 0;
  const navigator = createNavigator({ document: doc, window: win, onPage: () => shown++ });
  const original = doc.nodes.main;
  watch();
  await navigator.navigate('/gitpa/other/');
  assert.deepEqual(loads, [['assign', 'https://example.com/gitpa/other/']]);
  assert.equal(doc.nodes.main, original);
  assert.equal(win.history.entries.length, 0);
  assert.equal(shown, 0);
  // A page whose scripts are all loaded still swaps in place.
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  assert.notEqual(doc.nodes.main, original);
  assert.equal(shown, 1);
  // Back or Forward onto such a page has already moved to its address, so it reloads there.
  win.location = new URL('https://example.com/gitpa/other/');
  watch();
  await navigator.navigate(win.location.href, { pop: true, state: null });
  assert.deepEqual(loads.at(-1), ['reload', 'https://example.com/gitpa/other/']);
  assert.equal(shown, 1);
  navigator.dispose();
});

test('the graph view swaps in place and runs its script after its stylesheet loads', async () => {
  const { doc, win, loads, watch } = site({
    '/gitpa/graph.html': { scripts: GRAPH_SCRIPTS, home: true, styles: [{ href: '/gitpa/lsg-graph.css' }, { text: '.graph{}' }] },
    '/gitpa/one/': { scripts: SHARED_SCRIPTS, home: true },
  });
  let shown = 0;
  const navigator = createNavigator({ document: doc, window: win, onPage: () => shown++ });
  const original = doc.nodes.main;
  watch();
  assert.equal(await navigator.navigate('/gitpa/graph.html#/graph'), true);
  assert.equal(loads.length, 0);
  assert.notEqual(doc.nodes.main, original);
  assert.equal(shown, 1);
  const [stylesheet] = appended(doc, 'link');
  assert.equal(stylesheet.getAttribute('href'), 'https://example.com/gitpa/lsg-graph.css');
  assert.equal(appended(doc, 'style')[0].textContent, '.graph{}');
  await tick();
  assert.equal(appended(doc, 'script').length, 0);
  stylesheet.onload();
  await tick();
  const [script] = appended(doc, 'script');
  assert.equal(script.src, 'https://example.com/gitpa/lsg-graph.js');
  assert.equal(script.async, false);
  // The script has drawn this document's graph, so the next graph page loads normally.
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  watch();
  await navigator.navigate('/gitpa/graph.html#/graph');
  assert.deepEqual(loads, [['assign', 'https://example.com/gitpa/graph.html#/graph']]);
  assert.equal(appended(doc, 'link').length, 1);
  navigator.dispose();
});

test('All pages runs its script once, then later All pages screens use its initializer', async () => {
  const { doc, win, loads, watch } = site({
    '/gitpa/pages.html': { scripts: ALL_PAGES_SCRIPTS, home: true, styles: [{ text: '.all-pages{}' }] },
    '/gitpa/pages-2.html': { scripts: ALL_PAGES_SCRIPTS, home: true, styles: [{ text: '.all-pages{}' }] },
    '/gitpa/one/': { scripts: SHARED_SCRIPTS, home: true },
  });
  const navigator = createNavigator({ document: doc, window: win });
  watch();
  assert.equal(await navigator.navigate('/gitpa/pages.html'), true);
  await tick();
  assert.deepEqual(appended(doc, 'script').map(script => script.src), ['https://example.com/gitpa/lsg-all-pages.js']);
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  assert.equal(await navigator.navigate('/gitpa/pages-2.html'), true);
  await tick();
  assert.equal(loads.length, 0);
  assert.equal(appended(doc, 'script').length, 1);
  assert.equal(appended(doc, 'style').length, 1);
  navigator.dispose();
});

test('a script waiting on its stylesheet is dropped when the reader moves on first', async () => {
  const { doc, win } = site({
    '/gitpa/graph.html': { scripts: GRAPH_SCRIPTS, home: true, styles: [{ href: '/gitpa/lsg-graph.css' }] },
    '/gitpa/one/': { scripts: SHARED_SCRIPTS, home: true },
  });
  const navigator = createNavigator({ document: doc, window: win });
  assert.equal(await navigator.navigate('/gitpa/graph.html#/graph'), true);
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  appended(doc, 'link')[0].onload();
  await tick();
  assert.equal(appended(doc, 'script').length, 0);
  navigator.dispose();
});

test('returning to the graph view after leaving it in place loads it again', async () => {
  const { doc, win, loads, watch } = site({
    '/gitpa/graph.html': { scripts: GRAPH_SCRIPTS, home: true },
    '/gitpa/one/': { scripts: SHARED_SCRIPTS, home: true },
  }, GRAPH_SCRIPTS);
  win.location = new URL('https://example.com/gitpa/graph.html#/graph');
  const navigator = createNavigator({ document: doc, window: win });
  // The document has run the graph script, but it drew only the graph it started with.
  assert.equal(await navigator.navigate('/gitpa/one/'), true);
  assert.equal(loads.length, 0);
  watch();
  await navigator.navigate('/gitpa/graph.html#/graph');
  assert.deepEqual(loads, [['assign', 'https://example.com/gitpa/graph.html#/graph']]);
  navigator.dispose();
});

test('the header follows the new page, including its Home button, and keeps revealed controls revealed', async () => {
  const { doc, win } = site({
    '/gitpa/': { scripts: SHARED_SCRIPTS, home: false },
    '/gitpa/episode/': { scripts: SHARED_SCRIPTS, home: true },
  });
  const homepage = headerNode(doc, { home: false });
  for (const selector of ['[data-lsg-left-toggle]', '[data-lsg-more]', '[data-lsg-right-toggle]']) homepage.controls[selector].hidden = false;
  homepage.controls['[data-lsg-left-toggle]'].setAttribute('aria-expanded', 'true');
  homepage.controls['[data-lsg-more]'].setAttribute('aria-expanded', 'true');
  doc.nodes['.lsg-header'] = homepage;
  const navigator = createNavigator({ document: doc, window: win, onPage: () => {
    assert.notEqual(doc.nodes['.lsg-header'], homepage);
  } });
  assert.equal(await navigator.navigate('/gitpa/episode/'), true);
  const episode = doc.nodes['.lsg-header'];
  assert.ok(episode.querySelector('a[aria-label="Home"]'));
  assert.equal(episode.querySelector('[data-lsg-left-toggle]').hidden, false);
  assert.equal(episode.querySelector('[data-lsg-left-toggle]').getAttribute('aria-expanded'), 'true');
  assert.equal(episode.querySelector('[data-lsg-more]').hidden, false);
  assert.equal(episode.querySelector('[data-lsg-more]').getAttribute('aria-expanded'), 'false');
  assert.equal(episode.querySelector('[data-lsg-right-toggle]').hidden, false);
  assert.equal(episode.querySelector('[data-lsg-right-toggle]').getAttribute('aria-expanded'), 'false');
  // Search was never revealed here, so it stays hidden.
  assert.equal(episode.querySelector('[data-lsg-search]').hidden, true);
  episode.querySelector('[data-lsg-search]').hidden = false;
  assert.equal(await navigator.navigate('/gitpa/'), true);
  const home = doc.nodes['.lsg-header'];
  assert.equal(home.querySelector('a[aria-label="Home"]'), null);
  assert.equal(home.querySelector('[data-lsg-search]').hidden, false);
  assert.equal(home.querySelector('[data-lsg-left-toggle]').hidden, false);
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


test('search routes match readable canonical titles without normalizing authored Unicode', () => {
  assert.equal(searchPageRoute('Ghost in the Patch', 'p.html'), '/gitpa/');
  assert.equal(searchPageRoute('Microfreak/Preset/016 Voidom', 'p.html'), '/gitpa/Microfreak/Preset/016%20Voidom/');
  assert.equal(searchPageRoute("Cafe\u0301/!()*'", 'p.html'), '/gitpa/Cafe%CC%81/%21%28%29%2A%27/');
  for (const title of ['', '../a', 'a//b', 'a/ b', 'a\\b', 'a\n', null]) {
    assert.equal(searchPageRoute(title, 'p.html'), 'p.html');
  }
});

test('search receives replaced revision metadata before page hooks, and resets when absent', async () => {
  const { doc, win } = fixture(async url => response(url.includes('disabled') ? 'disabled' : 'revision-two'));
  const selector = 'link[rel="lsg-search"]';
  const metadata = revision => { const node = new Node('link', doc); node.setAttribute('data-revision', revision); return node; };
  doc.head.append(metadata('revision-one'));
  const originalQuery = doc.querySelector;
  doc.querySelectorAll = query => query === selector ? doc.head.children.filter(node => !node.removed) : (doc.nodes[query] ? [doc.nodes[query]] : []);
  doc.querySelector = query => query === selector ? doc.querySelectorAll(query)[0] || null : originalQuery(query);
  win.DOMParser = class { parseFromString(html) { return { title: html, head: { querySelectorAll: () => [] }, querySelectorAll: () => [], querySelector: query => {
    if (query === selector) return html === 'disabled' ? null : metadata(html);
    return ['main', 'nav'].includes(query) ? new Node(query, doc) : null;
  } }; } };
  const seen = [];
  win.logseqGardenerInitSearch = (root, options) => {
    assert.equal(root, doc);
    assert.equal(options.resolvePage, searchPageRoute);
    seen.push(doc.querySelector(selector)?.getAttribute('data-revision') ?? null);
  };
  const navigator = createNavigator({ document: doc, window: win, onPage: () => {
    assert.equal(seen.at(-1), doc.querySelector(selector)?.getAttribute('data-revision') ?? null);
  } });
  assert.deepEqual(seen, ['revision-one']);
  await navigator.navigate('/gitpa/two/');
  await navigator.navigate('/gitpa/three/#part');
  await navigator.navigate('/gitpa/disabled/');
  assert.deepEqual(seen, ['revision-one', 'revision-two', 'revision-two', null]);
  assert.equal(doc.querySelectorAll(selector).length, 0);
  navigator.dispose();
});


test('shared hash routes follow content swaps and same-page zoom exit before focus', async () => {
  const { doc, win, fragment } = fixture();
  const events = [];
  let hookReady = false;
  win.addEventListener('hashchange', () => {
    events.push(win.location.href);
    assert.equal(fragment.focused, undefined);
    if (win.location.pathname === '/gitpa/one/') assert.ok(hookReady);
  });
  const navigator = createNavigator({ document: doc, window: win, onPage: () => { hookReady = true; } });
  await navigator.navigate('/gitpa/one/#zoom/1');
  await navigator.navigate('/gitpa/one/');
  await navigator.navigate('/gitpa/one/');
  assert.deepEqual(events, ['https://example.com/gitpa/one/#zoom/1', 'https://example.com/gitpa/one/']);
  await navigator.navigate('/gitpa/two/#part');
  assert.equal(events.at(-1), 'https://example.com/gitpa/two/#part');
  assert.ok(fragment.focused);
  navigator.dispose();
});


test('shared outline bullet anchors retain their native zoom controller ownership', async () => {
  let fetches = 0;
  const { doc, win } = fixture(async () => { fetches++; return response(); });
  const navigator = createNavigator({ document: doc, window: win });
  const anchor = new Node('a', doc);
  anchor.setAttribute('href', '#');
  anchor.matches = selector => selector === '.outline .bullet';
  const click = new Event('click', { cancelable: true });
  Object.defineProperty(click, 'button', { value: 0 });
  Object.defineProperty(click, 'target', { value: { closest: () => anchor } });
  doc.dispatchEvent(click); await tick();
  assert.equal(click.defaultPrevented, false);
  assert.equal(fetches, 0);
  assert.equal(win.history.entries.length, 0);
  navigator.dispose();
});
