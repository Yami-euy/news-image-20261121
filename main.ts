// main.ts — "The World in One Page", 21 November 2026 (news-image-20261121).
//
// The entry is a single picture of the day's world news, drawn by
// render.py into entry.png beside this file. This program's only job is
// to carry that picture into the grader's output directory, unchanged,
// so the judge sees exactly the bytes the renderer produced.
//
// Node 22, standard library only. It runs twice in the grader and both
// runs must write the same bytes; a plain file copy guarantees that.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, 'entry.png');
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const TARGET = join(OUT_DIR, 'entry.png');

function fail(message: string): never {
  throw new Error(`main.ts: ${message}`);
}

if (!existsSync(SOURCE)) fail(`entry.png is missing next to main.ts (${SOURCE})`);
const size = statSync(SOURCE).size;
if (size === 0) fail('entry.png is empty');
if (size > 1048576) fail(`entry.png is ${size} bytes, over the 1 MiB cap`);

mkdirSync(OUT_DIR, { recursive: true });
copyFileSync(SOURCE, TARGET);

// The copy must be byte-for-byte the source: the judge sees exactly
// these bytes, so prove it instead of trusting the copy call.
const before = readFileSync(SOURCE);
const after = readFileSync(TARGET);
if (!before.equals(after)) fail('copied entry.png differs from the source');
console.log(`entry.png: ${after.length} bytes -> ${TARGET}`);
