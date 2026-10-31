# IndicWrite supported-Python container for a provider with 2GB RAM

Use `Dockerfile.cloud` **instead of** the legacy Python 3.10 local-only
`Dockerfile.demo`. This image uses Python3.12, the unchanged official
AI4Bharat IndicXlit neural weights, and the independently pinned MIT
ShunyaLabs Fairseq/Hydra import-compatibility code.

Official model predictions were genuinely verified on Python 3.12: all
40/40 identical to the documented original Python3.10 results, run
[41210696882](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41210696882).
The image itself needs its own build/smoke/health check before being trusted;
do not confuse the existing legacy Docker success with this image.

For an isolated container host (Northflank or similar) without introducing
billing, select a **free tier/credit allowance** and a single service with
**at least 2 GB RAM**, publish the port from the `PORT` variable or 8501,
point to this repo's `main` branch and Dockerfile path `Dockerfile.cloud`.
Disable paid upgrades, replicas, database and persistent disk. Check usage
and monthly credit consumption; free trial credits do not guarantee indefinite
no-cost hosting. If the billing page requires a payment method, STOP.

Do not copy any secrets, model weights or private BharatGen experiments into
the public service. The hosted app itself is free to visitors while the
configured service is running. Run a real external browser conversion and
check RAM before announcing a production URL.
