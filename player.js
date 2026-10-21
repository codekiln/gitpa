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

export function enhanceEpisode(document) {
  if (document.querySelector('.episode-player')) return null;
  const recordings = document.querySelectorAll('audio');
  if (recordings.length !== 1) return null;
  const audio = recordings[0];
  const source = audio.currentSrc || audio.getAttribute('src') || audio.querySelector('source')?.getAttribute('src');
  if (!source) return null;
  const footer = document.createElement('footer');
  footer.className = 'episode-player';
  footer.setAttribute('aria-label', 'Episode recording');
  const details = document.createElement('div');
  details.className = 'episode-player-details';
  const recording = document.createElement('a');
  recording.href = source;
  recording.textContent = 'Full recording';
  const chapter = document.createElement('span');
  chapter.className = 'episode-player-chapter';
  const status = document.createElement('span');
  status.className = 'episode-player-status';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  details.append(recording, chapter, status);
  audio.closest?.('li')?.classList.add('episode-recording-origin');
  audio.controls = true;
  audio.setAttribute('aria-label', 'Full episode recording');
  footer.append(details, audio);
  document.body.append(footer);
  document.body.classList.add('has-episode-player');
  const player = createPlayer(audio, state => {
    chapter.textContent = state.chapter;
    status.textContent = state.status;
  });
  const click = event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const anchor = event.target.closest?.('a[href]');
    if (!anchor || anchor.hasAttribute('download') || (anchor.target && anchor.target !== '_self')) return;
    const seconds = chapterTime(anchor.getAttribute('href'), source, document.baseURI);
    if (seconds === null) return;
    event.preventDefault();
    const heading = anchor.closest('h1, h2, h3, h4, h5, h6');
    player.seek(seconds, (heading || anchor).textContent.trim());
  };
  document.addEventListener('click', click);
  // Match padding to the actual footer height, including wrapped status text.
  const size = () => document.body.style.setProperty('--episode-player-height', `${footer.getBoundingClientRect().height}px`);
  const Observer = document.defaultView?.ResizeObserver;
  const observer = Observer ? new Observer(size) : null;
  observer?.observe(footer);
  size();
  return { audio, footer, dispose() {
    player.dispose();
    document.removeEventListener('click', click);
    observer?.disconnect();
  } };
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => enhanceEpisode(document), { once: true });
  else enhanceEpisode(document);
}
