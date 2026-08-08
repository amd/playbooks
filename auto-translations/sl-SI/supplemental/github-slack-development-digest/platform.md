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

- **Lemonade Server** je treba namestiti po navodilih v
  [vodniku za namestitev Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 ali novejši** in `npm`, ki ju uporabljata CLI orodje `agent-canvas` in strežniki MCP,
  zagnani z `npx`.
- **uv**, upravitelj paketov Python, ki ga Agent Canvas uporablja za upravljanje okolja
  agentskega strežnika. Namestite ga po navodilih v
  [vodniku za namestitev uv](https://docs.astral.sh/uv/getting-started/installation/).

## Zahtevani modeli

### Windows/Linux

Naslednji model mora biti na voljo strežniku Lemonade Server, preden začnete izvajati
vodnik.

| Vrsta modela | ID modela | Opombe |
| --- | --- | --- |
| Model za klepet GGUF | `Qwen3.6-35B-A3B-GGUF` | Strežnik Lemonade Server ga ponuja na `http://127.0.0.1:13305/api/v1`. Na napravah z manj kot 32 GB pomnilnika uporabite manjši model GGUF. |

Model zaženite z:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Zunanja poverila

Ta vodnik zahteva:

- Žeton GitHub z bralnim dostopom do repozitorija, ki se povzema.
- Žeton bota Slack z dostopom `chat:write` in bralnim dostopom do kanalov.
- ID ekipe Slack in ID ciljnega kanala Slack.