# Architecture — MVP

```
Streamlit UI (app.py)
    |
    | text + comma-separated explicit protected words
    v
src/indicwrite/core.py
    | validate: 500 characters, 80 Roman tokens
    | tokenize: [A-Za-z]+ vs everything else
    | preserve punctuation, digits, Devanagari, spacing
    | cache repeated words within request
    v
src/indicwrite/engine.py
    | lazy singleton
    v
Official ai4bharat.transliteration.XlitEngine("hi", beam_width=4, rescore=False)
    | pretrained Indian-language neural model
    v
Result: join unchanged text and predicted Hindi token strings
    v
Streamlit output (copyable st.code / download)
```

The official Python interface is word-level. The MVP therefore calls `translit_word` for Roman tokens, rather than inventing a sentence-level grammar model. The backend does **not** correct grammatical errors or translate into English. Neither is claimed implemented.

Caching is local to the Python process for the engine and local to each conversion for token predictions. Weight files are downloaded and cached by the upstream package, and never committed.

Potential quality limitations: mixed-script tokens, English words not in explicit preserve list, capitalized names, punctuation normalization, transliteration ambiguity without sentence context. Rewriting and translation should remain optional modules, with independently verified inference and metrics.
