/** Match only links into this recording, preserving ordinary links as a fallback. */
export function chapterTime(href, source, base) {
  try {
    const target = new URL(href, base);
    const recording = new URL(source, base);
    const match = /^#t=(\d+)$/.exec(target.hash);
    target.hash = '';
    recording.hash = '';
    if (!match || target.href !== recording.href) return null;
    const seconds = Number(match[1]);
    return Number.isSafeInteger(seconds) ? seconds : null;
  } catch { return null; }
}

export function clampTime(seconds, duration) {
  return Number.isFinite(duration) && duration >= 0 ? Math.min(seconds, duration) : seconds;
}

/** Owns pending seeks, while all playback controls remain native audio controls. */
export function createPlayer(audio, update = () => {}) {
  let request = 0;
  let pending = null;
  let chapter = '';
  let failure = '';
  let disposed = false;
  const listeners = [];
  const publish = () => {
    if (!disposed) update({ chapter, status: failure || (audio.ended ? 'Ended' : audio.paused ? 'Paused' : 'Playing'), pending: pending !== null });
  };
  const listen = (name, handler) => {
    audio.addEventListener(name, handler);
    listeners.push([name, handler]);
  };
  const applySeek = () => {
    if (pending === null || audio.readyState < 1) return;
    try {
      audio.currentTime = clampTime(pending, audio.duration);
      pending = null;
    } catch { failure = 'Unable to seek. Use the recording controls to try again.'; }
  };
  const metadata = () => { applySeek(); publish(); };
  listen('loadedmetadata', metadata);
  listen('durationchange', metadata);
  for (const name of ['playing', 'pause', 'ended']) listen(name, publish);
  listen('play', () => { failure = ''; publish(); });
  listen('error', () => {
    request += 1;
    pending = null;
    failure = 'Recording could not load. Open the full recording to try again.';
    publish();
  });
  publish();
  return {
    seek(seconds, label = '') {
      if (disposed || !Number.isSafeInteger(seconds) || seconds < 0) return false;
      const token = ++request;
      chapter = label;
      failure = '';
      pending = seconds;
      applySeek();
      // Call play synchronously inside the click gesture, even before metadata exists.
      try {
        const playing = audio.play();
        Promise.resolve(playing).catch(() => {
          if (!disposed && token === request) {
            failure = 'Press play in the recording controls to listen.';
            publish();
          }
        });
      } catch {
        failure = 'Press play in the recording controls to listen.';
      }
      publish();
      return true;
    },
    dispose() {
      disposed = true;
      request += 1;
      for (const [name, handler] of listeners) audio.removeEventListener(name, handler);
    },
  };
}

export function currentChapter(chapters, seconds) {
  let current = null;
  for (const chapter of chapters) {
    if (chapter.seconds > seconds) break;
    current = chapter;
  }
  return current;
}

/** The chapters enclosing `current`, outermost first, ending with `current` itself. */
export function chapterTrail(chapters, current) {
  const byId = new Map(chapters.map(chapter => [chapter.id, chapter]));
  const trail = [];
  for (let chapter = current; chapter && !trail.includes(chapter); chapter = byId.get(chapter.parent)) trail.unshift(chapter);
  return trail;
}

/** Playback context survives page changes; changing context is always explicit. */
export function createEpisodeSession(audio, update = () => {}) {
  let context = null;
  let controller = null;
  let playback = { status: 'Paused' };
  const publish = () => {
    if (!context) return;
    update({ context, current: currentChapter(context.chapters, audio.currentTime), ...playback });
  };
  for (const name of ['timeupdate', 'seeked', 'loadedmetadata']) audio.addEventListener(name, publish);
  const adopt = (next, replace) => {
    if (context?.source === next.source) return;
    controller?.dispose();
    if (replace) {
      audio.pause();
      audio.setAttribute('src', next.source);
      audio.load();
    }
    context = next;
    controller = createPlayer(audio, state => { playback = state; publish(); });
    publish();
  };
  return {
    adopt(next) { if (!context) adopt(next, false); },
    activate(next, seconds = 0) {
      adopt(next, context !== null);
      controller.seek(seconds, next.title);
      publish();
    },
    refresh: publish,
    get context() { return context; },
    dispose() {
      controller?.dispose();
      for (const name of ['timeupdate', 'seeked', 'loadedmetadata']) audio.removeEventListener(name, publish);
    },
  };
}

/** The build marks episodes explicitly so manuals with audio stay ordinary pages. */
export function readEpisode(document) {
  const marker = document.querySelector('meta[name="gitpa-episode"]');
  const main = document.querySelector('main');
  const raw = marker?.getAttribute('content');
  if (!raw || !main) return null;
  const source = new URL(raw, document.baseURI).href;
  const recordings = [...main.querySelectorAll('audio')].filter(audio => {
    const value = audio.getAttribute('src');
    return !audio.closest('.linked-references') && value && new URL(value, document.baseURI).href === source;
  });
  if (recordings.length !== 1) return null;
  const canonical = document.querySelector('link[rel="canonical"]')?.getAttribute('href');
  const url = new URL(canonical || document.baseURI, document.baseURI);
  url.hash = '';
  const titleHeading = main.querySelector('ul h1') || main.querySelector('h1');
  const startHeading = main.querySelector('h1');
  if (startHeading && !startHeading.id) startHeading.id = 'episode-start';
  const chapters = [];
  const blocks = new Map();
  const used = new Map();
  for (const heading of main.querySelectorAll('h1, h2, h3, h4, h5, h6')) {
    if (heading.closest('.linked-references')) continue;
    for (const anchor of heading.querySelectorAll('a[href]')) {
      const seconds = chapterTime(anchor.getAttribute('href'), source, document.baseURI);
      if (seconds === null) continue;
      const count = (used.get(seconds) || 0) + 1;
      used.set(seconds, count);
      if (!heading.id) heading.id = `chapter-${seconds}${count > 1 ? `-${count}` : ''}`;
      const chapter = { seconds, label: heading.textContent.trim(), id: heading.id,
        href: `${url.href}#${encodeURIComponent(heading.id)}`, parent: null };
      chapters.push(chapter);
      const block = heading.closest('li');
      if (block) blocks.set(block, chapter);
      break;
    }
  }
  // A chapter heading in a block nested under another chapter's block is its subchapter.
  for (const [block, chapter] of blocks) {
    for (let outer = block.parentElement?.closest('li'); outer; outer = outer.parentElement?.closest('li')) {
      if (blocks.has(outer)) { chapter.parent = blocks.get(outer).id; break; }
    }
  }
  chapters.sort((a, b) => a.seconds - b.seconds);
  const startHref = startHeading ? `${url.href}#${encodeURIComponent(startHeading.id)}` : url.href;
  return { source, url: url.href, startHref, title: titleHeading?.textContent.trim() || document.title,
    chapters, audio: recordings[0] };
}

const managers = new WeakMap();
export function createSitePlayer(document) {
  if (managers.has(document)) return managers.get(document);
  let audio = null;
  let footer = null;
  let session = null;
  let page = null;
  let observer = null;
  let originalParent = null, originalNext = null, originalOrigin = null, disposed = false;
  // The chapter trail and heading highlight change only with the chapter or the page.
  let shown = null;
  let disposeView = () => {};
  const makeFooter = initial => {
    audio = initial.audio;
    originalParent = audio.parentElement;
    originalNext = audio.nextSibling;
    originalOrigin = audio.closest('li');
    footer = document.createElement('footer');
    footer.className = 'episode-player';
    footer.setAttribute('aria-label', 'Episode recording');
    const details = document.createElement('div');
    details.className = 'episode-player-details';
    const episode = document.createElement('a');
    episode.className = 'episode-player-episode';
    const trail = document.createElement('span');
    trail.className = 'episode-player-chapter';
    const playing = document.createElement('a');
    playing.className = 'episode-player-return';
    playing.textContent = 'Return to playing spot';
    const status = document.createElement('span');
    status.className = 'episode-player-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    const recording = document.createElement('a');
    recording.className = 'episode-player-recording';
    recording.textContent = 'Full recording';
    details.append(episode, trail, playing, status, recording);
    originalOrigin?.classList.add('episode-recording-origin');
    audio.controls = true;
    audio.setAttribute('aria-label', 'Full episode recording');
    footer.append(details, audio);
    document.body.append(footer);
    document.body.classList.add('has-episode-player');
    session = createEpisodeSession(audio, state => {
      const start = state.context.startHref || `${state.context.url}#episode-start`;
      recording.href = state.context.source;
      episode.href = start;
      episode.textContent = state.context.title;
      playing.href = state.current?.href || start;
      status.textContent = state.status;
      const currentPage = document.querySelector('link[rel="canonical"]')?.getAttribute('href');
      const here = new URL(currentPage || document.baseURI, document.baseURI).href.split('#')[0];
      const key = `${state.context.source} ${here} ${state.current?.id}`;
      if (key === shown) return;
      shown = key;
      const links = chapterTrail(state.context.chapters, state.current).map(item => {
        const link = document.createElement('a');
        link.href = item.href;
        link.textContent = item.label;
        return link;
      });
      trail.replaceChildren(...links.flatMap((link, index) => {
        if (!index) return [link];
        const separator = document.createElement('span');
        separator.setAttribute('aria-hidden', 'true');
        separator.textContent = '›';
        return [separator, link];
      }));
      for (const heading of document.querySelectorAll('main h1, main h2, main h3, main h4, main h5, main h6')) {
        const selected = here === state.context.url && heading.id === state.current?.id;
        heading.classList.toggle('is-current-chapter', selected);
        for (const link of heading.querySelectorAll('a[href]')) {
          if (selected && chapterTime(link.getAttribute('href'), state.context.source, document.baseURI) === state.current?.seconds) link.setAttribute('aria-current', 'true');
          else link.removeAttribute('aria-current');
        }
      }
    });
    session.adopt(initial);
    const size = () => document.body.style.setProperty('--episode-player-height', `${footer.getBoundingClientRect().height}px`);
    const Observer = document.defaultView?.ResizeObserver;
    observer = Observer ? new Observer(size) : null;
    observer?.observe(footer);
    size();
  };
  const showPage = () => {
    if (disposed) return;
    disposeView();
    disposeView = () => {};
    page = readEpisode(document);
    shown = null;
    if (!page) { session?.refresh(); return; }
    if (!audio) { makeFooter(page); return; }
    const candidate = page.audio;
    // The footer already holds the recording of the episode it is playing.
    if (candidate !== audio && page.source === session.context?.source) {
      candidate.closest('li')?.classList.add('episode-recording-origin');
      candidate.remove();
    } else if (candidate !== audio) {
      candidate.closest('li')?.classList.add('episode-recording-origin');
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'episode-play';
      button.textContent = 'Play this episode';
      const play = () => session.activate(page);
      button.addEventListener('click', play);
      candidate.replaceWith(button);
      disposeView = () => button.removeEventListener('click', play);
    }
    session.refresh();
  };
  const originalAnchor = anchor => anchor?.matches?.('a[href]') && document.querySelector('main')?.contains(anchor)
    && !anchor.closest('.linked-references, .transclusion') && !anchor.hasAttribute('download')
    && (!anchor.target || anchor.target === '_self');
  // Gardener opens every external link in a new tab, recording timestamps included,
  // so a plain click on one is claimed whatever its target. Modified clicks still open a tab.
  const click = event => {
    if (!page || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest?.('a[href]');
    if (!anchor || anchor.hasAttribute('download')) return;
    const seconds = chapterTime(anchor.getAttribute('href'), page.source, document.baseURI);
    if (seconds === null) return;
    event.preventDefault();
    session.activate(page, seconds);
  };
  const mediaSeek = event => {
    if (!page || event.defaultPrevented || !event.cancelable || !event.bubbles) return;
    const { anchor, source, seconds } = event.detail || {};
    if (event.target !== anchor || !originalAnchor(anchor) || !Number.isSafeInteger(seconds) || seconds < 0
      || anchor.getAttribute('data-lsg-dialogue-time') !== String(seconds)
      || typeof source !== 'string' || source !== page.source
      || chapterTime(anchor.getAttribute('href'), page.source, document.baseURI) !== seconds) return;
    event.preventDefault();
    session.activate(page, seconds);
  };
  document.addEventListener('click', click);
  document.addEventListener('lsg:media-seek', mediaSeek);
  showPage();
  const manager = { showPage, get audio() { return audio; }, get footer() { return footer; }, dispose({ restoreOriginal = false } = {}) {
    if (disposed) return;
    disposed = true;
    disposeView();
    session?.dispose();
    document.removeEventListener('click', click);
    document.removeEventListener('lsg:media-seek', mediaSeek);
    observer?.disconnect();
    if (restoreOriginal && originalParent && document.querySelector('main')?.contains(originalParent)) {
      originalParent.insertBefore(audio, originalNext?.parentElement === originalParent ? originalNext : null);
      originalOrigin?.classList.remove('episode-recording-origin');
      footer.remove();
      document.body.classList.remove('has-episode-player');
      document.body.style.removeProperty?.('--episode-player-height');
    }
    if (managers.get(document) === manager) managers.delete(document);
  } };
  managers.set(document, manager);
  return manager;
}

export function enhanceEpisode(document) {
  if (managers.has(document) || !readEpisode(document)) return null;
  return createSitePlayer(document);
}
