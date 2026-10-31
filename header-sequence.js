const SVG = 'http://www.w3.org/2000/svg';
const SIDES = {
  prev: { label: 'Previous', arrow: 'M5 12l14 0M5 12l6 6M5 12l6 -6' },
  next: { label: 'Next', arrow: 'M5 12l14 0M13 18l6 -6M13 6l6 6' },
};

/**
 * Read a page's previous and next pages from its rendered `prev` and `next`
 * page property rows, then from Gardener's `nav.page-sequence` links.
 */
export function sequenceLinks(main) {
  const links = {};
  const add = (key, anchor, title = anchor?.textContent.trim()) => {
    if (Object.hasOwn(SIDES, key) && !links[key] && anchor && title) {
      links[key] = { href: anchor.getAttribute('href'), title };
    }
  };
  const properties = main.querySelector('.page-properties');
  for (const row of properties ? properties.querySelectorAll('.page-property') : []) {
    add(row.querySelector('dt')?.textContent.trim().toLowerCase(), row.querySelector('dd a[href]'));
  }
  const sequence = main.querySelector('nav.page-sequence');
  for (const key of Object.keys(SIDES)) {
    const anchor = sequence?.querySelector(`a[rel~="${key}"][href]`);
    const prefix = `${SIDES[key].label}: `;
    const text = anchor?.textContent.trim() ?? '';
    add(key, anchor, text.startsWith(prefix) ? text.slice(prefix.length) : text);
  }
  return links;
}

function sequenceLink(document, key, { href, title }) {
  const link = document.createElement('a');
  link.className = `gitpa-sequence gitpa-sequence-${key}`;
  link.setAttribute('href', href);
  link.setAttribute('rel', key);
  const icon = document.createElementNS(SVG, 'svg');
  icon.setAttribute('class', 'lsg-icon');
  icon.setAttribute('viewBox', '0 0 24 24');
  icon.setAttribute('aria-hidden', 'true');
  const path = document.createElementNS(SVG, 'path');
  path.setAttribute('d', SIDES[key].arrow);
  icon.append(path);
  const label = document.createElement('span');
  label.className = 'gitpa-sequence-title';
  label.textContent = title;
  if (key === 'prev') link.append(icon, label);
  else link.append(label, icon);
  return link;
}

/** Add the page's previous and next links around the header's spacer; returns the added links. */
export function renderSequence(document, main) {
  const header = document.querySelector('.lsg-header');
  const space = header?.querySelector('.lsg-header-space');
  if (!space) return [];
  for (const stale of header.querySelectorAll('.gitpa-sequence')) stale.remove();
  const { prev, next } = sequenceLinks(main);
  const added = [];
  if (prev) {
    const link = sequenceLink(document, 'prev', prev);
    space.before(link);
    added.push(link);
  }
  if (next) {
    const link = sequenceLink(document, 'next', next);
    space.after(link);
    added.push(link);
  }
  return added;
}

/** Previous and Next links in the header for pages with `prev::` or `next::`. */
export default {
  id: 'header-sequence',
  apiVersion: 1,
  setup(host) {
    let shown = [];
    const remove = links => { for (const link of links) link.remove(); };
    const stop = host.onPageAdopted(({ main, signal }) => {
      remove(shown);
      const links = shown = signal.aborted ? [] : renderSequence(host.document, main);
      signal.addEventListener('abort', () => remove(links), { once: true });
    });
    return () => { stop(); remove(shown); };
  },
};
