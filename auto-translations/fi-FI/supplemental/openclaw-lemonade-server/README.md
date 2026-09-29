<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Aja OpenClaw Lemonade Server -taustajärjestelmällä

## Yleiskatsaus

[**OpenClaw**](https://openclaw.ai/) on autonominen tekoälyagentti, joka voi kirjoittaa ja suorittaa koodia, hallita tiedostoja ja tehdä puolestasi monimutkaisia monivaiheisia tehtäviä. Toisin kuin keskusteluavustaja, joka vain vastaa kysymyksiin, OpenClaw suorittaa todellisia toimintoja järjestelmässäsi, mikä tarkoittaa, että se tarvitsee nopean ja tehokkaan tekoälytaustajärjestelmän, joka pysyy vaativan agenttisilmukan tahdissa.

[**Lemonade Server**](https://lemonade-server.ai/) on juuri tällainen taustajärjestelmä. Se on avoimen lähdekoodin paikallinen päättelypalvelin, joka suorittaa generatiivisen tekoälyn malleja suoraan laitteistollasi ja tarjoaa ne käyttöön alan standardin mukaisen OpenAI API:n kautta.

Yhdessä ne muodostavat täysin paikallisen tekoälyagenttipinon: Lemonade hoitaa mallin päättelyn, ja OpenClaw tarjoaa agenttisilmukan, joka muuttaa mallin tulosteet todellisiksi toiminnoiksi.

> **Ennen kuin jatkat:** OpenClaw on erittäin autonominen tekoälyagentti. Minkä tahansa tekoälyagentin päästäminen käsiksi järjestelmääsi voi johtaa arvaamattomiin tai tahattomiin lopputuloksiin. Jatka vain, jos ymmärrät riskit ja olet valmis siihen, että autonominen ohjelmisto toimii puolestasi.

---

## Mitä opit

Tämän ohjeen lopussa osaat:

- Tutustua **Lemonade Serveriin**
- **Asentaa OpenClaw'n** ja **osoittaa sen käyttämään Lemonade Serveriä** tekoälytaustajärjestelmänään.
- **Käynnistää OpenClaw-yhdyskäytävän** ja varmistaa, että agenttisi on valmis toimimaan.
- **Yhdistää viestintäkanavan** (Discord tai Telegram), jotta voit keskustella agenttisi kanssa mistä tahansa laitteesta.

---

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetusten määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

<!-- @os:linux -->
- Tietokone, jossa on **Ubuntu 24.04+** tai yhteensopiva Debian-pohjainen Linux-jakelu, jossa on `apt-get`
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (valinnainen, OpenClaw'n hiekkalaatikointiin)
- **noin 10–30 Gt vapaata levytilaa** mallien painoille
<!-- @os:end -->

<!-- @os:windows -->
- Tietokone, jossa on **Windows 10/11**
- Vähintään **12 Gt RAM-muistia** (64 Gt+ suositellaan suuremmille malleille)
- **noin 10–30 Gt vapaata levytilaa** mallien painoille
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (valinnainen, OpenClaw'n hiekkalaatikointiin)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Suositellun mallin lataaminen ja käyttöönotto

Tämän ohjeen suositeltu malli on **Qwen3.6-35B-A3B-GGUF**, joka on peräisin Unslothilta. Kyseessä on vahva MoE-malli, jonka 263k-tokenin kontekstiikkuna sopii hyvin agenttityökuormille. Tämä malli käyttää UD-Q4_K_XL-kvantisointia. Lataa se nyt:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Lataa se sitten käyttöön suurella kontekstiikkunalla ja tallenna asetus tulevia ajokertoja varten:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Mallin oletuskontekstipituus on 262 144 tokenia. Jos kohtaat muistin loppumiseen liittyviä (OOM) virheitä, harkitse kontekstiikkunan pienentämistä. Koska Qwen3.6 kuitenkin hyödyntää laajennettua kontekstia monimutkaisissa tehtävissä, suosittelemme ylläpitämään vähintään 128K tokenin kontekstipituutta ajattelukyvyn säilyttämiseksi.

> **Vinkki: Poista ajattelu käytöstä nopeampia agenttivastauksia varten:** Qwen3.6-35B-A3B toimii oletuksena ajattelutilassa, mikä lisää viivettä ennen jokaista vastausta. Agenttisilmukoissa tämä ylimääräinen viive kertyy nopeasti. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json)-repositorio tarjoaa valmiin määrityksen, joka poistaa ajattelun käytöstä. Käytä sitä lataamalla tiedosto ja tuomalla se:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## WSL:n määrittäminen

Ajamme OpenClaw'n WSL:n sisällä (suositellaan) ja yhdistämme sen Windowsissa natiivisti suoritettavaan Lemonadeen. Tämä tarjoaa Linux-komentotulkkiympäristön OpenClaw'lle samalla kun Lemonaden GPU-kiihdytys pysyy Windows-puolella.

### Asenna WSL ja Ubuntu

Avaa PowerShell järjestelmänvalvojana ja asenna WSL-ydin:

```powershell
wsl --install --no-distribution
```

Asenna sitten Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Ota systemd käyttöön WSL:ssä

Suorita tämä Ubuntu-päätteessä:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Poistu WSL:stä ja käynnistä se uudelleen:

```powershell
exit
wsl --shutdown
wsl
```

### Sillan luominen Lemonadesta Windowsista WSL:ään

WSL2 toimii virtuaalisessa verkossa. Windowsissa toimiva Lemonade sitoutuu osoitteeseen `127.0.0.1`, johon WSL ei pääse suoraan käsiksi. Windowsin porttivälityspalvelin (port proxy) välittää liikenteen WSL-yhdyskäytävän IP-osoitteesta Windowsin localhost-osoitteeseen.

**Etsi WSL-yhdyskäytävän IP-osoite** (suorita WSL:ssä):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Lisää porttivälitys** (suorita järjestelmänvalvojana avatussa PowerShellissä, korvaa `<WSL-Gateway-IP>` WSL-yhdyskäytävän IP-osoitteellasi):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Huomio: Jos kohtaat virheen `netsh: command not found`, kokeile käyttää sen sijaan suoraan suoritettavan tiedoston nimeä - `netsh.exe`

**Lisää palomuurisääntö** (samassa korotetuissa oikeuksissa toimivassa PowerShellissä):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Vahvista WSL:stä**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Jos olet jo ladannut Qwen3.6-35B-A3B-GGUF-mallin edellisessä vaiheessa, sinun pitäisi nähdä tämän kaltainen JSON-tuloste:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

#### Sillan pitäminen toiminnassa uudelleenkäynnistyksen jälkeen

`netsh portproxy` -sääntö säilyy uudelleenkäynnistysten yli, mutta WSL:n yhdyskäytävän IP-osoite voi muuttua `wsl --shutdown` -komennon tai uudelleenkäynnistyksen jälkeen. Kun näin käy, välityspalvelin osoittaa yhä vanhaan IP-osoitteeseen, eikä Lemonade ole enää WSL:stä käytettävissä. Jos näin tapahtuu, käytä jotakin alla olevista vaihtoehdoista.

**Vaihtoehto 1 (suositeltu) — Korjaa silta automaattisesti.** Jotta et joutuisi tekemään tätä manuaalisesti joka kerta, käytä ajastettua tehtävää, joka tarkistaa sillan jokaisen käynnistyksen ja kirjautumisen yhteydessä ja rakentaa sen uudelleen vain, kun yhdyskäytävän IP-osoite on muuttunut. Katso [Lemonaden WSL-sillan automaattisen korjauksen opas](assets/RepairLemonadeWslBridge.md).


**Vaihtoehto 2 — Korjaa silta manuaalisesti.** Hanki ensin nykyinen WSL:n yhdyskäytävän IP-osoite suorittamalla tämä WSL:n sisällä:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopioi tämä arvo; käytät sitä alla `<new-WSL-Gateway-IP>`:n paikalla.

Suorita sitten **korotetuissa oikeuksissa toimivassa PowerShellissä** (Suorita järjestelmänvalvojana) seuraavat: listaa olemassa olevat säännöt, poista vain vanhentunut Lemonade-sääntö ja lisää uusi nykyisellä IP-osoitteella:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

`show all` -komennon tulosteessa vanhentunut Lemonade-sääntö on merkintä, jonka yhteysosoite (connect address) on `127.0.0.1` portissa `13305`; sen kuunteluosoite (listen address) on sinun `<old-WSL-Gateway-IP>`. Poistamalla tämän osoitteen mukaan poistetaan vain tämä sääntö, ja kaikki muut portproxy-säännöt koneellasi säilyvät koskemattomina.

Asennuksen aikana lisäämäsi palomuurisääntö on sidottu porttiin `13305` (ei IP-osoitteeseen), joten se toimii edelleen eikä sitä tarvitse luoda uudelleen.

> **Suositus:** Yhdyskäytäväongelmien välttämiseksi suosittelemme vahvasti seuraavaa komentotulkkiasetusta:
> - **Windows-komennot** tulisi suorittaa **PowerShellissä**
> - **WSL-jakelun komennot** tulisi suorittaa **komentokehotteessa** (suoritettuna **järjestelmänvalvojana**)

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Asenna ja määritä OpenClaw

### Asenna OpenClaw
<!-- @os:windows -->
> Suorita tämän osion komennot **WSL-päätteessä**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard`-lippu ohittaa interaktiivisen asennusvelhon; määrität mallin taustajärjestelmän manuaalisesti seuraavassa vaiheessa, mikä antaa sinulle tarkan hallinnan siitä, mitä mallia ja palvelinta käytetään.

Avaa uusi pääte ja vahvista asennus:

```bash
openclaw --version
```

> **Vihje:** Jos näet asennuksen jälkeen viestin `command not found`, lisää npm:n globaali bin-hakemisto PATH-muuttujaan:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Tehdäksesi tästä pysyvän, lisää yllä oleva rivi `~/.bashrc`- tai `~/.zshrc`-tiedostoosi.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


### Määritä OpenClaw käyttämään Lemonadea

Suorita OpenClaw:n ei-interaktiivinen käyttöönotto.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Tämä komento kirjoittaa OpenClaw:n määrityksen tiedostoon `~/.openclaw/openclaw.json`.

> **OpenClaw:n kontekstiikkunan mitoitus:** OpenClaw:n tiivistys (compaction) käynnistyy, kun `contextTokens > contextWindow − reserveTokens`. Oletusarvoinen `reserveTokensFloor` on 20 000 tokenia, alaraja, joka ohittaa `reserveTokens`-arvon, kun se on pienempi, joten mikä tahansa mallin konteksti alle noin 37 000 tokenia käynnistää loputtoman tiivistyssilmukan. Aseta pieni varaus ja poista alaraja käytöstä kerran määrityksessäsi, niin se pätee jokaiseen malliin ilman mallikohtaista säätöä:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` on *alaraja* (vähimmäissuoja), ei itse varaus; pelkän alarajan asettamisella ei ole vaikutusta. `reserveTokensFloor: 0` poistaa suojan käytöstä, jolloin pienempi `reserveTokens`-arvo hyväksytään.
>
> **Milloin tätä kannattaa käyttää:** Käytä tätä määritystä, jos mallisi tehokas kontekstiikkuna on alle noin 37 000 tokenia, joko siksi, että malli on pieni (esim. 8k, 16k, 32k), tai siksi, että olet tarkoituksella rajoittanut sen pienempään arvoon (esim. ladannut 128k-mallin, mutta asettanut kontekstin 16k:hon Lemonadessa). Ilman tätä OpenClaw joutuu käynnistyksessä loputtomaan tiivistyssilmukkaan.
>
> **Suuren kontekstin mallit täydellä kontekstilla:** Voit ohittaa tämän kokonaan. Oletusarvot toimivat hyvin, tiivistys käynnistyy hyvissä ajoin ennen ikkunan täyttymistä, ja mallilla on runsaasti tilaa tuottaa pitkiä vastauksia. Jos sovellat tätä silti, huomaa, että `reserveTokens: 4096` rajoittaa vastauksen pituuden noin 4k tokeniin, mikä saattaa katkaista pitkän tiedoston luonnin tai yksityiskohtaiset suunnitelmat.
>
> **Mihin tämä lisätään:** Sijoita `compaction`-lohko kohdan `agents.defaults` sisään `openclaw.json`-tiedostossasi (yleensä polussa `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Määrityksesi muut osat (gateway, channels, models jne.) pysyvät ennallaan, vain `compaction`-avain tarvitsee lisätä.
### (Suositeltu) Ota käyttöön Docker-hiekkalaatikointi

OpenClaw voi ohjata kaikki agentin tiedosto- ja koodioperaatiot eristetyn Docker-säiliön kautta sen sijaan, että ne suoritettaisiin suoraan isäntäkoneellasi. Tämä rajoittaa mahdollisten tahattomien toimien vaikutusalueen hiekkalaatikkoon, jolloin isäntäkoneesi tiedostojärjestelmä ja verkko pysyvät koskemattomina.

Rakenna hiekkalaatikkokuva kerran (Docker on oltava asennettuna):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Suorita tämä lisätäksesi `sandbox`-avaimen olemassa olevaan `agents.defaults`-lohkoon tiedostossa `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Hiekkalaatikkosäiliöillä ei ole **verkkoyhteyttä** oletusarvoisesti. Katso [hiekkalaatikoinnin viiteopas](https://docs.openclaw.ai/gateway/sandboxing) bind-liitoksia ja verkon ohituksia varten.

> #### Vianmääritys: Docker-käyttöoikeus evätty
> 
> Jos saat "permission denied" -virheen Docker-komentoja suorittaessasi:
> 
> **Vaihe 1: Lisää käyttäjäsi docker-ryhmään**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Vaihe 2: Jos virhe jatkuu, tee pysyvä korjaus**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Käynnistä sen jälkeen järjestelmäsi **uudelleen**.
> 
> **Nopea väliaikainen korjaus** (nollautuu uudelleenkäynnistyksen jälkeen):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
## (Suositeltu) OpenClaw-integraatio Firecrawl-palveluiden kanssa

[Firecrawl](https://docs.firecrawl.dev/introduction) tarjoaa itse isännöidyn verkon indeksointi- ja sisällönpoimintapalvelun, joka voi kiertää näitä haasteita ja vapauttaa OpenClaw-automaation koko potentiaalin.

Tässä asennuksessa OpenClaw toimii joukkona Docker-säiliöitä, joita hallitaan Podmanilla. Elinkaaren hallinnan ja automaattisen käynnistyksen yksinkertaistamiseksi rekisteröimme Firecrawlin käyttäjätason `systemd`-palveluksi, joka orkestroi taustalla olevaa Podman Compose -pinoa. Tämä mahdollistaa sen, että OpenClaw voi käynnistää yhdyskäytävän, pysäyttää ja tarkistaa Firecrawl-palvelun standardien `systemctl --user` -komentojen avulla ilman suoraa vuorovaikutusta säiliöiden kanssa.

Pitääksemme asian yksinkertaisena olemme jakaneet koko prosessin neljään vaiheeseen:

---

### 1. Rekisteröi järjestelmäpalvelu
Siirry systemd-käyttäjäkonfiguraation hakemistoon:
```bash
cd ~/.config/systemd/user
```
Luo ja avaa uusi tiedosto nimeltä `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopioi ja liitä seuraava konfiguraatio:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
Tässä vaiheessa palvelu on määritelty, mutta sitä ei ole vielä rekisteröity `systemd`:lle.
Varmista, että tiedostonimi vastaa täsmälleen edellä luomaasi, ja suorita sitten:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Jos onnistuit, sinun pitäisi nähdä seuraava tuloste:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` sisältää symboliset linkit palveluihin, jotka on määritetty käynnistymään automaattisesti.

### 2. Määritä Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) sopii ihanteellisesti niille, jotka tarvitsevat täyden hallinnan omista scraping- ja tiedonkäsittely-ympäristöistään, mutta se tuo mukanaan lisäylläpidon ja -konfiguroinnin vaatimuksia.

Aloita kloonaamalla repositorio:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Luo `.env`-tiedosto `/firecrawl`-hakemistoon: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Ota OpenClaw käyttöön Podman Composella

Ennen kuin jatkat, varmista, että olet noutanut uusimman OpenClaw Docker -kuvan:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Kun se on tehty, lataa OpenClaw Compose -tiedosto [openclaw-compose.yaml](assets/openclaw-compose.yaml) ja sijoita se juuritason `/firecrawl`-hakemistoon:

> Tämä käytäntö on tarpeen, jotta `systemd` löytää ja käynnistää palvelun oikein, kuten `WorkingDirectory=${HOME}/firecrawl`-asetuksessa on määritetty.

> Voit aina laajentaa pinoa lisäämällä uusia Firecrawl-palveluita tarpeen mukaan. Täydellinen luettelo saatavilla olevista palveluista löytyy virallisesta [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) -tiedostosta.

### 4. Käynnistä OpenClaw-palvelu Firecrawlin kautta 

Ennen kuin annat hallinnan `systemd`:lle, varmista, että kaikki toimii oikein suorittamalla pino manuaalisesti:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Jos kaikki on määritetty oikein, sinun pitäisi nähdä OpenClaw-säiliön käynnistyvän, ja komentorivin tulosteen pitäisi näyttää suunnilleen tältä:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Kun olet vahvistanut tämän, sammuta pino ennen jatkamista:
```bash
podman compose -f openclaw-compose.yaml down
```
Ennen palvelun käynnistämistä sinun on varmistettava, että `firecrawl`-hakemiston ja sen `.env`-tiedoston omistajuus ja käyttöoikeudet on asetettu oikein.
Tämä on välttämätöntä, jotta palvelu voi kirjoittaa tunnistetietosi käynnistyksen yhteydessä.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Nyt kun kaikki on vahvistettu, käynnistä palvelu `systemd`:n kautta:
```bash
systemctl --user start firecrawl.service
```
[OpenClaw Actions](https://docs.openclaw.ai/) on käytettävissä interaktiivisen säiliön sisältä, ja verkkokojelauta on saatavilla samassa isäntäkoneessa ja portissa osoitteessa http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### `OPENCLAW_GATEWAY_TOKEN`-arvon hankkiminen

Kun palvelu on käynnissä, huomaat, että kotikansioosi (~/.openclaw) on luotu uusi `.openclaw`-hakemisto. Tämä hakemisto on oletusarvoisesti lukittu, joten sinun on avattava se saadaksesi yhdyskäytävän tunnuksesi.

1. Myönnä pääsy hakemistoon:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Lue yhdyskäytävän tunnuksesi:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Etsi tulosteesta `OPENCLAW_GATEWAY_TOKEN`-arvo.

3. Avaa yhdyskäytävän kojelauta selaimessasi osoitteessa http://127.0.0.1:18789. Liitä tunnuksesi kehotettaessa todentaaksesi itsesi.

Pysäyttääksesi palvelun, suorita:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Käynnistä OpenClaw Gateway

Gateway on OpenClaw-prosessi, joka hallinnoi agenttisilmukkaa ja tarjoaa hallintapaneelin:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Avaa hallintapaneeli suorittamalla tämä toisessa päätteessä, samalla kun gateway on yhä käynnissä:

```bash
openclaw dashboard
```

Koska gateway sidotaan loopback-osoitteeseen, hallintapaneeli todentaa käyttäjän automaattisesti, kun se avataan samalta koneelta – tokenin syöttöä tai laitteen hyväksyntää ei tarvita paikallista käyttöä varten. Näet OpenClaw-hallintapaneelin, jossa Lemonade-mallisi näkyy aktiivisena taustajärjestelmänä.

> Jos olet ottanut hiekkalaatikoinnin (sandboxing) käyttöön, voit varmistaa sen toimivuuden pyytämällä agenttia suorittamaan `run hostname` hallintapaneelista. Jos näet koneesi isäntänimen sijaan lyhyen kontin tunnisteen, hiekkalaatikko toimii.

**Onnittelut, olet rakentanut täysin paikallisen tekoälyagenttipinon alusta alkaen.**

> **Tarvitsetko gatewayn tokenin?** Suorita `openclaw dashboard --no-open`, jolloin hallintapaneelin osoite tulostuu tokenin kanssa upotettuna (se yrittää myös kopioida sen leikepöydälle). Vaihtoehtoisesti token löytyy kohdasta `gateway.auth.token` tiedostossa `~/.openclaw/openclaw.json`.

**Hallintapaneelin käyttäminen toiselta laitteelta (SSH-tunnelin kautta)**

Jos OpenClaw on käynnissä etäkoneella, voit avata sen hallintapaneelin paikalliselta koneeltasi SSH-tunnelin kautta. Tunneli ohjaa gatewayn portin (`18789`) niin, että paikallinen selaimesi voi keskustella etäkoneen gatewayn kanssa osoitteen `127.0.0.1` kautta.

1. Yhdistä **paikalliselta koneeltasi** etäkoneeseen kerran ja hyväksy sormenjälkikehote, jotta isäntä lisätään tunnettuihin isäntiin:

   ```bash
   ssh user@<host-ip>
   ```

2. Avaa SSH-tunneli edelleen **paikalliselta koneeltasi**:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Huomio:** Kun olet syöttänyt salasanasi, pääte ei näytä mitään tulostetta ja vaikuttaa jumiutuneelta. Tämä on odotettua: `-N`-lippu kertoo SSH:lle, ettei se suorita mitään etäkomentoa, joten se ainoastaan pitää tunnelin auki. Jätä tämä pääte käyntiin.

3. Avaa **paikallisella koneellasi** selain ja siirry osoitteeseen `http://127.0.0.1:18789`.

4. Tulosta **etäkoneella** gatewayn token ja liitä se selaimeen kirjautuaksesi:

   ```bash
   openclaw dashboard --no-open
   ```

   Tämä tulostaa hallintapaneelin osoitteen tokenin kanssa upotettuna; kopioi token kirjautumista varten. (Token löytyy myös kohdasta `gateway.auth.token` tiedostossa `~/.openclaw/openclaw.json`.)

> **Etälaitteen hyväksyminen:** Kun avaat hallintapaneelin toiselta koneelta tai puhelimesta, selain saattaa näyttää pyyntötunnisteen. Listaa **etäkoneella** odottavat pyynnöt:
> ```bash
> openclaw devices list
> ```
> Hyväksy sitten vastaava pyyntö:
> ```bash
> openclaw devices approve <requestId>
> ```
> Tämä on tarpeen vain etä- tai toissijaisille laitteille; saman koneen loopback-käyttö todentuu automaattisesti. Katso lisätietoja [Etäkäyttö](https://docs.openclaw.ai/gateway/remote)-dokumentaatiosta.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Valinnainen: Yhdistä viestintäkanava

Kun gateway on käynnissä, voit tavoittaa paikallisen agenttisi mistä tahansa laitteesta. Valitse asetuksiisi sopiva vaihtoehto. OpenClaw tukee [Discordia](https://docs.openclaw.ai/channels/discord), [Telegramia](https://docs.openclaw.ai/channels/telegram) ja muita kanavia, katso koko lista osoitteesta [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Vaihtoehto A: Discord

Discord edellyttää palvelinta, jolla **sinulla on ylläpitäjän oikeudet** botin lisäämiseksi. Jos jaat palvelimia mutta et omista niitä, käytä sen sijaan vaihtoehtoa B (Telegram).

#### Luo Discord-tili ja -palvelin

Jos sinulla ei ole Discord-tiliä, rekisteröidy osoitteessa [discord.com](https://discord.com). Tarvitset myös palvelimen, jolla olet ylläpitäjä – luo sellainen napsauttamalla **+**-kuvaketta Discordin sivupalkissa ja valitsemalla **Create My Own**. Yksityinen palvelin riittää.

#### Luo Discord-sovellus ja botti

1. Siirry [Discord Developer Portaliin](https://discord.com/developers/applications) ja napsauta **New Application**. Anna sille nimi (esim. "openclaw-bot").
2. Napsauta sivupalkissa **Bot**. Aseta botille käyttäjänimi.
3. Vieritä edelleen Bot-sivulla kohtaan **Privileged Gateway Intents** ja ota käyttöön:
   - **Message Content Intent** (vaaditaan)
   - **Server Members Intent** (suositellaan)
4. Vieritä takaisin ylös ja napsauta **Reset Token** luodaksesi botin tokenin. Kopioi se.

#### Lisää botti palvelimellesi

1. Napsauta sivupalkissa **OAuth2/ URL Generator**.
2. Ota kohdassa **Scopes** käyttöön `bot` ja `applications.commands`.
3. Ota kohdassa **Bot Permissions** käyttöön: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopioi luotu osoite, liitä se selaimeesi, valitse palvelimesi ja vahvista. Botin pitäisi nyt näkyä palvelimesi jäsenluettelossa.

#### Kerää tunnisteesi

Ota Discordissa käyttöön kehittäjätila (**User Settings/ Advanced/ Developer Mode**), ja sen jälkeen:
- Napsauta palvelimesi kuvaketta hiiren oikealla painikkeella: **Copy Server ID**
- Napsauta omaa avatariasi hiiren oikealla painikkeella: **Copy User ID**

#### Salli yksityisviestit palvelimen jäseniltä

Napsauta palvelimesi kuvaketta hiiren oikealla painikkeella/ **Privacy Settings**/ ota käyttöön **Direct Messages**. Tämä sallii botin lähettää sinulle yksityisviestin, mikä vaaditaan pariutusvaiheessa.

#### Määritä OpenClaw Discordia varten

Tallenna botin token ympäristömuuttujaksi ja luo sitten yksi paikkaustiedosto, joka ottaa Discordin käyttöön, viittaa tokeniin ja lisää palvelimesi sallittujen listalle. Korvaa `<server_id>` ja `<user_id>` yllä kerätyillä tunnisteilla.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Älä luota siihen, että pyydät agenttia määrittämään tämän.** Kun hiekkalaatikointi on käytössä, agentti ei voi kirjoittaa tiedostoon `~/.openclaw/openclaw.json` hiekkalaatikon sisältä – käytä sen sijaan yllä mainittuja CLI-komentoja isäntäkoneella.

Käynnistä gateway uudelleen, jotta se ottaa uuden kanava-asetuksen käyttöön:

```bash
openclaw gateway run --bind loopback --port 18789
```

Näet gatewayn tulosteessa muutaman sekunnin sisällä tekstin `logged in to discord as <bot-name>`.
#### Yhdistä Discord-tilisi

Lähetä botille yksityisviesti Discordissa. Se vastaa lyhyellä pariskoodilla.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Hyväksy se koneella, jolla OpenClaw on käynnissä:
```bash
openclaw pairing approve discord <CODE>
```

> Pariskoodit vanhenevat tunnin kuluttua.

Voit nyt keskustella agenttisi kanssa suoraan Discordista ja siirtää tehtäviä paikalliselle laitteistollesi.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Vaihtoehto B: Telegram

Telegram on useimmille käyttäjille yksinkertaisempi kuin Discord, sillä se ei vaadi palvelinta eikä ylläpitäjän oikeuksia.

#### Luo Telegram-botti

1. Avaa Telegram ja lähetä viesti käyttäjälle **@BotFather**.
2. Lähetä `/newbot` ja seuraa ohjeita. Tallenna saamasi bottitunnus.

#### Määritä OpenClaw Telegramia varten

Tallenna tunnus ympäristömuuttujaan:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Lisää kanavan määritykset tiedostoon `~/.openclaw/openclaw.json` (tai päivitä se hallintapaneelin kautta):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Käynnistä yhdyskäytävä uudelleen ja lähetä botillesi mikä tahansa viesti Telegramissa. Hyväksy pariutuminen:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Pariskoodit vanhenevat tunnin kuluttua. Voit nyt keskustella agenttisi kanssa Telegramin yksityisviesteillä.

---

## Seuraavat askeleet

Nyt kun agenttisi voi vastaanottaa komentoja puhelimestasi ja toimia paikallisella koneellasi, tässä on kolme tutkimisen arvoista suuntaa:

1. **Osakemarkkinoiden yhteenveto**: Ajasta OpenClaw hakemaan tietoa rahoitusalan rajapinnoista kiinteällä aikavälillä, tiivistämään päivän liikkeet paikallisella mallillasi ja lähettämään yhteenvedon puhelimeesi joka aamu valitsemasi kanavan kautta.

2. **Hienosäädön valvonta**: Käynnistä koulutustehtävä etänä Telegramin tai Discordin kautta, ja anna agentin seurata koulutuslokia sekä raportoida määräajoin häviöarvot, GPU:n käyttöasteen ja levytilan käytön puhelimeesi. Jos ajo pysähtyy tai VRAM piikittyy, saat siitä tiedon välittömästi ilman, että sinun tarvitsee olla koneen ääressä.

3. **IoT paikallisella VLM:llä**: Suuntaa kamera etuoveesi, aja näkömalli Lemonadella ja anna OpenClaw'n analysoida kuvia pyynnöstä tai liipaisimen perusteella. Kysy puhelimestasi "saapuiko tänään paketteja?" ja saat suoran vastauksen omalta laitteistoltasi.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->