export const manifest = {
  "id": "illuminated-initials",
  "apiVersion": 1,
  "version": "1.0.0",
  "module": "illuminated-initials.js",
  "styles": ["illuminated-initials.css"],
  "activation": "after-load",
  "pageProperties": []
};

// A small ink garden is drawn anew in the browser. The page title seeds its
// composition so returning to an episode brings back the same illumination.
function seedFor(value) {
  let seed = 2166136261;
  for (const char of value) seed = Math.imul(seed ^ char.codePointAt(0), 16777619);
  return seed >>> 0;
}
function artwork(seed) {
  const flowers = seed % 2
    ? '<circle cx="16" cy="23" r="3"/><circle cx="83" cy="75" r="3"/><circle cx="77" cy="18" r="2"/>'
    : '<path d="M13 25q-5-5 0-8 5 3 0 8Zm72 42q-6-5 0-9 6 4 0 9ZM74 16q-4-4 0-7 4 3 0 7Z"/>';
  const spirit = seed % 3 === 0
    ? '<path d="M76 82q-2-9 4-11 6 2 4 11l-2-2-2 3-2-3Z" fill="#efe4c8"/><circle cx="78.5" cy="76" r=".7" fill="#303f50" stroke="none"/><circle cx="81.5" cy="76" r=".7" fill="#303f50" stroke="none"/>' : '';
  return `<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"><rect x="3" y="3" width="94" height="94" rx="2" fill="#eee3ca" stroke="#334d5b" stroke-width="2"/><rect x="7" y="7" width="86" height="86" fill="#d9e4de" stroke="#a16a49" stroke-width=".8"/><path d="M10 89C32 73 16 50 11 35M90 11C68 27 85 50 90 65M12 12C29 24 25 30 20 38M88 88C70 76 75 68 80 61" fill="none" stroke="#526d61" stroke-width="1.5"/><g fill="#698377" stroke="#435e56" stroke-width=".8"><path d="M14 73q-10-2-7-10 8 0 10 8M16 57q-2-11 7-12 3 8-6 13M13 40q-9-3-6-9 7 0 8 8M85 27q10 2 7 10-8 0-10-8M84 43q2 11-7 12-3-8 6-13M87 60q9 3 6 9-7 0-8-8"/></g><g fill="#b77663" stroke="#794f4c" stroke-width=".7">${flowers}</g><g fill="#c2a35d"><circle cx="25" cy="14" r="1.5"/><circle cx="68" cy="87" r="1.5"/><circle cx="89" cy="48" r="1"/><circle cx="11" cy="50" r="1"/></g><g stroke="#435e56" stroke-width=".8">${spirit}</g></svg>`;
}

function illuminate(container, seed, chapter = false) {
  const document = container.ownerDocument;
  const walker = document.createTreeWalker(container, 4, {
    acceptNode(node) {
      if (node.parentElement.closest('button, svg, .illuminated-initial')) return 2;
      const link = node.parentElement.closest('a');
      if (link && /^\d/.test(link.textContent.trim())) return 2;
      return /\p{L}/u.test(node.data) ? 1 : 2;
    }
  });
  let node;
  while ((node = walker.nextNode())) {
    const match = /\p{L}/u.exec(node.data);
    if (!match) continue;
    const initial = document.createElement('span');
    initial.className = 'illuminated-initial' + (chapter ? ' illuminated-initial--chapter' : '');
    initial.innerHTML = artwork(seed);
    const letter = document.createElement('span');
    letter.className = 'illuminated-initial__letter';
    letter.textContent = match[0];
    initial.append(letter);
    const suffix = node.splitText(match.index);
    suffix.deleteData(0, match[0].length);
    suffix.parentNode.insertBefore(initial, suffix);
    return initial;
  }
}

export default {
  ...manifest,
  setup(host) {
    let initials = [];
    const clear = () => {
      for (const initial of initials) initial.replaceWith(initial.querySelector('.illuminated-initial__letter').textContent);
      initials = [];
    };
    const unsubscribe = host.onPageAdopted(({ main, page }) => {
      clear();
      if (!main || !host.document.querySelector('meta[name="gitpa-episode"]')) return;
      const headings = [...main.querySelectorAll('h2')];
      const annotations = headings.find(h => h.textContent.trim().toLowerCase() === 'ceremonial annotations');
      const chapters = headings.find(h => h.textContent.trim().toLowerCase() === 'chapters');
      const annotationText = annotations?.parentElement.querySelector(':scope > ul > li');
      const chapter = chapters?.parentElement.querySelector(':scope > ul > li > h3');
      const seed = seedFor(page.id);
      for (const [target, salt, isChapter] of [[annotationText, 0, false], [chapter, 1, true]]) {
        if (target) {
          const initial = illuminate(target, seed + salt, isChapter);
          if (initial) initials.push(initial);
        }
      }
    });
    return () => { unsubscribe(); clear(); };
  }
};
