# IndicWrite — isolated, local-only classroom demonstration

**Scope:** The exact official AI4Bharat IndicXlit implementation, with a fully local Streamlit user interface. It uses the legacy Python 3.10 environment already verified by earlier GitHub CI. Python 3.10 reached its final security release on 1 October 2026, so **never expose this demo to the public internet** or reuse this image for another application.

From the repository root on Windows with Docker Desktop installed and WSL2 integration enabled:

```powershell
docker compose -f compose.demo.yml build
docker compose -f compose.demo.yml up
```

Open **http://127.0.0.1:8501**. The port is bound only to the local machine. First conversion may download official model weights into a dedicated named volume. Try `kal mujhe college jana hai!`, then demonstrate Clear, English term preservation and downloading the Hindi result.

To stop without deleting cache:

```powershell
docker compose -f compose.demo.yml down
```

To run a genuine pretrained smoke within the built container:

```powershell
docker compose -f compose.demo.yml run --rm --entrypoint python indicwrite scripts/smoke_indicxlit.py
```

The Compose command ensures the model runs inside the same isolated service with its cached weights and localhost-only policy.

The Docker image does not include BharatGen, OPUS or IndicTrans2. It neither creates nor queries any database and has no access to other repositories or services. `INDICWRITE_PRIVATE_BHARATGEN=0` explicitly disables the private research mode.

**Release gate:** Local Docker build/inference must pass real CI before claiming this exact container was tested. Even then, a localhost Docker demo is not a publicly hosted URL, and cannot replace the separate licensing approvals required for public BharatGen outputs.
