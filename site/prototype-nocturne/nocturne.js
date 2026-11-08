// PROTOTYPE: a moonlit manuscript garden for GitP episode initials.
// Run preview.py against a built site; the production site does not load this.
const svgNS = 'http://www.w3.org/2000/svg';
function hash(text) {
  let h = 2166136261;
  for (const c of text) h = Math.imul(h ^ c.codePointAt(0), 16777619);
  return h >>> 0;
}
function image(seed) {
  const stars = Array.from({ length: 11 }, (_, i) => {
    const x = 20 + ((seed >>> (i % 16)) + 17 * i) % 62;
    const y = 12 + ((seed >>> ((i + 4) % 16)) + 29 * i) % 69;
    const r = i % 4 === 0 ? 1.1 : .55;
    return `<circle cx="${x}" cy="${y}" r="${r}"/>`;
  }).join('');
  const flower = seed % 2 ? '#b8736b' : '#b79864';
  const spirit = seed % 2
    ? '<path d="M76 77c-1-10 1-17 5-17s6 7 5 17l-2-2-2 3-2-3-2 2z"/><circle cx="79.5" cy="66" r=".6"/><circle cx="83" cy="66" r=".6"/>'
    : '<path d="M15 77c-2-9 0-16 5-17 5 1 7 8 5 17l-3-2-2 3-2-3z"/><circle cx="18.5" cy="66" r=".6"/><circle cx="22" cy="66" r=".6"/>';
  // Layered imperfect strokes, ink stippling, and off-center forms suggest a
  // printed page worked over by hand instead of a polished geometric icon.
  return `<svg xmlns="${svgNS}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
    <path fill="#d5bd80" stroke="#5a4c3e" stroke-width="1.3" d="M3 4L96 3 97 96 4 97Z"/>
    <path fill="#29394c" stroke="#f4dfaa" stroke-width="1" d="M8 9L91 8 92 91 9 92Z"/>
    <path fill="none" stroke="#ad9362" stroke-width=".55" d="M11 12L88 11 89 88 12 89Z M5 6L94 6 94 94 6 94Z"/>
    <path fill="#d5bd80" opacity=".95" d="M62 24a11 11 0 1 0 12-12 9 9 0 1 1-12 12Z"/>
    <g fill="#e9d4a0" opacity=".9">${stars}</g>
    <g fill="none" stroke="#9bb2a3" stroke-width="1.1" stroke-linecap="round">
      <path d="M12 89C29 77 9 59 19 41S15 20 12 15 M88 90C72 74 94 58 80 37S86 18 88 13"/>
      <path d="M10 86c15-9 7-21 8-29 M91 86C78 77 83 62 81 51" stroke="#d2bf89" stroke-width=".45"/>
    </g>
    <g fill="#789484" stroke="#b1c0a5" stroke-width=".45">
      <path d="M16 76Q5 72 9 64q9 1 8 10ZM18 62Q22 52 29 55q-1 8-11 9ZM17 48Q6 44 11 37q9 1 7 10ZM17 31Q20 22 26 23q1 8-9 10ZM84 75q11-4 7-12-9 1-8 10ZM82 60q-4-10-11-7 1 8 11 9ZM82 44q11-4 6-11-9 1-7 10ZM83 27q-3-9-9-8-1 8 9 10Z"/>
    </g>
    <g fill="${flower}" stroke="#dec698" stroke-width=".5"><path d="M15 22q-5-3-2-6 3-2 5 3 4-3 6 0 1 4-5 4-1 5-4 3-2-1 0-4ZM79 79q-5-3-2-6 3-2 5 3 4-3 6 0 1 4-5 4-1 5-4 3-2-1 0-4Z"/></g>
    <g fill="#f1e7ce" stroke="#344a53" stroke-width=".65">${spirit}</g>
    <g fill="#d5bd80"><path d="M3 3h12L3 15ZM97 3H85l12 12ZM3 97h12L3 85ZM97 97H85l12-12Z"/><circle cx="50" cy="5.5" r="1.2"/><circle cx="50" cy="94.5" r="1.2"/></g>
  </svg>`;
}
function paint() {
  document.querySelectorAll('.illuminated-initial:not([data-prototype-nocturne])').forEach((initial, index) => {
    const previous = initial.querySelector('svg');
    if (!previous) return;
    const template = document.createElement('template');
    template.innerHTML = image(hash(location.pathname + ':' + index));
    previous.replaceWith(template.content.firstElementChild);
    initial.dataset.prototypeNocturne = '';
  });
}
document.documentElement.classList.add('prototype-nocturne');
new MutationObserver(paint).observe(document.documentElement, { childList: true, subtree: true });
paint();
