<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjekirjan suorittamiseen tarvittavat alustan määritykset.

## Tarvittavat sovellukset/kehykset

### Windows/Linux

- **Lemonade Server** tulee asentaa
  [Lemonade-asennusoppaan](https://lemonade-server.ai/docs/guide/install/) mukaisesti.
- **Node.js 22.12 tai uudempi** ja `npm`, joita `agent-canvas`-CLI ja `npx`:llä käynnistetyt
  MCP-palvelimet käyttävät.
- **uv**, Python-pakettien hallintaohjelma, jota Agent Canvas käyttää agenttipalvelimen
  ympäristön hallintaan. Asenna se
  [uv-asennusoppaan](https://docs.astral.sh/uv/getting-started/installation/) mukaisesti.

## Tarvittavat mallit

### Windows/Linux

Seuraavan mallin tulee olla Lemonade Serverin käytettävissä ennen ohjekirjan
käynnistämistä.

| Mallityyppi | Mallitunnus | Huomautukset |
| --- | --- | --- |
| GGUF-keskustelumalli | `Qwen3.6-35B-A3B-GGUF` | Lemonade Server tarjoilee osoitteessa `http://127.0.0.1:13305/api/v1`. Käytä pienempää GGUF-mallia laitteissa, joissa on alle 32 Gt muistia. |

Käynnistä malli komennolla:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## Ulkoiset tunnistetiedot

Tämä ohjekirja vaatii:

- GitHub-tunnuksen, jolla on lukuoikeus yhteenvedon kohteena olevaan tietovarastoon.
- Slack-bottitunnuksen, jolla on `chat:write`- ja kanavan lukuoikeudet.
- Slack-tiimin tunnuksen ja kohde-Slack-kanavan tunnuksen.