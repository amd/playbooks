<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega vodnika.

## Zahtevane aplikacije/ogrodja

### Windows/Linux

- **Lemonade Server** mora biti nameščen v skladu z
  [vodnikom za namestitev Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ali novejši** in `npm`, ki ju uporablja `agent-canvas` CLI.
- **uv**, upravitelj paketov Python, ki ga Agent Canvas uporablja za upravljanje
  okolja agentskega strežnika. Namestite ga iz
  [vodnika za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/).

## Zahtevani modeli

### Windows/Linux

Naslednji model mora biti na voljo za Lemonade Server, preden zaženete
vodnik.

| Vrsta modela | ID modela | Opombe |
| --- | --- | --- |
| Klepetalni model GGUF | `Qwen3.6-35B-A3B-GGUF` | Streže ga Lemonade Server na `http://127.0.0.1:13305/api/v1`. Na napravah z manj kot 32 GB pomnilnika uporabite manjši model GGUF. |

Model zaženite z:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
