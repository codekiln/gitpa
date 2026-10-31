/** Restrict enhancement to the site's HTML documents. */
export function navigationURL(href, base) {
  try {
    const url = new URL(href, base);
    const current = new URL(base);
    return url.origin === current.origin && url.pathname.startsWith('/gitpa/') &&
      (url.pathname.endsWith('/') || url.pathname.endsWith('.html')) ? url : null;
  } catch { return null; }
}

/** Map canonical search page titles to the same readable routes as site_routes.py. */
export function searchPageRoute(title, fallback) {
  if (typeof title !== 'string') return fallback;
  const parts = title.split('/');
  if (!title || /[\\\x00-\x1f\x7f]/u.test(title) ||
      parts.some(part => !part || part === '.' || part === '..' || part !== part.trim())) return fallback;
  if (title === 'Ghost in the Patch') return '/gitpa/';
  try {
    return '/gitpa/' + parts.map(part => encodeURIComponent(part).replace(/[!'()*]/g,
      char => '%' + char.charCodeAt(0).toString(16).toUpperCase())).join('/') + '/';
  } catch { return fallback; }
}

export function sameDocument(left, right) {
  const a = new URL(left); const b = new URL(right);
  a.hash = ''; b.hash = '';
  return a.href === b.href;
}

/** Abort is an optimization; the token also protects against unabortable responses. */
export function latestRequest(fetcher, Abort = AbortController) {
  let sequence = 0;
  let controller;
  return {
    async run(url, commit) {
      const token = ++sequence;
      controller?.abort();
      controller = new Abort();
      try {
        const response = await fetcher(url, { signal: controller.signal, headers: { Accept: 'text/html' } });
        if (!response.ok) throw new Error(`Page could not load (${response.status}).`);
        const type = response.headers?.get('content-type');
        if (type && !type.toLowerCase().includes('text/html')) throw new Error('The address did not return a page.');
        const html = await response.text();
        if (token !== sequence) return false;
        await commit(html, response);
        return token === sequence;
      } catch (error) {
        if (token !== sequence) return false;
        throw error;
      }
    },
    cancel() { sequence++; controller?.abort(); },
  };
}

export function legacyResolver(fetcher, origin) {
  let routes;
  return async target => {
    if (!target.hash.startsWith('#/page/')) return target;
    let name;
    try { name = decodeURIComponent(target.hash.slice(7)).trim().replace(/^\/+|\/+$/g, '').normalize('NFC').toLowerCase(); }
    catch { throw new Error('Invalid legacy page address.'); }
    if (!routes) {
      routes = fetcher(new URL('/gitpa/legacy-routes.json', origin).href).then(response => {
        if (!response.ok) throw new Error('Page routes could not load.');
        return response.json();
      }).catch(error => { routes = null; throw error; });
    }
    const map = await routes;
    if (!Object.hasOwn(map, name)) throw new Error('Legacy page address was not found.');
    const resolved = navigationURL(map[name], new URL('/gitpa/', origin).href);
    if (!resolved) throw new Error('Legacy page address leaves the site.');
    return resolved;
  };
}

export function createNavigator({ document, window, onPage = () => {}, onError = () => {} }) {
  const history = window.history;
  const previousScrollRestoration = history.scrollRestoration;
  history.scrollRestoration = 'manual';
  let nextKey = 0;
  const key = () => `gitpa-${Date.now()}-${++nextKey}`;
  const stateWithKey = state => ({ ...state, gitpaNavigation: state?.gitpaNavigation || key() });
  let displayedURL = window.location.href;
  let displayedState = stateWithKey(history.state);
  history.replaceState(displayedState, '', displayedURL);
  const positions = new Map();
  const requests = latestRequest(window.fetch.bind(window), window.AbortController || AbortController);
  let disposed = false;
  let generation = 0;
  const resolveLegacy = legacyResolver(window.fetch.bind(window), window.location.origin);
  let recovery;
  const remember = () => positions.set(displayedState.gitpaNavigation, { x: window.scrollX, y: window.scrollY });
  const clearError = () => { recovery?.remove(); recovery = null; };
  const showError = (target, error) => {
    clearError();
    recovery = document.createElement('div');
    recovery.className = 'navigation-error';
    recovery.setAttribute('role', 'alert');
    recovery.setAttribute('tabindex', '-1');
    const message = document.createElement('span');
    message.textContent = 'Page could not load. ';
    const link = document.createElement('a');
    link.href = target.href;
    link.textContent = 'Open the page directly';
    link.setAttribute('data-native-navigation', '');
    recovery.append(message, link);
    // In-flow recovery stays visible without replacing the current recording or page.
    document.querySelector('main').prepend(recovery);
    recovery.focus();
    recovery.scrollIntoView({ block: 'nearest' });
    onError(error, target);
  };
  const scroll = (url, state, restore) => {
    const saved = restore && positions.get(state.gitpaNavigation);
    let element;
    if (url.hash) {
      let fragment;
      try { fragment = decodeURIComponent(url.hash.slice(1)); } catch { fragment = url.hash.slice(1); }
      element = document.getElementById(fragment) || document.getElementsByName(fragment)[0];
    }
    if (element) {
      if (typeof window.logseqGardenerRevealFragment === 'function') {
        window.logseqGardenerRevealFragment(url.hash, { scroll: false });
      }
      const hadTabindex = element.hasAttribute('tabindex');
      if (!hadTabindex) {
        element.setAttribute('tabindex', '-1');
        element.addEventListener('blur', () => element.removeAttribute('tabindex'), { once: true });
      }
      element.focus({ preventScroll: true });
    }
    if (saved) window.scrollTo(saved.x, saved.y);
    else if (element) element.scrollIntoView();
    else window.scrollTo(0, 0);
  };
  const adoptURL = (target, options) => {
    if (options.pop) displayedState = stateWithKey(options.state);
    else {
      displayedState = stateWithKey(options.replace ? history.state : {});
      history[options.replace ? 'replaceState' : 'pushState'](displayedState, '', target.href);
    }
    displayedURL = target.href;
  };
  const notifySharedRoute = oldURL => {
    // Shared outline routing listens to hashchange; history.pushState does not emit it.
    const event = typeof window.HashChangeEvent === 'function'
      ? new window.HashChangeEvent('hashchange', { oldURL, newURL: displayedURL })
      : new Event('hashchange');
    window.dispatchEvent(event);
  };
  async function navigate(href, options = {}) {
    let target = navigationURL(href, displayedURL);
    if (!target || disposed) return false;
    const token = ++generation;
    requests.cancel();
    remember();
    clearError();
    try { target = await resolveLegacy(target); }
    catch (error) {
      if (token !== generation || disposed) return false;
      showError(target, error);
      return false;
    }
    if (token !== generation || disposed) return false;
    if (sameDocument(target.href, displayedURL)) {
      requests.cancel();
      const previousURL = displayedURL;
      adoptURL(target, options);
      if (previousURL !== displayedURL) notifySharedRoute(previousURL);
      scroll(target, displayedState, options.pop);
      return true;
    }
    try {
      return await requests.run(target.href, (html, response) => {
        if (disposed) return;
        const responseURL = response.url ? navigationURL(response.url, target.href) : target;
        if (!responseURL) throw new Error('Page redirected outside the site.');
        // Keep the requested fragment when fetch's response URL omits it.
        if (!responseURL.hash) responseURL.hash = target.hash;
        const parsed = new window.DOMParser().parseFromString(html, 'text/html');
        const main = parsed.querySelector('main');
        const nav = parsed.querySelector('nav');
        if (!main || !nav || !document.querySelector('main') || !document.querySelector('nav')) throw new Error('Page has no site content.');
        const importedMain = document.importNode(main, true);
        const importedNav = document.importNode(nav, true);
        // Imported scripts never execute; remove them to keep that invariant explicit.
        for (const root of [importedMain, importedNav]) for (const script of root.querySelectorAll('script')) script.remove();
        const metadata = ['meta[name="gitpa-episode"]', 'link[rel="canonical"]', 'link[rel="lsg-search"]'].map(selector => [selector, parsed.querySelector(selector)]);
        const importedMetadata = metadata.map(([selector, node]) => [selector, node && document.importNode(node, true)]);
        document.querySelector('main').replaceWith(importedMain);
        document.querySelector('nav').replaceWith(importedNav);
        document.title = parsed.title;
        for (const [selector, node] of importedMetadata) {
          for (const existing of document.querySelectorAll(selector)) existing.remove();
          if (node) document.head.append(node);
        }
        const previousURL = displayedURL;
        adoptURL(responseURL, options);
        window.logseqGardenerInitOutline?.(importedMain);
        window.logseqGardenerInitProperties?.(importedMain);
        window.logseqGardenerInitBacklinks?.(importedMain);
        window.logseqGardenerInitTheme?.(importedNav);
        window.logseqGardenerInitSearch?.(document, { resolvePage: searchPageRoute });
        onPage({ url: responseURL, document });
        notifySharedRoute(previousURL);
        scroll(responseURL, displayedState, options.pop);
      });
    } catch (error) {
      if (disposed) return false;
      // A failed traversal retains its destination history entry for retry/Forward.
      // displayedURL still identifies the content behind the recovery message.
      showError(target, error);
      return false;
    }
  }
  const click = event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest?.('a[href]');
    if (!anchor || anchor.matches?.('.outline .bullet') || anchor.hasAttribute('download') || anchor.hasAttribute('data-native-navigation') || (anchor.target && anchor.target !== '_self') || anchor.rel?.split(/\s+/).includes('external')) return;
    const target = navigationURL(anchor.getAttribute('href'), displayedURL);
    if (!target) return;
    event.preventDefault();
    void navigate(target.href);
  };
  const pop = event => { void navigate(window.location.href, { pop: true, state: event.state }); };
  document.addEventListener('click', click);
  window.addEventListener('popstate', pop);
  const previousNavigate = window.gitpaNavigate;
  window.gitpaNavigate = navigate;
  window.logseqGardenerInitOutline?.(document);
  window.logseqGardenerInitProperties?.(document);
  window.logseqGardenerInitSearch?.(document, { resolvePage: searchPageRoute });
  const initialURL = new URL(displayedURL);
  if (initialURL.hash && !initialURL.hash.startsWith('#/page/')) scroll(initialURL, displayedState, false);
  return { navigate, dispose() {
    disposed = true;
    generation++;
    requests.cancel();
    clearError();
    document.removeEventListener('click', click);
    window.removeEventListener('popstate', pop);
    history.scrollRestoration = previousScrollRestoration;
    window.gitpaNavigate = previousNavigate;
  } };
}
