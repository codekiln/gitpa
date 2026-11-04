const { test } = require('node:test');
const { execFileSync } = require('node:child_process');
const { join, resolve } = require('node:path');
const root = resolve(__dirname, '..');

test('the proposed plugin contract type-checks, including its negative examples', () => {
  execFileSync(process.execPath, [join(root, 'node_modules/typescript/bin/tsc'), '-p', 'contracts/tsconfig.json'],
    { cwd: root, stdio: 'inherit' });
});
