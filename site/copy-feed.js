/** The homepage's Copy feed URL button puts the podcast feed address on the clipboard. */
export const FEED_URL = 'https://codekiln.github.io/gitpa/rss.xml';

/** Handle Copy feed URL clicks on `document` until the returned function runs. */
export function installCopyFeed(document) {
  async function copyFeed(event) {
    const button = event.target.closest?.('[data-copy-feed]');
    if (!button) return;
    const status = button.parentElement.querySelector('[data-copy-feed-status]');
    try {
      await document.defaultView.navigator.clipboard.writeText(FEED_URL);
      status.textContent = 'Feed URL copied.';
    } catch {
      status.textContent = 'Copy the podcast RSS feed link instead.';
    }
  }
  document.addEventListener('click', copyFeed);
  return () => document.removeEventListener('click', copyFeed);
}

if (typeof document !== 'undefined') installCopyFeed(document);
