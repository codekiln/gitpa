import { createNavigator } from './navigation.js';
import { createPluginAdapter } from './plugin-adapter.js';
import episodePlayer from './episode-player.js';
import headerSequence from './header-sequence.js';
import illuminatedInitials from './illuminated-initials.js';

const installations = new WeakMap();
const createSitePlugins = document => createPluginAdapter(document, [episodePlayer, headerSequence, illuminatedInitials]);

/** Legacy site entry while Gardener's shared plugin host is being defined. */
export function installSite(document, { createNavigation = createNavigator, createPlugins = createSitePlugins } = {}) {
  if (installations.has(document)) return installations.get(document);
  let navigation = null, plugins = null, started = false, disposed = false;
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
  function stop() {
    if (disposed) return;
    disposed = true;
    document.removeEventListener('DOMContentLoaded', start);
    document.removeEventListener('click', copyFeed);
    try {
      try { plugins?.dispose(); }
      finally { navigation?.dispose(); }
    } finally {
      navigation = null;
      plugins = null;
      installations.delete(document);
    }
  }
  const installation = { dispose: () => stop() };
  function start() {
    if (disposed || started) return;
    started = true;
    try {
      plugins = createPlugins(document);
      navigation = createNavigation({ document, window: document.defaultView, onPage() { plugins.adopt(); } });
    } catch (error) {
      stop();
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
