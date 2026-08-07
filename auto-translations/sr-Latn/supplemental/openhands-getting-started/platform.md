<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

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
