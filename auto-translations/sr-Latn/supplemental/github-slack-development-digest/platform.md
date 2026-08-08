<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika (playbook).

## Potrebne aplikacije/frameworks

### Windows/Linux

- **Lemonade Server** treba biti instaliran prema
  [vodiču za instalaciju Lemonade-a](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ili noviji** i `npm`, koje koriste `agent-canvas` CLI i MCP
  serveri pokrenuti pomoću `npx`.
- **uv**, Python menadžer paketa koji Agent Canvas koristi za upravljanje okruženjem agent
  servera. Instalirajte ga prema
  [vodiču za instalaciju uv-a](https://docs.astral.sh/uv/getting-started/installation/).

## Potrebni modeli

### Windows/Linux

Sledeći model mora biti dostupan Lemonade Server-u pre pokretanja
priručnika.

| Tip modela | ID modela | Napomene |
| --- | --- | --- |
| GGUF model za ćaskanje | `Qwen3.6-35B-A3B-GGUF` | Servira ga Lemonade Server na `http://127.0.0.1:13305/api/v1`. Koristite manji GGUF model na uređajima sa manje od 32 GB memorije. |

Pokrenite model pomoću:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Eksterni kredencijali

Ovaj priručnik zahteva:

- GitHub token sa pravom čitanja repozitorijuma koji se sumira.
- Slack bot token sa `chat:write` i pravom čitanja kanala.
- Slack team ID i ID ciljnog Slack kanala.