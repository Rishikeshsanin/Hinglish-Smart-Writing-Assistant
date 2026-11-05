import test from "node:test";
import assert from "node:assert/strict";
import handler from "../api/transliterate.js";

const NATIVE = "https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/";
function response() {
  return {
    code: 0, headers: {}, data: null,
    setHeader(name, value) { this.headers[name] = value; return this; },
    status(code) { this.code = code; return this; },
    json(value) { this.data = value; return this; }
  };
}

test("legacy API never forwards requests or generates synthetic Hindi", () => {
  const orig = globalThis.fetch;
  let calls = 0;
  globalThis.fetch = async () => { calls++; throw Error("forbidden"); };
  try {
    for (const req of [
      {method: "GET", query: {word: "namaste"}},
      {method: "POST", query: {word: "hi"}},
      {method: "OPTIONS", query: {}}
    ]) {
      const res = response();
      handler(req, res);
      assert.equal(res.code, 410);
      assert.equal(res.data.canonical_url, NATIVE);
      assert.equal(res.data.result, undefined);
      assert.equal(res.headers["Cache-Control"], "no-store");
      assert.equal(res.headers["X-Content-Type-Options"], "nosniff");
      assert.equal(res.headers["Access-Control-Allow-Origin"], undefined);
      assert.equal(res.headers.Deprecation, "true");
    }
    assert.equal(calls, 0, "Retired proxy should never call hosted API");
  } finally {
    globalThis.fetch = orig;
  }
});
