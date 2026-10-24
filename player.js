import { createNavigator } from './navigation.js';

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

/** Playback context survives page changes; changing context is always explicit. */
export function createEpisodeSession(audio, update = () => {}) {
  let context = null;
  let origin = null;
  let controller = null;
  let playback = { status: 'Paused' };
  const publish = () => {
    if (!context) return;
    update({ context, origin, current: currentChapter(context.chapters, audio.currentTime), ...playback });
  };
  const nativePlay = () => {
    if (!origin && context) origin = { href: context.startHref || `${context.url}#episode-start`, label: context.title };
    publish();
  };
  for (const name of ['timeupdate', 'seeked', 'loadedmetadata']) audio.addEventListener(name, publish);
  audio.addEventListener('play', nativePlay);
  const adopt = (next, replace) => {
    if (context?.source === next.source) return;
    controller?.dispose();
    if (replace) {
      audio.pause();
      audio.setAttribute('src', next.source);
      audio.load();
    }
    context = next;
    origin = null;
    controller = createPlayer(audio, state => { playback = state; publish(); });
    publish();
  };
  return {
    adopt(next) { if (!context) adopt(next, false); },
    activate(next, seconds = 0, start = null) {
      adopt(next, context !== null);
      origin = start || { href: next.startHref || `${next.url}#episode-start`, label: next.title };
      controller.seek(seconds, next.title);
      publish();
    },
    refresh: publish,
    get context() { return context; },
    dispose() {
      controller?.dispose();
      for (const name of ['timeupdate', 'seeked', 'loadedmetadata']) audio.removeEventListener(name, publish);
      audio.removeEventListener('play', nativePlay);
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
  const used = new Map();
  for (const heading of main.querySelectorAll('h1, h2, h3, h4, h5, h6')) {
    if (heading.closest('.linked-references')) continue;
    for (const anchor of heading.querySelectorAll('a[href]')) {
      const seconds = chapterTime(anchor.getAttribute('href'), source, document.baseURI);
      if (seconds === null) continue;
      const count = (used.get(seconds) || 0) + 1;
      used.set(seconds, count);
      if (!heading.id) heading.id = `chapter-${seconds}${count > 1 ? `-${count}` : ''}`;
      chapters.push({ seconds, label: heading.textContent.trim(), id: heading.id,
        href: `${url.href}#${encodeURIComponent(heading.id)}` });
      break;
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
  let disposeView = () => {};
  const makeFooter = initial => {
    audio = initial.audio;
    footer = document.createElement('footer');
    footer.className = 'episode-player';
    footer.setAttribute('aria-label', 'Episode recording');
    const details = document.createElement('div');
    details.className = 'episode-player-details';
    const recording = document.createElement('a');
    recording.textContent = 'Full recording';
    const origin = document.createElement('a');
    origin.className = 'episode-player-origin';
    origin.textContent = 'Return to start';
    const chapter = document.createElement('a');
    chapter.className = 'episode-player-chapter';
    const status = document.createElement('span');
    status.className = 'episode-player-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    details.append(recording, origin, chapter, status);
    audio.closest('li')?.classList.add('episode-recording-origin');
    audio.controls = true;
    audio.setAttribute('aria-label', 'Full episode recording');
    footer.append(details, audio);
    document.body.append(footer);
    document.body.classList.add('has-episode-player');
    session = createEpisodeSession(audio, state => {
      recording.href = state.context.source;
      origin.href = state.origin?.href || state.context.startHref || `${state.context.url}#episode-start`;
      chapter.href = state.current?.href || state.context.startHref || `${state.context.url}#episode-start`;
      chapter.textContent = state.current?.label || state.context.title;
      status.textContent = state.status;
      const currentPage = document.querySelector('link[rel="canonical"]')?.getAttribute('href');
      const here = new URL(currentPage || document.baseURI, document.baseURI).href.split('#')[0];
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
    disposeView();
    disposeView = () => {};
    page = readEpisode(document);
    if (!page) { session?.refresh(); return; }
    if (!audio) { makeFooter(page); return; }
    const candidate = page.audio;
    if (candidate !== audio) {
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
  const click = event => {
    if (!page || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest?.('a[href]');
    if (!anchor || anchor.hasAttribute('download') || (anchor.target && anchor.target !== '_self')) return;
    const seconds = chapterTime(anchor.getAttribute('href'), page.source, document.baseURI);
    if (seconds === null) return;
    const heading = anchor.closest('h1, h2, h3, h4, h5, h6');
    const chapter = page.chapters.find(item => item.id === heading?.id);
    event.preventDefault();
    session.activate(page, seconds, chapter && { href: chapter.href, label: chapter.label });
  };
  document.addEventListener('click', click);
  showPage();
  const manager = { showPage, get audio() { return audio; }, get footer() { return footer; }, dispose() {
    disposeView();
    session?.dispose();
    document.removeEventListener('click', click);
    observer?.disconnect();
    managers.delete(document);
  } };
  managers.set(document, manager);
  return manager;
}

export function enhanceEpisode(document) {
  if (managers.has(document) || !readEpisode(document)) return null;
  return createSitePlayer(document);
}

if (typeof document !== 'undefined') {
  const start = () => {
    const player = createSitePlayer(document);
    createNavigator({ document, window: document.defaultView, onPage: player.showPage });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
}
