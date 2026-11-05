// Retired legacy proxy: the public Vercel experience is a gateway only.
// The upstream hosted word-level API was unreliable and unverified for
// release. Do not expose a wildcard-CORS/open relay or pretend this route
// is backed by the canonical local-checkpoint Streamlit engine.
const CANONICAL = "https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/";

export default function handler(_req, res) {
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("Deprecation", "true");
  res.setHeader("Link", `<${CANONICAL}>; rel="alternate"`);
  return res.status(410).json({
    error: "The legacy Vercel proxy has been retired. Use the genuine native IndicWrite converter.",
    canonical_url: CANONICAL
  });
}
