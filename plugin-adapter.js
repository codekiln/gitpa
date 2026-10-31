/**
 * Runs browser plugins written for Gardener's host API on Gitpa's own navigator
 * until Gitpa moves to Gardener's plugin host
 * (https://github.com/codekiln/gitpa/issues/93).
 *
 * The adapter adopts the current page when it is created; call `adopt()` after
 * each in-site navigation. Gitpa pages carry no plugin metadata, so `metadata`
 * is `{}` and `revision` is empty. Hosts offer `apiVersion`, `document`,
 * `baseURL` and `onPageAdopted`.
 */
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
  adopt();
  for (const plugin of plugins) {
    if (plugin?.apiVersion !== 1 || typeof plugin.setup !== 'function') {
      report(new Error(`Plugin ${plugin?.id} does not support host API version 1.`));
      continue;
    }
    const own = new Set();
    const host = {
      apiVersion: 1,
      document,
      get baseURL() { return baseURL ?? new URL('/gitpa/', document.URL).href; },
      onPageAdopted(listener) {
        listeners.add(listener);
        own.add(listener);
        if (current) notify(listener, current);
        return () => { listeners.delete(listener); own.delete(listener); };
      },
    };
    try {
      const cleanup = plugin.setup(host);
      if (typeof cleanup === 'function') cleanups.push(cleanup);
    } catch (error) {
      for (const listener of own) listeners.delete(listener);
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
      current = null;
    },
  };
}
