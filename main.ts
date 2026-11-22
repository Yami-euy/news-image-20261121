// main.ts — "The World in One Page" v4, Saturday 21 November 2026.
// Entry for news-image-20261121: one newspaper front page of the day's
// world news, drawn by render.py into entry.png next to this file.
//
// This program only moves that picture into the grader's output
// directory, byte for byte, so the judge sees exactly what the
// renderer produced. Nothing is re-encoded or resized here.
//
// Node 22, standard library only. The grader runs it twice and both
// runs must write identical bytes; a plain read + write guarantees it.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FOLDER = dirname(fileURLToPath(import.meta.url));
const PICTURE = join(FOLDER, "entry.png");
const DEST_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const DEST = join(DEST_DIR, "entry.png");
const LIMIT = 1048576; // 1 MiB, the competition's file cap

function abort(why: string): never {
  throw new Error(`main.ts: ${why}`);
}

if (!existsSync(PICTURE)) abort(`no entry.png beside main.ts (${PICTURE})`);
const bytes = readFileSync(PICTURE);
if (bytes.length === 0) abort("entry.png is empty");
if (bytes.length > LIMIT) abort(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);

mkdirSync(DEST_DIR, { recursive: true });
writeFileSync(DEST, bytes);

// Check the copy instead of trusting it: the judge sees exactly
// these bytes, so read the copy back and compare with the source.
const check = readFileSync(DEST);
if (!check.equals(bytes)) abort("copied entry.png differs from the source");
console.log(`entry.png: ${check.length} bytes -> ${DEST}`);
