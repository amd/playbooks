<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog playbook-a.

## Potrebne aplikacije/frameworkovi

### Windows/Linux

- **Lemonade Server** treba instalirati prateći
  [Lemonade vodič za instalaciju](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ili noviji** i `npm`, koje koristi `agent-canvas` CLI.
- **uv**, Python menadžer paketa koji Agent Canvas koristi za upravljanje
  okruženjem agent servera. Instalirajte ga sa
  [uv vodiča za instalaciju](https://docs.astral.sh/uv/getting-started/installation/).

## Potrebni modeli

### Windows/Linux

Sledeći model mora biti dostupan Lemonade Server-u pre pokretanja
playbook-a.

| Tip modela | ID modela | Napomene |
| --- | --- | --- |
| GGUF chat model | `Qwen3.6-35B-A3B-GGUF` | Servira ga Lemonade Server na `http://127.0.0.1:13305/api/v1`. Koristite manji GGUF model na uređajima sa manje od 32 GB memorije. |

Pokrenite model sa:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
