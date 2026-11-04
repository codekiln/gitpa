/**
 * Runs browser plugins written for Gardener's host API on Gitpa's own navigator
 * until Gitpa moves to Gardener's plugin host
 * (https://github.com/codekiln/gitpa/issues/93).
 *
 * The adapter adopts the current page when it is created; call `adopt()` after
 * each in-site navigation. A plugin is its manifest (`id`, `apiVersion`,
 * `version`, optional `pageProperties`) plus `setup`. The build publishes the
 * properties a manifest requests in a
 * `<script type="application/json" data-gitpa-plugin="<id>">` element of the
 * page head; the adapter passes them as `metadata` and ignores any other key.
 * `revision` is empty. Hosts offer `apiVersion`, `document`, `baseURL`,
 * `onPageAdopted` and `persistentRegion`.
 */
const ID = /^[a-z0-9]+(-[a-z0-9]+)*$/;
function manifestError(plugin) {
  if (plugin?.apiVersion !== 1) return `Plugin ${plugin?.id} does not support host API version 1.`;
  if (typeof plugin.id !== 'string' || !ID.test(plugin.id)) return `Plugin id ${JSON.stringify(plugin.id)} is not lowercase words joined by hyphens.`;
  if (typeof plugin.version !== 'string' || !plugin.version) return `Plugin ${plugin.id} declares no version.`;
  if (plugin.pageProperties !== undefined && !(Array.isArray(plugin.pageProperties) && plugin.pageProperties.every(key => typeof key === 'string'))) {
    return `Plugin ${plugin.id} declares pageProperties that are not a list of names.`;
  }
  if (typeof plugin.setup !== 'function') return `Plugin ${plugin.id} has no setup function.`;
  return null;
}
export function createPluginAdapter(document, plugins, { baseURL, report = error => console.error(error) } = {}) {
  const listeners = new Set();
  const cleanups = [];
  let current = null, controller = null, disposed = false;
  const notify = (listener, adoption) => {
    try { listener(adoption); }
    catch (error) { report(error); }
  };
  function adopt() {
    if (disposed) return;
    controller?.abort();
    controller = new AbortController();
    const title = document.title ?? '';
    current = {
      page: { id: title.normalize('NFC').toLowerCase(), title, url: document.URL },
      main: document.querySelector('main'),
      revision: '',
      metadata: {},
      signal: controller.signal,
    };
    for (const listener of [...listeners]) notify(listener, current);
  }
  const regions = new Set();
  // Only the properties a plugin's manifest requests reach it.
  function metadataFor(plugin) {
    const wanted = plugin.pageProperties ?? [];
    const element = wanted.length && [...document.querySelectorAll('script[data-gitpa-plugin]')]
      .find(script => script.getAttribute('data-gitpa-plugin') === plugin.id);
    if (!element) return {};
    try {
      const values = JSON.parse(element.textContent);
      return Object.fromEntries(wanted.filter(key => Object.hasOwn(values, key)).map(key => [key, values[key]]));
    } catch (error) {
      report(new Error(`Plugin ${plugin.id} has unreadable page properties: ${error.message}`));
      return {};
    }
  }
  adopt();
  const seen = new Set();
  for (const plugin of plugins) {
    const problem = manifestError(plugin) ?? (seen.has(plugin.id) ? `Plugin ${plugin.id} is listed twice.` : null);
    if (problem) {
      report(new Error(problem));
      continue;
    }
    seen.add(plugin.id);
    const own = new Set();
    const adoptionFor = adoption => ({ ...adoption, metadata: metadataFor(plugin) });
    const mine = new Map();
    const host = {
      apiVersion: 1,
      document,
      get baseURL() { return baseURL ?? new URL('/gitpa/', document.URL).href; },
      onPageAdopted(listener) {
        const wrapped = adoption => listener(adoptionFor(adoption));
        listeners.add(wrapped);
        own.add(wrapped);
        if (current) notify(wrapped, current);
        return () => { listeners.delete(wrapped); own.delete(wrapped); };
      },
      persistentRegion(localId) {
        if (mine.has(localId)) return mine.get(localId);
        const element = document.createElement('div');
        element.setAttribute('data-gitpa-region', `${plugin.id}-${localId}`);
        element.setAttribute('style', 'display: contents');
        document.body.append(element);
        const region = { element, dispose() { element.remove(); regions.delete(region); mine.delete(localId); } };
        regions.add(region);
        mine.set(localId, region);
        return region;
      },
    };
    try {
      const cleanup = plugin.setup(host);
      if (typeof cleanup === 'function') cleanups.push(cleanup);
    } catch (error) {
      for (const listener of own) listeners.delete(listener);
      for (const region of mine.values()) region.dispose();
      report(error);
    }
  }
  return {
    adopt,
    dispose() {
      if (disposed) return;
      disposed = true;
      controller?.abort();
      for (const cleanup of cleanups.splice(0)) {
        try { cleanup(); }
        catch (error) { report(error); }
      }
      listeners.clear();
      for (const region of [...regions]) region.dispose();
      current = null;
    },
  };
}
