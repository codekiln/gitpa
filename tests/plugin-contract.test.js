const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { mkdtempSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');
let directory, episodePlayerPlugin;
const root = resolve(__dirname, '..');

before(() => {
  directory = mkdtempSync(join(tmpdir(), 'gitpa-plugin-contract-'));
  execFileSync(process.execPath, [join(root, 'node_modules/typescript/bin/tsc'), '-p', 'contracts/tsconfig.json',
    '--noEmit', 'false', '--outDir', directory], { cwd: root, stdio: 'inherit' });
  ({ episodePlayerPlugin } = require(join(directory, 'experiments/plugins/episode-player.js')));
});
after(() => { if (directory) rmSync(directory, { recursive: true, force: true }); });

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
  return { audio: { currentTime: 62, paused: 0, cleared: 0, loaded: 0, removedSources: 0,
      pause() { this.paused++; }, removeAttribute(name) { assert.equal(name, 'src'); this.cleared++; },
      querySelectorAll(selector) { assert.equal(selector, 'source'); return [{ remove: () => this.removedSources++ }]; },
      load() { this.loaded++; } },
    footer: { parentElement: null, removed: 0, remove() { this.removed++; } },
    shown: 0, disposed: 0, showPage() { this.shown++; }, dispose() { this.disposed++; } };
}

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

test('site disposal releases the subscription and media once, including stale callbacks', () => {
  const h = host(), player = manager();
  const dispose = episodePlayerPlugin(() => player).setup(h.api);
  const stale = h.listener;
  dispose(); dispose(); stale({ signal: new AbortController().signal });
  assert.equal(h.listener, null);
  assert.equal(player.audio.paused, 1);
  assert.equal(player.audio.cleared, 1);
  assert.equal(player.audio.removedSources, 1);
  assert.equal(player.audio.loaded, 1);
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
