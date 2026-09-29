<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) on DeepSeek V4 -perheen tehokkuuteen keskittyvä versio — 284 miljardin parametrin Mixture of Experts -malli, jossa on 13 miljardia aktiivista parametria. [DeepSeekin teknisen raportin](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) mukaan se saavuttaa 79 % tuloksen SWE-bench Verified -testissä ja 91,6 % LiveCodeBench-testissä.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) on erityisesti tälle mallille kehitetty päättelymoottori. Sen sijaan, että kyseessä olisi yleiskäyttöinen ajoympäristö, ds4 on suunnattu suoraan DeepSeek V4 -perheeseen arkkitehtuurikohtaisilla ytimen optimoinneilla AMD ROCm™ -ohjelmistolle. Se on tällä hetkellä yksi parhaiten suoriutuvista DeepSeek V4 Flash -toteutuksista Strix Halo -alustalla.

Tässä oppaassa näytetään, miten `ai-toolbox-cockpit`-pääteympäristöä käytetään ds4:n asentamiseen, mallipainojen lataamiseen ja DeepSeek V4 Flash -mallin paikallisen tarjoamisen käynnistämiseen AMD Ryzen™ AI Halo Developer Platform -alustalla.

## Mitä opit

- Kuinka asentaa ja käynnistää `ai-toolbox-cockpit`-pääteympäristön
- Kuinka luoda ds4-ROCm-työkalulaatikkokontti (toolbox container)
- Suositellun kvantisoinnin lataaminen yhtä Halo-solmua varten
- ds4-päättelypalvelimen käynnistäminen ja OpenAI-yhteensopivan päätepisteen paljastaminen
- Web UI:n tai koodausagentin yhdistäminen paikalliseen palvelimeen

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

## Ohjelmistovaatimusten asentaminen

> **Tämän kokoonpanon (yhden solmun IQ2_XXS, 126k konteksti) järjestelmävaatimukset:**
> - Strix Halo -järjestelmä, jossa on **vähintään 128 Gt yhtenäistä muistia**.
> - **BIOSin varattu VRAM (UMA-kehyspuskuri) asetettuna minimiin**, jotta jaettu muistipooli voi olla mahdollisimman suuri.
> - GPU:n **jaetun muistipoolin koko asetettuna vähintään 110 Gt:hen**: suorita `amd-ttm --set 110` (katso yllä oleva muistiasetuksen määritysvaihe) ja käynnistä järjestelmä uudelleen. Pienemmät arvot voivat aiheuttaa muistin loppumisen mallin latautuessa 126k kontekstilla. Jos järjestelmässäsi on vähemmän muistia käytettävissä, laske sen sijaan **Context**-arvoa Server Mode -tilassa.
>
> **Huomautus:** Kokeile asettaa **GPU:n jaettu muistipooli** aluksi arvoon **110 Gt**. Jos törmäät muistin loppumista koskeviin virheisiin, nosta jaettua muistipoolia tai pienennä kontekstin kokoa.

ai-toolbox-cockpit käyttää säilön työkalulaatikoita (container toolboxes) ds4-moottorin suorittamiseen. Asenna `podman`, `distrobox` ja `pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## Saatavilla olevat kvantisoinnit

ds4:n kehittäjä tarjoaa useita DeepSeek V4 Flash -mallin kvantisoituja versioita GGUF-muodossa. Kaikki alla olevat mallit käyttävät importance matrix (imatrix) -kalibrointia, joka säilyttää tarkemman tarkkuuden malliin osissa, jotka ovat tärkeimpiä koodaus- ja päättelytehtävien kannalta.

| Kvantisointi | Koko | Kuvaus |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 Gt | Suositellaan yhdelle 128 Gt:n solmulle |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 Gt | Säilyttää kerrokset 37–42 Q4-tarkkuudella paremman tarkkuuden saavuttamiseksi. Mahtuu 128 Gt:hen, mutta jättää vähemmän tilaa kontekstille |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 Gt | Korkeampi laatu. Vaatii kaksi Halo-solmua useiden solmujen klusteroinnin kautta |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 Gt | Valinnainen lisäosa spekulatiiviselle dekoodaukselle, joka parantaa generointinopeutta |

**IQ2_XXS imatrix** -malli on hyvä lähtökohta. Se mahtuu mukavasti yhteen solmuun ja jättää tarpeeksi muistia kohtuulliselle kontekstin kokoluokalle.

## ai-toolbox-cockpitin asentaminen

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) on kevyt pääteympäristö, joka helpottaa erilaisten tekoälytaustajärjestelmien asentamista. Käytämme sitä ds4-säilön luomiseen, mallipainojen lataamiseen ja palvelinten käynnistämiseen. Asenna se `pipx`:llä:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Käynnistä cockpit:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Vaihe 1: Työkalulaatikon luominen

**Interactive Toolboxes** -välilehdellä valitse uusin saatavilla oleva/vakaa työkalulaatikko ds4:lle (esim. `ds4-rocm-10.0`) ja napsauta **Create/Update**. Tämä hakee säilökuvan ja luo työkalulaatikkoympäristön.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Vaihe 2: Mallin lataaminen

Siirry **Models**-välilehdelle. Valitse ensin taustajärjestelmä (ds4). Valitse sitten avattavasta valikosta **IQ2_XXS imatrix (~80.8 GB)** ja napsauta **Download**. Mallitiedostot tallennetaan oletuksena hakemistoon `~/ds4` (voit muuttaa tallennuspolkua).

> **Huomautus:** IQ2_XXS-malli on kooltaan noin 80 Gt, joten lataaminen voi kestää jonkin aikaa yhteydestäsi riippuen. Voit jatkaa, kun lataus on valmis.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## Vaihe 3: Palvelimen käynnistäminen

Siirry **Server Mode** -välilehdelle. Valitse ladattu malli ja työkalulaatikko, ja määritä sitten kontekstin koko, isäntä (host) ja portti. Kun olet valmis, napsauta **Start ds4-server**.

> **Vihje** Kontekstin koko `126000` on järkevä lähtöarvo, jonka pitäisi mahtua yhteen solmuun — voit asettaa sen suuremmaksi, jos sinulla on ylimääräistä muistia, tai pienentää sitä, jos törmäät muistin loppumista koskeviin virheisiin. Portti (`8000` tässä oppaassa) on mielivaltainen; valitse mikä tahansa vapaa portti.

> **KV-levyvälimuisti (valinnainen).** **KV Disk Cache** -asetuksen käyttöönotto siirtää KV-välimuistin levylle (kohdassa **Host Cache Dir**, oletuksena `~/.cache/ds4-kv`), jotta toistuvat järjestelmäkehotteet palautetaan SSD-levyltä sen sijaan, että ne laskettaisiin uudelleen. Tämä on suorituskykyoptimointi koodausagenttien työnkuluille, joissa on pitkiä, toistuvia kehotteita, eikä se ole **pakollinen** palvelimen käyttämiseksi.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Palvelin käynnistyy ja kuuntelee porttia 8000, paljastaen OpenAI-yhteensopivan API-päätepisteen osoitteessa `http://localhost:8000/v1`.

**Pikatesti:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->
## Web-käyttöliittymän yhdistäminen

Voit yhdistää minkä tahansa keskustelukäyttöliittymän, joka tukee OpenAI API -muotoa. Voit esimerkiksi käyttää HuggingFace ChatUI -käyttöliittymää:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Avaa selaimessasi osoite `http://localhost:3000` aloittaaksesi keskustelun.

> **Huomio:** `--network=host` asettaa Web-käyttöliittymän isäntäkoneen verkkoon, jotta se pääsee käsiksi ds4-palvelimeen suoraan osoitteessa `localhost`. Tämä pitää ds4-palvelimen sidottuna loopback-osoitteeseen (sen ei tarvitse olla näkyvillä muissa liittymissä).

> **Vinkki:** Web-käyttöliittymän portti (tässä `3000`, asetettu muuttujalla `PORT`) on mielivaltainen — valitse mikä tahansa vapaa portti, jos `3000` on jo käytössä, ja avaa sitten kyseinen portti selaimessasi. Varmista, että `OPENAI_BASE_URL`-osoitteen portti vastaa porttia, jossa ds4-palvelimesi on käynnissä.

## Koodausagentin yhdistäminen

ds4-palvelin tarjoaa sekä OpenAI- että Anthropic-yhteensopivat rajapinnat, joten useimmat koodausagentit voivat yhdistää siihen suoraan. Voit esimerkiksi lisätä sen `pi`-koodausagenttiin lisäämällä seuraavan lohkon tiedostoon `~/.pi/agent/models.json`:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **Vinkki**: Jos koodausagenttisi tai Web-käyttöliittymäsi on käynnissä eri koneella kuin Halo-alusta, sinun täytyy välittää palvelimen portti (tässä `8000`) SSH:n kautta:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Seuraavat vaiheet

- **Usean solmun klusterointi**: Jos sinulla on kaksi Halo-laitetta, ds4 tukee Q4-mallin (~153 Gt) jakamista kahden koneen kesken pipeline-rinnakkaisuuden avulla. Katso asennusohjeet [ds4-toolboxin dokumentaatiosta](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Spekulatiivinen dekoodaus (MTP)**: Lataa MTP-painot (~3,6 Gt) ja välitä `--mtp` palvelimelle nopeampaa generointinopeutta varten.
- **KV-välimuistin siirto levylle**: Koodausagenttien työnkulkuja varten ota käyttöön `--kv-disk-dir`, jotta toistuvat järjestelmäkehotteet palautetaan SSD-levyltä sen sijaan, että ne laskettaisiin uudelleen joka kerta.

Lisätietoja löydät [ds4-repositoriosta](https://github.com/antirez/ds4) ja [ds4-cockpit-toolboxista](https://github.com/kyuz0/strix-halo-ds4-toolbox).