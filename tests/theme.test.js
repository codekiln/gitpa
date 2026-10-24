const test = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const css = readFileSync(path.join(__dirname, '../site/theme.css'), 'utf8');
const luminance = hex => {
  const rgb = hex.match(/[a-f0-9]{2}/g).map(v => parseInt(v, 16) / 255)
    .map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
};
const contrast = (a, b) => (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
test('Nord light and dark text, links and player controls remain readable on their surfaces', () => {
  const palettes = [...css.matchAll(/--lsg-text:\s*#[^}]+/g)];
  assert.equal(palettes.length, 3);
  for (const [declarations] of palettes) {
    const values = Object.fromEntries([...declarations.matchAll(/--([a-z-]+):\s*#([a-f0-9]{6})(?=;|\s)/g)].map(m => [m[1], luminance(m[2])]));
    for (const surface of ['lsg-background', 'lsg-surface']) {
      for (const text of ['lsg-text', 'lsg-link']) assert.ok(contrast(values[text], values[surface]) >= 4.5, `${text} on ${surface}`);
      assert.ok(contrast(values['lsg-focus'], values[surface]) >= 3);
    }
    assert.ok(contrast(values['gitpa-heading'], values['lsg-background']) >= 3);
    assert.ok(contrast(values['gitpa-code-text'], values['gitpa-button-background']) >= 4.5);
  }
});
