import { createSitePlayer } from './player.js';
import { createNavigator } from './navigation.js';

const installations = new WeakMap();

/** Legacy site entry while Gardener's shared plugin host is being defined. */
export function installSite(document, { createPlayer = createSitePlayer, createNavigation = createNavigator } = {}) {
  if (installations.has(document)) return installations.get(document);
  let player = null, navigation = null, started = false, disposed = false;
  async function copyFeed(event) {
    const button = event.target.closest?.('[data-copy-feed]');
    if (!button) return;
    const status = button.parentElement.querySelector('[data-copy-feed-status]');
    try {
      await document.defaultView.navigator.clipboard.writeText('https://codekiln.github.io/gitpa/rss.xml');
      status.textContent = 'Feed URL copied.';
    } catch {
      status.textContent = 'Copy the podcast RSS feed link instead.';
    }
  }
  function stop(restoreOriginal = false) {
    if (disposed) return;
    disposed = true;
    document.removeEventListener('DOMContentLoaded', start);
    document.removeEventListener('click', copyFeed);
    try {
      try { navigation?.dispose(); }
      finally { player?.dispose({ restoreOriginal }); }
    } finally {
      player = null;
      navigation = null;
      installations.delete(document);
    }
  }
  const installation = { dispose: () => stop() };
  function start() {
    if (disposed || started) return;
    started = true;
    try {
      player = createPlayer(document);
      navigation = createNavigation({ document, window: document.defaultView, onPage: player.showPage });
    } catch (error) {
      stop(true);
      throw error;
    }
  }
  document.addEventListener('click', copyFeed);
  installations.set(document, installation);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
  return installation;
}

if (typeof document !== 'undefined') installSite(document);
