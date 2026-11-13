const { test, before } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const url = source => `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const site = name => readFileSync(join(__dirname, '../site', name), 'utf8');
let headerSequence, sequenceLinks;
before(async () => {
  ({ default: headerSequence, sequenceLinks } = await import(url(site('header-sequence.js'))));
});

/**
 * The part of lsg's plugin host this plugin uses: it adopts the current page when the plugin
 * starts and again on `adopt()`, aborting the previous page's signal first.
 */
function startPlugin(document) {
  let listener = null, controller = null;
  const adopt = () => {
    controller?.abort();
    controller = new AbortController();
    listener?.({ main: document.querySelector('main'), signal: controller.signal });
  };
  const cleanup = headerSequence.setup({
    apiVersion: 1, document,
    onPageAdopted(fn) { listener = fn; adopt(); return () => { listener = null; }; },
  });
  return { adopt, dispose() { controller?.abort(); cleanup(); } };
}

/** Just enough DOM for the header, page properties and Gardener's sequence nav. */
class Element {
  constructor(tagName, attributes = {}, children = [], namespaceURI = 'http://www.w3.org/1999/xhtml') {
    this.tagName = tagName.toLowerCase(); this.namespaceURI = namespaceURI;
    this.attributes = new Map(Object.entries(attributes)); this.childNodes = []; this.parentNode = null;
    this.append(...children);
  }
  get textContent() { return this.childNodes.map(node => typeof node === 'string' ? node : node.textContent).join(''); }
  set textContent(text) { for (const node of this.childNodes) if (typeof node !== 'string') node.parentNode = null; this.childNodes = [String(text)]; }
  set className(value) { this.setAttribute('class', value); }
  get children() { return this.childNodes.filter(node => typeof node !== 'string'); }
  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  getAttribute(name) { return this.attributes.has(name) ? this.attributes.get(name) : null; }
  hasAttribute(name) { return this.attributes.has(name); }
  append(...nodes) { for (const node of nodes) this.insert(node, this.childNodes.length); }
  insert(node, index) {
    if (typeof node !== 'string') { node.remove(); node.parentNode = this; }
    this.childNodes.splice(index, 0, node);
  }
  before(node) { this.parentNode.insert(node, this.parentNode.childNodes.indexOf(this)); }
  after(node) { this.parentNode.insert(node, this.parentNode.childNodes.indexOf(this) + 1); }
  remove() {
    if (!this.parentNode) return;
    this.parentNode.childNodes.splice(this.parentNode.childNodes.indexOf(this), 1);
    this.parentNode = null;
  }
  replaceWith(node) { this.before(node); this.remove(); }
  matches(selector) {
    const parts = selector.trim().split(/\s+/).map(compound);
    if (!parts.at(-1)(this)) return false;
    let ancestor = this.parentNode;
    for (let index = parts.length - 2; index >= 0; index--) {
      while (ancestor && !parts[index](ancestor)) ancestor = ancestor.parentNode;
      if (!ancestor) return false;
      ancestor = ancestor.parentNode;
    }
    return true;
  }
  querySelectorAll(selector) {
    const found = [];
    const walk = element => { for (const child of element.children) { if (child.matches(selector)) found.push(child); walk(child); } };
    walk(this);
    return found;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}
function compound(text) {
  const tag = text.match(/^[a-z][a-z0-9]*/i)?.[0].toLowerCase();
  const classes = [...text.replace(/\[[^\]]*\]/g, '').matchAll(/\.([\w-]+)/g)].map(match => match[1]);
  const attributes = [...text.matchAll(/\[([\w-]+)(?:(~?=)"([^"]*)")?\]/g)];
  return element => (!tag || element.tagName === tag) &&
    classes.every(name => (element.getAttribute('class') || '').split(/\s+/).includes(name)) &&
    attributes.every(([, name, operator, value]) => {
      const actual = element.getAttribute(name);
      if (actual === null) return false;
      if (operator === '=') return actual === value;
      if (operator === '~=') return actual.split(/\s+/).includes(value);
      return true;
    });
}
const h = (tag, attributes, ...children) => new Element(tag, attributes, children);

function header() {
  return h('header', { class: 'lsg-header' },
    h('button', { class: 'lsg-button', 'data-lsg-left-toggle': '' }),
    h('span', { class: 'lsg-header-space' }),
    h('a', { class: 'lsg-button', href: '/gitpa/', 'aria-label': 'Home' }),
    h('button', { class: 'lsg-button lsg-right-toggle', 'data-lsg-right-toggle': '' }));
}
const row = (key, title) => h('div', { class: 'page-property' },
  h('dt', {}, key), h('dd', {}, h('a', { href: `/gitpa/${title}/` }, title)));
/** A rendered page: `properties` become page property rows, `sequence` Gardener's nav links. */
function page(title, { properties = {}, sequence = {} } = {}) {
  const rows = Object.entries(properties).map(([key, value]) => row(key, value));
  const links = Object.entries(sequence).map(([key, value]) =>
    h('a', { rel: key, href: `/gitpa/${value}/` }, `${key === 'prev' ? 'Previous' : 'Next'}: ${value}`));
  return h('main', {}, h('h1', {}, title),
    ...(rows.length ? [h('section', { class: 'page-properties' }, h('details', {}, h('summary', {}, 'Properties'), h('dl', {}, ...rows)))] : []),
    h('ul', { class: 'outline' }, h('li', {}, 'Notes with a ', h('a', { href: '/gitpa/Other/' }, 'link'))),
    ...(links.length ? [h('nav', { class: 'page-sequence' }, ...links)] : []));
}
function siteDocument(main) {
  const root = h('html', {}, h('head'), h('body', {}, header(), main));
  return {
    root, title: main.querySelector('h1').textContent, URL: 'https://example.com/gitpa/Page/',
    querySelector: selector => root.querySelector(selector),
    querySelectorAll: selector => root.querySelectorAll(selector),
    createElement: tag => new Element(tag),
    createElementNS: (namespace, tag) => new Element(tag, {}, [], namespace),
  };
}
/** The header as a reader sees it: each item's role in order. */
function headerItems(document) {
  return document.querySelector('.lsg-header').children.map(element => {
    if (element.matches('.gitpa-sequence')) return `${element.getAttribute('rel')} ${element.getAttribute('href')}`;
    if (element.matches('.lsg-header-space')) return 'space';
    return element.getAttribute('aria-label') || element.tagName;
  });
}
function navigate(document, main) {
  document.querySelector('main').replaceWith(main);
  document.title = main.querySelector('h1').textContent;
}

test('a two-sided sequence puts Previous left of the spacer and Next right of it', () => {
  const document = siteDocument(page('B', { properties: { tags: 'Episode', prev: 'A', next: 'C' } }));
  const plugin = startPlugin(document);
  assert.deepEqual(headerItems(document), ['button', 'prev /gitpa/A/', 'space', 'next /gitpa/C/', 'Home', 'button']);
  const [previous, next] = document.querySelector('.lsg-header').querySelectorAll('.gitpa-sequence');
  assert.equal(previous.textContent, 'A');
  assert.equal(next.textContent, 'C');
  for (const link of [previous, next]) assert.equal(link.hasAttribute('aria-label') || link.hasAttribute('title'), false, 'the title text is the name');
  assert.deepEqual(previous.children.map(child => child.tagName), ['svg', 'span'], 'left arrow before the title');
  assert.deepEqual(next.children.map(child => child.tagName), ['span', 'svg'], 'right arrow after the title');
  for (const link of [previous, next]) {
    const icon = link.querySelector('svg');
    assert.equal(icon.getAttribute('aria-hidden'), 'true');
    assert.equal(icon.namespaceURI, 'http://www.w3.org/2000/svg');
    assert.equal(link.querySelector('.gitpa-sequence-title').textContent, link.textContent);
  }
  assert.equal(document.querySelector('main').querySelectorAll('.page-property').length, 3, 'property rows stay');
  plugin.dispose();
  assert.deepEqual(headerItems(document), ['button', 'space', 'Home', 'button']);
});

test('a one-sided sequence shows only the side it has', () => {
  const document = siteDocument(page('GitP/A/Session/26/10/26-Mon', { properties: { prev: 'GitP/A/Session/26/10/24-Sat' } }));
  const plugin = startPlugin(document);
  assert.deepEqual(headerItems(document), ['button', 'prev /gitpa/GitP/A/Session/26/10/24-Sat/', 'space', 'Home', 'button']);
  plugin.dispose();
});

test('a page without a sequence leaves the header as rendered', () => {
  const document = siteDocument(page('Plain', { properties: { tags: 'Preset' } }));
  const plugin = startPlugin(document);
  assert.deepEqual(headerItems(document), ['button', 'space', 'Home', 'button']);
  assert.deepEqual(sequenceLinks(page('Bare')), {});
  assert.deepEqual(sequenceLinks(page('Odd', { properties: { toString: 'A', constructor: 'B' } })), {});
  plugin.dispose();
});

test("Gardener's page-sequence nav supplies a side the property rows lack", () => {
  assert.deepEqual(sequenceLinks(page('B', { sequence: { prev: 'A', next: 'C' } })), {
    prev: { href: '/gitpa/A/', title: 'A' }, next: { href: '/gitpa/C/', title: 'C' },
  });
  assert.deepEqual(sequenceLinks(page('B', { properties: { prev: 'A' }, sequence: { prev: 'Z', next: 'C' } })), {
    prev: { href: '/gitpa/A/', title: 'A' }, next: { href: '/gitpa/C/', title: 'C' },
  });
});

test('in-site navigation renders the new page and clears the old one', () => {
  const document = siteDocument(page('B', { properties: { prev: 'A', next: 'C' } }));
  const installation = startPlugin(document);
  assert.deepEqual(headerItems(document), ['button', 'prev /gitpa/A/', 'space', 'next /gitpa/C/', 'Home', 'button']);

  navigate(document, page('C', { properties: { prev: 'B' } }));
  installation.adopt();
  assert.deepEqual(headerItems(document), ['button', 'prev /gitpa/B/', 'space', 'Home', 'button']);

  navigate(document, page('Plain'));
  installation.adopt();
  assert.deepEqual(headerItems(document), ['button', 'space', 'Home', 'button']);

  // The navigator may replace the whole header with the fetched page's header.
  navigate(document, page('D', { sequence: { next: 'E' } }));
  const old = document.querySelector('.lsg-header');
  old.replaceWith(header());
  installation.adopt();
  assert.deepEqual(headerItems(document), ['button', 'space', 'next /gitpa/E/', 'Home', 'button']);
  assert.equal(old.querySelectorAll('.gitpa-sequence').length, 0);

  installation.dispose();
  assert.deepEqual(headerItems(document), ['button', 'space', 'Home', 'button']);
});
