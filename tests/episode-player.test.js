const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const url = source => `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
let episodePlayerPlugin, manifest;
before(async () => {
  const source = readFileSync(join(__dirname, '../site/episode-player.js'), 'utf8')
    .replace("'./player.js'", JSON.stringify(url('export const createSitePlayer = () => { throw new Error("unused"); };')));
  ({ episodePlayerPlugin, manifest } = await import(url(source)));
});

function host() {
  let controller = new AbortController(), listener;
  const removedClasses = [], mounted = [];
  const region = { element: { append(node) { node.parentElement = this; mounted.push(node); } },
    disposed: 0, dispose() { this.disposed++; } };
  const api = { apiVersion: 1, document: { body: { classList: { remove: name => removedClasses.push(name) } } },
    baseURL: 'https://example.com/garden/',
    onPageAdopted(fn) { listener = fn; fn({ signal: controller.signal }); return () => { listener = null; }; },
    persistentRegion(id) { assert.equal(id, 'recording'); return region; } };
  return { api, region, removedClasses, mounted, next() {
    controller.abort(); controller = new AbortController(); listener?.({ signal: controller.signal });
  }, get listener() { return listener; } };
}

function manager() {
  return { audio: { currentTime: 62, paused: 0,
      pause() { this.paused++; } },
    footer: { parentElement: null, removed: 0, remove() { this.removed++; } },
    shown: 0, disposed: 0, showPage() { this.shown++; }, dispose() { this.disposed++; } };
}

test('the plugin declares a manifest', () => {
  assert.deepEqual(manifest, { id: 'episode-player', apiVersion: 1, version: '1.0.0', module: 'episode-player.js',
    styles: ['player.css'], activation: 'after-load', pageProperties: [] });
  const plugin = episodePlayerPlugin(() => manager());
  for (const key of Object.keys(manifest)) assert.deepEqual(plugin[key], manifest[key]);
});

test('the player factory handles initial adoption once and survives page-scope replacement', () => {
  const h = host(), player = manager(); let factories = 0;
  const plugin = episodePlayerPlugin(document => { assert.equal(document, h.api.document); factories++; return player; });
  const dispose = plugin.setup(h.api);
  assert.equal(factories, 1);
  assert.equal(player.shown, 0, 'the existing factory already handled the initial page');
  for (let i = 0; i < 20; i++) { h.next(); player.audio.currentTime++; }
  assert.equal(factories, 1);
  assert.equal(player.shown, 20);
  assert.equal(player.audio.currentTime, 82);
  assert.equal(player.audio.paused, 0, 'page AbortSignals do not dispose the site player');
  assert.equal(h.mounted.length, 1);
  dispose();
});

test('site disposal releases the subscription and pauses the media once, including stale callbacks', () => {
  const h = host(), player = manager();
  const dispose = episodePlayerPlugin(() => player).setup(h.api);
  const stale = h.listener;
  dispose(); dispose(); stale({ signal: new AbortController().signal });
  assert.equal(h.listener, null);
  assert.equal(player.audio.paused, 1);
  assert.equal(player.disposed, 1);
  assert.equal(player.footer.removed, 1);
  assert.equal(h.region.disposed, 1);
  assert.equal(player.shown, 0);
  assert.deepEqual(h.removedClasses, ['has-episode-player']);
});

test('an ordinary landing page can acquire the persistent footer on a later episode', () => {
  const h = host(), player = manager(), footer = player.footer;
  player.footer = null; player.audio = null;
  player.showPage = () => { player.footer = footer; };
  const dispose = episodePlayerPlugin(() => player).setup(h.api);
  assert.equal(h.mounted.length, 0);
  h.next();
  assert.equal(h.mounted.length, 1);
  assert.equal(footer.parentElement, h.region.element);
  dispose();
});
