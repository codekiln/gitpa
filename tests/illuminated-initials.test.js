const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const source = readFileSync(join(__dirname, '../site/illuminated-initials.js'), 'utf8');
const moduleURL = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;

// Minimal text nodes let us exercise the plugin's placement and restoration
// without coupling the test to the particular illustrated paths.
function fixture() {
  let listener, episode = true;
  const elements = [];
  const document = {
    querySelector: () => episode ? {} : null,
    createElement() {
      const element = { className: '', innerHTML: '', children: [],
        append(child) { this.children.push(child); },
        querySelector() { return this.children[0]; },
        replaceWith(text) { this.restored = text; this.removed = true; } };
      elements.push(element);
      return element;
    },
    createTreeWalker(container, _, filter) {
      let index = 0;
      return { nextNode() { while (index < container.nodes.length) {
        const node = container.nodes[index++]; if (filter.acceptNode(node) === 1) return node;
      } return null; } };
    },
  };
  function text(data, link = null) {
    const inserted = [];
    const parentNode = { insertBefore(node) { inserted.push(node); } };
    const node = { data, inserted, parentNode,
      parentElement: { closest(selector) { return selector === 'a' ? link : null; } },
      splitText(index) {
        const suffix = { data: this.data.slice(index), parentNode,
          deleteData(start, count) { this.data = this.data.slice(0, start) + this.data.slice(start + count); } };
        this.data = this.data.slice(0, index);
        this.suffix = suffix;
        return suffix;
      } };
    return node;
  }
  const annotation = text('A single sound');
  const timestamp = text('00:00', { textContent: '00:00' });
  const chapter = text(' enter the garden');
  const annotationTarget = { ownerDocument: document, nodes: [annotation] };
  const chapterTarget = { ownerDocument: document, nodes: [timestamp, chapter] };
  const heading = (name, target) => ({ textContent: name, parentElement: { querySelector: () => target } });
  const main = { querySelectorAll: () => [heading('Ceremonial Annotations', annotationTarget), heading('Chapters', chapterTarget)] };
  const host = { document, onPageAdopted(fn) { listener = fn; return () => { listener = null; }; } };
  return { host, main, annotation, timestamp, chapter, elements, adopt(page = 'episode') { listener?.({ main, page: { id: page } }); },
    setEpisode(value) { episode = value; }, get listener() { return listener; } };
}

test('episode adoption illuminates the annotation and chapter title, then restores text', async () => {
  const { default: plugin } = await import(moduleURL);
  const f = fixture(), dispose = plugin.setup(f.host);
  f.adopt();
  assert.equal(f.elements.length, 4); // Two frames and their text spans.
  assert.equal(f.annotation.inserted[0].children[0].textContent, 'A');
  assert.equal(f.chapter.inserted[0].children[0].textContent, 'e');
  assert.equal(f.timestamp.inserted.length, 0);
  assert.equal(f.chapter.suffix.data, 'nter the garden');
  assert.match(f.annotation.inserted[0].innerHTML, /aria-hidden="true"/);
  f.setEpisode(false);
  f.adopt('ordinary-page');
  assert.equal(f.annotation.inserted[0].restored, 'A');
  assert.equal(f.chapter.inserted[0].restored, 'e');
  assert.equal(f.elements.length, 4);
  dispose();
  assert.equal(f.listener, null);
});

test('episode-seeded illustrations are stable and vary in their details', async () => {
  const { artwork } = await import(moduleURL);
  assert.equal(artwork(6), artwork(6));
  assert.notEqual(artwork(6), artwork(7));
  assert.match(artwork(6), /<svg[^>]*aria-hidden="true"/);
});
