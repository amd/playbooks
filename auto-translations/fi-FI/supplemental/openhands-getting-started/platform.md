<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan odotetut alustan konfiguraatiot tämän ohjekirjan suorittamista varten.

## Vaaditut sovellukset/kehykset

### Windows/Linux

- **Lemonade Server** tulee asentaa
  [Lemonaden asennusoppaan](https://lemonade-server.ai/docs/guide/install/) ohjeiden mukaisesti.
- **Node.js 22.12 tai uudempi** ja `npm`, joita `agent-canvas`-komentorivityökalu käyttää.
- **uv**, Python-pakettienhallinta, jota Agent Canvas käyttää agenttipalvelimen
  ympäristön hallintaan. Asenna se
  [uv:n asennusoppaan](https://docs.astral.sh/uv/getting-started/installation/) mukaisesti.

## Vaaditut mallit

### Windows/Linux

Seuraavan mallin tulee olla Lemonade Serverin saatavilla ennen ohjekirjan
aloittamista.

| Mallityyppi | Mallitunnus | Huomautukset |
| --- | --- | --- |
| GGUF-keskustelumalli | `Qwen3.6-35B-A3B-GGUF` | Lemonade Server palvelee osoitteessa `http://127.0.0.1:13305/api/v1`. Käytä pienempää GGUF-mallia laitteissa, joissa on alle 32 Gt muistia. |

Käynnistä malli komennolla:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
