const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
let createPluginAdapter;
before(async () => {
  const source = readFileSync(join(__dirname, '../site/plugin-adapter.js'), 'utf8');
  ({ createPluginAdapter } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`));
});

/** A document whose head holds `data-gitpa-plugin` scripts, as the build publishes them. */
function fakeDocument(published = {}) {
  const body = { children: [], append(node) { this.children.push(node); node.parent = this; } };
  const element = tag => ({ tag, attributes: {}, style: {}, setAttribute(name, value) { this.attributes[name] = value; },
    remove() { const list = this.parent?.children; if (list) list.splice(list.indexOf(this), 1); } });
  const document = { title: 'Page', URL: 'https://example.com/gitpa/Page/', body, published,
    querySelector: () => ({}),
    querySelectorAll: selector => {
      assert.equal(selector, 'script[data-gitpa-plugin]');
      return Object.entries(document.published).map(([id, text]) => ({ getAttribute: () => id, textContent: text }));
    },
    createElement: element };
  return document;
}
const manifest = (id, extra = {}) => ({ id, apiVersion: 1, version: '1.0.0', ...extra });

test('a plugin receives only the page properties its manifest requests', () => {
  const document = fakeDocument({ alpha: '{"prev":"[[A]]","secret":"x"}', beta: '{"prev":"[[Z]]"}' });
  const received = {};
  const plugins = ['alpha', 'beta', 'gamma'].map(id => ({ ...manifest(id, { pageProperties: id === 'gamma' ? [] : ['prev', 'next'] }),
    setup(host) { host.onPageAdopted(({ metadata }) => { received[id] = metadata; }); return () => {}; } }));
  const adapter = createPluginAdapter(document, plugins);
  assert.deepEqual(received, { alpha: { prev: '[[A]]' }, beta: { prev: '[[Z]]' }, gamma: {} });
  document.published = { alpha: '{"next":"[[B]]"}' };
  adapter.adopt();
  assert.deepEqual(received, { alpha: { next: '[[B]]' }, beta: {}, gamma: {} });
  adapter.dispose();
});

test('unreadable published properties are reported and the plugin still runs with none', () => {
  const errors = [];
  let metadata;
  createPluginAdapter(fakeDocument({ alpha: '{not json' }), [{ ...manifest('alpha', { pageProperties: ['prev'] }),
    setup(host) { host.onPageAdopted(adoption => { metadata = adoption.metadata; }); return () => {}; } }],
  { report: error => errors.push(error.message) });
  assert.deepEqual(metadata, {});
  assert.match(errors[0], /alpha.*unreadable/);
});

test('a plugin that fails in setup or on a page leaves the others working', () => {
  const errors = [];
  const adopted = [];
  const failingSetup = { ...manifest('broken-setup'), setup(host) { host.onPageAdopted(() => adopted.push('broken-setup')); host.persistentRegion('x'); throw new Error('setup'); } };
  const failingPage = { ...manifest('broken-page'), setup(host) { host.onPageAdopted(() => { throw new Error('page'); }); return () => {}; } };
  const working = { ...manifest('working'), setup(host) { host.onPageAdopted(() => adopted.push('working')); return () => {}; } };
  const document = fakeDocument();
  const adapter = createPluginAdapter(document, [failingSetup, failingPage, working], { report: error => errors.push(error.message) });
  adapter.adopt();
  adapter.adopt();
  assert.deepEqual(adopted, ['broken-setup', 'working', 'working', 'working'], 'the failed plugin is unsubscribed after its first page');
  assert.deepEqual(errors, ['setup', 'page', 'page', 'page']);
  assert.equal(document.body.children.length, 0, 'the failed plugin leaves no region behind');
  adapter.dispose();
});

test('invalid manifests and duplicate ids are reported and skipped', () => {
  const errors = [];
  const setup = () => () => {};
  const ran = [];
  const good = { ...manifest('good'), setup(host) { ran.push('good'); return () => {}; } };
  createPluginAdapter(fakeDocument(), [
    { ...manifest('Bad_Id'), setup }, { id: 'no-version', apiVersion: 1, setup }, { ...manifest('v2'), apiVersion: 2, setup },
    { ...manifest('props', { pageProperties: 'prev' }), setup }, { ...manifest('no-setup') }, good, good,
  ], { report: error => errors.push(error.message) });
  assert.deepEqual(ran, ['good']);
  assert.equal(errors.length, 6);
  assert.match(errors.at(-1), /good is listed twice/);
});

test('a persistent region lives in the page body until the plugin or site disposes it', () => {
  const document = fakeDocument();
  let region;
  const adapter = createPluginAdapter(document, [{ ...manifest('player'), setup(host) {
    region = host.persistentRegion('recording');
    assert.equal(host.persistentRegion('recording'), region);
    return () => {};
  } }]);
  assert.equal(document.body.children.length, 1);
  assert.equal(region.element.attributes['data-gitpa-region'], 'player-recording');
  adapter.dispose();
  assert.equal(document.body.children.length, 0);
});
