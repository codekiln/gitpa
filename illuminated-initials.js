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
export function artwork(seed) {
  const palette = seed % 2 ? ['#ad594f', '#b78352'] : ['#a24c49', '#c29a55'];
  const spirit = seed % 3 === 0 ? `<path d="M102 97 q-1-10 5-12 q7 2 5 12 l-3-2 -2 3 -2-3z" fill="#f5ecd4" stroke="#577477" stroke-width="1"/><circle cx="105" cy="91" r=".8" fill="#46545d"/><circle cx="109" cy="91" r=".8" fill="#46545d"/>` : `<path d="M103 91q3-7 9 0q-3 7-9 0z" fill="#e7d7a9" stroke="#8a7050"/><circle cx="107.5" cy="91" r="1.4" fill="#566a66"/>`;
  return `<svg viewBox="0 0 130 130" aria-hidden="true" focusable="false"><path d="M37 22 Q57 8 88 19 Q106 35 100 84 Q89 109 53 108 Q30 101 27 71 Q24 40 37 22Z" fill="#f3ead5" stroke="#bd9a60" stroke-width="1.3"/>
  <path d="M35 26 Q55 14 87 23 M35 29 Q60 18 90 26 M34 100 Q65 109 94 95" fill="none" stroke="#d5bd83" stroke-width=".8"/>
  <g fill="none" stroke="#587267" stroke-linecap="round" stroke-width="1.4"><path d="M21 118 C49 103 3 83 20 55 S40 27 28 10"/><path d="M19 115 C5 104 7 91 11 83 M17 76 C8 69 7 59 11 53 M23 51 C34 45 37 37 34 30 M27 28 C18 22 19 15 20 10"/><path d="M90 108 C125 115 114 88 112 68 S116 39 126 25"/><path d="M112 83 C122 80 123 73 124 67 M112 66 C102 62 101 55 102 49 M116 44 C126 40 126 34 124 31"/></g>
  <g fill="#78917e" stroke="#557364" stroke-width=".7"><path d="M18 104 Q2 101 6 92 Q17 91 18 104ZM17 90 Q27 78 31 88 Q29 96 17 94ZM17 68 Q4 67 7 58 Q17 57 17 68ZM24 54 Q36 42 39 50 Q37 58 24 57ZM27 35 Q17 27 16 22 Q26 22 28 33ZM113 90 Q125 83 127 90 Q124 98 113 94ZM112 73 Q100 69 102 61 Q112 61 114 72ZM115 53 Q126 47 128 54 Q123 61 114 57Z"/></g>
  <g fill="${palette[0]}" stroke="#8e6055" stroke-width=".75"><path d="M14 52 C3 43 11 37 15 43 C21 36 27 44 18 52 L16 55Z"/><path d="M35 26 C26 18 32 12 36 17 C41 10 48 18 40 26 L37 28Z"/><path d="M125 67 C116 59 122 54 126 59 C131 54 136 60 128 67 L126 69Z"/></g>
  <g fill="${palette[1]}"><circle cx="15.8" cy="46.5" r="1.9"/><circle cx="37" cy="20.5" r="1.9"/><circle cx="126" cy="62" r="1.9"/><circle cx="48" cy="19" r="1.4"/><circle cx="88" cy="104" r="1.4"/></g>
  <g fill="none" stroke="#987c53" stroke-width=".9"><path d="M44 17l2-4 2 4 M92 96l2-4 2 4"/><path d="M14 113q6-3 9 1M9 117q8-2 12 2M103 16q7 1 10 7M103 12q11 1 15 10"/></g>${spirit}</svg>`;
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
