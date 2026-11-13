const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const source = readFileSync(join(__dirname, '../site/copy-feed.js'), 'utf8');
const moduleURL = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;

test('copy feed button reports success and clipboard failures, and stops on removal', async () => {
  const { installCopyFeed } = await import(moduleURL);
  const document = new EventTarget(), status = { textContent: '' };
  let copied;
  document.closest = selector => selector === '[data-copy-feed]' ? document : null;
  document.parentElement = { querySelector: () => status };
  document.defaultView = { navigator: { clipboard: { async writeText(value) { copied = value; } } } };
  const remove = installCopyFeed(document);
  document.dispatchEvent(new Event('click'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(copied, 'https://codekiln.github.io/gitpa/rss.xml');
  assert.equal(status.textContent, 'Feed URL copied.');
  document.defaultView.navigator.clipboard.writeText = async () => { throw new Error('denied'); };
  document.dispatchEvent(new Event('click'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(status.textContent, 'Copy the podcast RSS feed link instead.');
  remove();
  status.textContent = '';
  document.dispatchEvent(new Event('click'));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(status.textContent, '');
});
