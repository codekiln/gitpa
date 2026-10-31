import { createSitePlayer } from './player.js';
import { createNavigator } from './navigation.js';

const installations = new WeakMap();

/** Legacy site entry while Gardener's shared plugin host is being defined. */
export function installSite(document, { createPlayer = createSitePlayer, createNavigation = createNavigator } = {}) {
  if (installations.has(document)) return installations.get(document);
  let player = null, navigation = null, started = false, disposed = false;
  function stop(restoreOriginal = false) {
    if (disposed) return;
    disposed = true;
    document.removeEventListener('DOMContentLoaded', start);
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
  installations.set(document, installation);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
  return installation;
}

if (typeof document !== 'undefined') installSite(document);
