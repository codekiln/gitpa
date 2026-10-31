const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const url = source => `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const playerSource = readFileSync(join(__dirname, '../site/player.js'), 'utf8');
let installSite;
before(async () => {
  const navigation = url(readFileSync(join(__dirname, '../site/navigation.js'), 'utf8'));
  const site = name => url(readFileSync(join(__dirname, '../site', name), 'utf8'));
  const bootstrap = readFileSync(join(__dirname, '../site/bootstrap.js'), 'utf8')
    .replace("'./player.js'", JSON.stringify(url(playerSource)))
    .replace("'./navigation.js'", JSON.stringify(navigation))
    .replace("'./plugin-adapter.js'", JSON.stringify(site('plugin-adapter.js')))
    .replace("'./header-sequence.js'", JSON.stringify(site('header-sequence.js')));
  ({ installSite } = await import(url(bootstrap)));
});

function fixture(loading = false) {
  const document = new EventTarget(); document.readyState = loading ? 'loading' : 'complete'; document.defaultView = {};
  const counts = { players: 0, navigators: 0, pages: 0, playerDisposals: 0, navigationDisposals: 0,
    pluginAdapters: 0, pluginPages: 0, pluginDisposals: 0 };
  let hook;
  const factories = {
    createPlayer(doc) { assert.equal(doc, document); counts.players++; return {
      showPage() { counts.pages++; }, dispose() { counts.playerDisposals++; },
    }; },
    createPlugins(doc) { assert.equal(doc, document); counts.pluginAdapters++; return {
      adopt() { counts.pluginPages++; }, dispose() { counts.pluginDisposals++; },
    }; },
    createNavigation(options) { assert.equal(options.document, document); assert.equal(options.window, document.defaultView);
      counts.navigators++; hook = options.onPage; return { dispose() { counts.navigationDisposals++; } }; },
  };
  return { document, counts, factories, adopt: () => hook(), ready() {
    document.readyState = 'complete'; document.dispatchEvent(new Event('DOMContentLoaded'));
  } };
}

test('importing player exports with a browser document performs no automatic startup', async () => {
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'document');
  const document = new EventTarget(); document.readyState = 'loading';
  let listeners = 0;
  document.addEventListener = () => { listeners++; };
  Object.defineProperty(globalThis, 'document', { configurable: true, value: document });
  try {
    const imported = await import(url(playerSource + '\n// distinct purity fixture'));
    assert.equal(typeof imported.createSitePlayer, 'function');
    assert.equal(listeners, 0);
  } finally {
    if (previous) Object.defineProperty(globalThis, 'document', previous);
    else delete globalThis.document;
  }
});

test('repeated entry installation starts one player and router after readiness', () => {
  const f = fixture(true), first = installSite(f.document, f.factories);
  assert.equal(installSite(f.document, f.factories), first);
  assert.equal(f.counts.players, 0);
  f.ready(); f.ready(); f.adopt(); f.adopt();
  assert.deepEqual(f.counts, { players: 1, navigators: 1, pages: 2, playerDisposals: 0, navigationDisposals: 0,
    pluginAdapters: 1, pluginPages: 2, pluginDisposals: 0 });
  first.dispose(); first.dispose();
  assert.equal(f.counts.navigationDisposals, 1); assert.equal(f.counts.playerDisposals, 1);
  assert.equal(f.counts.pluginDisposals, 1);
});

test('disposing pending startup prevents a late readiness event and allows a fresh installation', () => {
  const f = fixture(true), first = installSite(f.document, f.factories);
  first.dispose(); f.ready();
  assert.equal(f.counts.players, 0); assert.equal(f.counts.navigators, 0); assert.equal(f.counts.pluginAdapters, 0);
  const next = installSite(f.document, f.factories);
  assert.notEqual(next, first); assert.equal(f.counts.players, 1);
  next.dispose();
});

test('failed router construction disposes its player and does not strand the installation', () => {
  const f = fixture();
  assert.throws(() => installSite(f.document, { ...f.factories, createNavigation() { throw new Error('failed'); } }), /failed/);
  assert.equal(f.counts.playerDisposals, 1); assert.equal(f.counts.pluginDisposals, 1);
  const retry = installSite(f.document, f.factories);
  assert.equal(f.counts.players, 2); assert.equal(f.counts.navigators, 1);
  retry.dispose();
});

test('copy feed button reports success and clipboard failures', async () => {
  const f = fixture(), status = { textContent: '' };
  let copied;
  f.document.closest = selector => selector === '[data-copy-feed]' ? f.document : null;
  f.document.parentElement = { querySelector: () => status };
  f.document.defaultView.navigator = { clipboard: { async writeText(value) { copied = value; } } };
  const installation = installSite(f.document, f.factories);
  f.document.dispatchEvent(new Event('click'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(copied, 'https://codekiln.github.io/gitpa/rss.xml');
  assert.equal(status.textContent, 'Feed URL copied.');
  f.document.defaultView.navigator.clipboard.writeText = async () => { throw new Error('denied'); };
  f.document.dispatchEvent(new Event('click'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(status.textContent, 'Copy the podcast RSS feed link instead.');
  installation.dispose();
});
