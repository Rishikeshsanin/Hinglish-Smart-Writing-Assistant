import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../public/index.html', import.meta.url), 'utf8');
const css = readFileSync(new URL('../public/styles.css', import.meta.url), 'utf8');
const js = readFileSync(new URL('../public/app.js', import.meta.url), 'utf8');

test('public landing links to original native Streamlit app', () => {
  assert.match(html, /href="https:\/\/hinglish-smart-writing-assistant-indicwrite-rishi\.streamlit\.app\/"/);
  assert.match(html, /Open IndicWrite converter/);
  assert.match(html, /original pretrained AI4Bharat IndicXlit model/);
});

test('Vercel landing neither calls unverified proxy nor fabricates results', () => {
  assert.doesNotMatch(html, /<textarea\b|id="convert"|<script\b/i);
  assert.doesNotMatch(js, /fetch\s*\(|transliterateWord|\bresult\.textContent\b/);
  assert.match(html, /not a second converter/);
});

test('landing has keyboard, motion and narrow viewport affordances', () => {
  assert.match(html, /class="skip-link" href="#main"/);
  assert.match(html, /aria-label="Open native IndicWrite converter/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /prefers-reduced-motion:reduce/);
  assert.match(css, /max-width:800px/);
  assert.match(css, /max-width:390px/);
  assert.match(html, /name="viewport"/);
});

test('research-only rewriting is not advertised as available', () => {
  assert.match(html, /Manual editing is <strong>not<\/strong> automatic grammar correction/);
  assert.match(html, /Private BharatGen output and research-only features never appear|Optional private BharatGen research is not hosted here/);
});
