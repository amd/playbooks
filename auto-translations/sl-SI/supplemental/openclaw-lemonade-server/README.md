<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Zaganjanje OpenClaw z Lemonade Server kot zaledjem

## Pregled

[**OpenClaw**](https://openclaw.ai/) je avtonomni AI agent, ki lahko piše in izvaja kodo, upravlja z datotekami ter opravlja zapletena, večstopenjska opravila v vašem imenu. Za razliko od klepetalnega asistenta, ki zgolj odgovarja na vprašanja, OpenClaw izvaja resnična dejanja v vašem sistemu, kar pomeni, da potrebuje hitro in zmogljivo AI zaledje, ki lahko sledi zahtevnemu ciklu delovanja agenta.

[**Lemonade Server**](https://lemonade-server.ai/) je prav to zaledje. Gre za odprtokodni lokalni strežnik za sklepanje, ki poganja GenAI modele neposredno na vaši strojni opremi in jih izpostavi prek standardnega API-ja OpenAI za panogo.

Skupaj tvorita popolnoma lokalen sklad AI agenta: Lemonade skrbi za sklepanje modela, OpenClaw pa zagotavlja zanko agenta, ki izhode modela pretvori v dejanska dejanja.

> **Preden nadaljujete:** OpenClaw je visoko avtonomen AI agent. Dodelitev dostopa do vašega sistema kateremu koli AI agentu lahko privede do nepredvidljivih ali nenamernih posledic. Nadaljujte le, če razumete tveganja in vam je udobno z avtonomno programsko opremo, ki deluje v vašem imenu.

---

## Kaj se boste naučili

Do konca tega vodnika boste zmožni:

- Spoznati **Lemonade Server**
- **Namestiti OpenClaw** in ga **usmeriti na Lemonade Server** kot svoje AI zaledje.
- **Zagnati prehod OpenClaw** in potrditi, da je vaš agent pripravljen za delo.
- **Povezati komunikacijski kanal** (Discord ali Telegram), da se boste lahko s svojim agentom pogovarjali iz katere koli naprave.

---

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme

<!-- @os:linux -->
- Računalnik z operacijskim sistemom **Ubuntu 24.04+** ali z združljivo distribucijo Linuxa, ki temelji na Debianu, z `apt-get`
- Vsaj **12 GB RAM-a** (priporočeno 64 GB+ za večje modele)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (izbirno, za peskovnik OpenClaw)
- **~10–30 GB prostega prostora na disku** za uteži modela
<!-- @os:end -->

<!-- @os:windows -->
- Računalnik z operacijskim sistemom **Windows 10/11**
- Vsaj **12 GB RAM-a** (priporočeno 64 GB+ za večje modele)
- **~10–30 GB prostega prostora na disku** za uteži modela
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (izbirno, za peskovnik OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Prenos in nalaganje priporočenega modela

Priporočeni model za ta vodnik je **Qwen3.6-35B-A3B-GGUF** podjetja Unsloth, zmogljiv model MoE z 263k-žetonskim kontekstnim oknom, ki je zelo primeren za obremenitve agentov. Ta model uporablja kvantizacijo UD-Q4_K_XL. Prenesite ga zdaj:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Nato ga naložite z velikim kontekstnim oknom in to nastavitev shranite za prihodnje zagone:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ima privzeto kontekstno dolžino 262.144 žetonov. Če naletite na napake zaradi pomanjkanja pomnilnika (OOM), razmislite o zmanjšanju kontekstnega okna. Ker pa Qwen3.6 za zahtevna opravila izkorišča razširjen kontekst, priporočamo ohranitev kontekstne dolžine vsaj 128K žetonov, da se ohranijo zmožnosti razmišljanja.

> **Nasvet: onemogočite razmišljanje za hitrejše odzive agenta:** Qwen3.6-35B-A3B privzeto deluje v načinu razmišljanja, kar pred vsakim odgovorom doda zakasnitev. Pri zankah agenta se ta dodatna obremenitev hitro nakopiči. Repozitorij [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) ponuja pripravljeno konfiguracijo, ki onemogoči razmišljanje. Za uporabo prenesite datoteko in jo uvozite:
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

## Nastavitev WSL

OpenClaw poganjamo znotraj WSL (priporočeno) in ga povežemo z Lemonade, ki teče izvorno v sistemu Windows. To vam zagotovi okolje lupine Linux za OpenClaw, medtem ko GPU pospeševanje Lemonade ostane na strani Windows.

### Namestitev WSL in Ubuntu

Odprite PowerShell kot skrbnik in namestite jedro WSL:

```powershell
wsl --install --no-distribution
```

Nato namestite Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogočanje systemd v WSL

To zaženite znotraj terminala Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Zapustite WSL in ga ponovno zaženite:

```powershell
exit
wsl --shutdown
wsl
```

### Premostitev Lemonade iz sistema Windows v WSL

WSL2 teče v virtualnem omrežju. Lemonade v sistemu Windows se veže na `127.0.0.1`, do katerega WSL ne more dostopati neposredno. Windowsov posrednik vrat (port proxy) posreduje promet z IP-ja prehoda WSL na lokalni gostitelj (localhost) sistema Windows.

**Poiščite svoj IP prehoda WSL** (zaženite znotraj WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte posrednik vrat** (zaženite v PowerShell kot skrbnik, pri čemer `<WSL-Gateway-IP>` zamenjajte s svojim IP-jem prehoda WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Opomba: Če naletite na napako `netsh: command not found`, poskusite namesto tega uporabiti izrecno ime izvedljive datoteke – `netsh.exe`

**Dodajte pravilo požarnega zidu** (v istem povišanem PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Preverite iz WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Če ste v prejšnjem koraku že naložili model Qwen3.6-35B-A3B-GGUF, bi morali videti JSON izhod, kot je ta:

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

#### Ohranjanje delovanja mostu po ponovnem zagonu

Pravilo `netsh portproxy` preživi ponovne zagone, vendar se IP-naslov prehoda WSL lahko spremeni po ukazu `wsl --shutdown` ali ponovnem zagonu. Ko se to zgodi, proxy še vedno kaže na stari IP-naslov in Lemonade postane nedosegljiv iz WSL. Če se to zgodi, uporabite eno od spodnjih možnosti.

**Možnost 1 (priporočeno) — samodejno popravilo mostu.** Da vam tega ne bi bilo treba delati ročno vsakič znova, uporabite načrtovano opravilo, ki preveri most ob vsakem zagonu in prijavi ter ga obnovi le, ko se IP-naslov prehoda spremeni. Glejte [vodnik za samodejno popravilo mostu Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Možnost 2 — ročno popravilo mostu.** Najprej pridobite trenutni IP-naslov prehoda WSL tako, da znotraj WSL zaženete naslednje:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopirajte to vrednost; uporabili jo boste namesto `<new-WSL-Gateway-IP>` spodaj.

Nato v **povišanem PowerShell** (zagon kot skrbnik) izpišite obstoječa pravila, izbrišite le zastarelo pravilo Lemonade in dodajte novo z aktualnim IP-naslovom:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

V izpisu ukaza `show all` je zastarelo pravilo Lemonade tisti vnos, katerega naslov za povezavo je `127.0.0.1` na vratih `13305`; njegov naslov za poslušanje je vaš `<old-WSL-Gateway-IP>`. Če izbrišete po tem naslovu, odstranite samo to pravilo, medtem ko ostala pravila portproxy na vašem računalniku ostanejo nedotaknjena.

Pravilo požarnega zidu, ki ste ga dodali med nastavitvijo, je vezano na vrata `13305` (ne na IP-naslov), zato še naprej deluje in ga ni treba ponovno ustvariti.

> **Priporočilo:** Da se izognete težavam s prehodom, močno priporočamo naslednjo konfiguracijo lupine:
> - **Ukazi za Windows** naj se izvajajo v **PowerShell**
> - **Ukazi za distribucijo WSL** naj se izvajajo v **ukaznem pozivu** (zagnanem kot **skrbnik**)

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

## Namestitev in konfiguracija OpenClaw

### Namestite OpenClaw
<!-- @os:windows -->
> Ukaze v tem razdelku zaženite znotraj svojega terminala **WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Zastavica `--no-onboard` preskoči interaktivnega čarovnika za nastavitev; zaledje modela boste ročno konfigurirali v naslednjem koraku, kar vam omogoča natančen nadzor nad tem, kateri model in strežnik se uporabljata.

Odprite nov terminal in potrdite namestitev:

```bash
openclaw --version
```

> **Nasvet:** Če po namestitvi vidite sporočilo `command not found`, dodajte npm-jev globalni bin imenik v svojo PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da to naredite trajno, dodajte zgornjo vrstico v svojo datoteko `~/.bashrc` ali `~/.zshrc`.

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


### Konfigurirajte OpenClaw za uporabo Lemonade

Zaženite neinteraktivno uvajanje OpenClaw.
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

Ta ukaz zapiše konfiguracijo OpenClaw v `~/.openclaw/openclaw.json`.

> **Določanje velikosti kontekstnega okna za OpenClaw:** Stiskanje (compaction) OpenClaw se sproži, ko `contextTokens > contextWindow − reserveTokens`. Privzeta vrednost `reserveTokensFloor` je 20.000 žetonov, kar je spodnja meja, ki preglasi `reserveTokens`, kadar je ta nižji, zato bo vsak kontekst modela pod ~37k sprožil neskončno zanko stiskanja. V svoji konfiguraciji nastavite nizko rezervo in enkrat onemogočite spodnjo mejo, kar velja za vsak model, brez potrebe po prilagajanju za posamezen model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodnja meja* (minimalna zaščita), ne rezerva sama, zato nastavitev samo spodnje meje nima učinka. `reserveTokensFloor: 0` onemogoči to zaščito, tako da je nižji `reserveTokens` sprejet.
>
> **Kdaj to uporabiti:** To konfiguracijo uporabite, če je dejansko kontekstno okno vašega modela pod ~37k, bodisi ker je model majhen (npr. 8k, 16k, 32k) bodisi ker ste namerno omejili kontekst na nižjo vrednost (npr. nalagate model s 128k, vendar v Lemonade nastavite kontekst na 16k). Brez tega OpenClaw ob zagonu vstopi v neskončno zanko stiskanja.
>
> **Modeli z velikim kontekstom pri polnem kontekstu:** To lahko v celoti preskočite. Privzete nastavitve delujejo dobro, stiskanje se bo sprožilo precej pred zapolnitvijo okna, model pa ima dovolj prostora za generiranje dolgih odgovorov. Če to vseeno uporabite, upoštevajte, da `reserveTokens: 4096` omeji dolžino odgovora na približno 4k žetonov, kar lahko prekine ustvarjanje dolgih datotek ali podrobnih načrtov.
>
> **Kam to dodati:** Blok `compaction` postavite znotraj `agents.defaults` v svoji datoteki `openclaw.json` (običajno na `~/.openclaw/openclaw.json`):
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
> Preostanek vaše konfiguracije (gateway, kanali, modeli itd.) ostane nespremenjen, dodati je treba le ključ `compaction`.
### (Priporočeno) Omogočite peskovnik Docker (Docker Sandboxing)

OpenClaw lahko vse operacije agenta z datotekami in kodo usmeri skozi izoliran vsebnik Docker, namesto da bi jih izvajal neposredno na vašem gostitelju. To omeji doseg morebitnega nenamernega dejanja na peskovnik, gostiteljev datotečni sistem in omrežje pa ostaneta nedotaknjena.

Zgradite sliko peskovnika (Docker mora biti nameščen):

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

Zaženite to, da dodate ključ `sandbox` znotraj obstoječega bloka `agents.defaults` v `~/.openclaw/openclaw.json`:

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

Vsebniki peskovnika privzeto **nimajo dostopa do omrežja**. Za bind mounts in preglase omrežja glejte [referenco za peskovnik](https://docs.openclaw.ai/gateway/sandboxing).

> #### Odpravljanje težav: Docker zavrne dovoljenje (Permission Denied)
> 
> Če pri izvajanju ukazov Docker dobite »permission denied«:
> 
> **Korak 1: Dodajte svojega uporabnika v skupino docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Korak 2: Če napaka ostane, uporabite trajno rešitev**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Nato **znova zaženite** sistem.
> 
> **Hitra začasna rešitev** (ponastavi se ob ponovnem zagonu):
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
## (Priporočeno) Integracija OpenClaw s storitvami Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) ponuja samostojno gostovano storitev za pajkanje po spletu in izvlečenje vsebine, ki lahko premosti te izzive in sprosti poln potencial avtomatizacije OpenClaw.

V tej postavitvi OpenClaw teče kot niz vsebnikov Docker, upravljanih s Podman. Za poenostavitev upravljanja življenjskega cikla in samodejnega zagona registriramo Firecrawl kot uporabniško storitev `systemd`, ki orkestrira spodnji sklad Podman Compose. To omogoča OpenClaw, da zažene prehod (gateway), ustavi in preveri storitev Firecrawl s standardnimi ukazi `systemctl --user`, namesto da bi neposredno komunicirali z vsebniki.

Za poenostavitev smo celoten postopek razdelili na štiri korake:

---

### 1. Registrirajte sistemsko storitev
Pomaknite se v mapo z uporabniško konfiguracijo systemd:
```bash
cd ~/.config/systemd/user
```
Ustvarite in odprite novo datoteko z imenom `firecrawl.service`.
```bash
nano firecrawl.service
```
Kopirajte in prilepite naslednjo konfiguracijo:
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
V tem trenutku je storitev definirana, vendar še ni registrirana pri `systemd`.
Poskrbite, da se ime datoteke natančno ujema z zgoraj ustvarjenim, nato zaženite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Če je postopek uspešen, bi morali videti naslednji izpis:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` vsebuje simbolne povezave do storitev, ki so nastavljene za samodejni zagon.

### 2. Konfigurirajte Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealen za tiste, ki potrebujejo popoln nadzor nad okoljem za pajkanje in obdelavo podatkov, vendar prinaša tudi dodaten trud pri vzdrževanju in konfiguraciji.

Začnite s kloniranjem repozitorija:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Ustvarite datoteko `.env` v mapi `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Namestite OpenClaw s Podman Compose

Preden nadaljujete, se prepričajte, da ste povlekli najnovejšo sliko Docker za OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ko je to opravljeno, prenesite datoteko Compose za OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) in jo namestite v korensko mapo `/firecrawl`:

> Ta konvencija je potrebna, da `systemd` pravilno najde in zažene storitev, kot je določeno v `WorkingDirectory=${HOME}/firecrawl`.

> Sklad lahko kadar koli razširite z dodatnimi storitvami Firecrawl po potrebi. Celoten seznam razpoložljivih storitev najdete v uradni datoteki [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Zaženite storitev OpenClaw prek Firecrawl

Preden prepustite nadzor `systemd`, ročno zaženite sklad in preverite, ali vse deluje pravilno:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Če je vse pravilno konfigurirano, bi moral vsebnik OpenClaw zagnati se, izpis v ukazni vrstici pa naj bi bil podoben temu:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Ko je preverjeno, pred nadaljevanjem znova ustavite sklad:
```bash
podman compose -f openclaw-compose.yaml down
```
Preden zaženete storitev, morate zagotoviti pravilno lastništvo in dovoljenja za mapo `firecrawl` in njeno datoteko `.env`.
To je nujno, da lahko storitev ob zagonu zapiše vaše poverilnice.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Zdaj, ko je vse preverjeno, zaženite storitev prek `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Dejanja OpenClaw](https://docs.openclaw.ai/) so dostopna znotraj interaktivnega vsebnika, nadzorna plošča (Web Dashboard) pa je na voljo na istem gostitelju in vratih na naslovu http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Pridobitev vašega žetona `OPENCLAW_GATEWAY_TOKEN`

Ko je storitev zagnana in deluje, boste v svoji domači mapi opazili novo mapo `.openclaw` (~/.openclaw). Ta mapa je privzeto zaklenjena, zato jo morate odkleniti, da pridobite svoj žeton za prehod (gateway token).

1. Odobrite dostop do mape:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Preberite svoj žeton za prehod:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
V izpisu poiščite vrednost `OPENCLAW_GATEWAY_TOKEN`.

3. Odprite nadzorno ploščo prehoda v brskalniku na naslovu http://127.0.0.1:18789. Ko boste pozvani k avtentikaciji, prilepite svoj žeton.

Za ustavitev storitve zaženite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Zaženite prehod OpenClaw (Gateway)

Prehod (angl. gateway) je proces OpenClaw, ki upravlja zanko agenta in postreže nadzorno ploščo:

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

Za odprtje nadzorne plošče to zaženite v drugem terminalu, medtem ko prehod še vedno teče:

```bash
openclaw dashboard
```

Ker se prehod povezuje na loopback, se nadzorna plošča samodejno preveri pristnost, ko je odprta v isti napravi, za lokalni dostop ni potreben vnos žetona ali odobritev naprave. Videti bi morali nadzorno ploščo OpenClaw z vašim modelom Lemonade, navedenim kot aktivno zaledje.

> Če ste omogočili peskovnik, lahko to preverite tako, da agenta prosite, naj v nadzorni plošči zažene `run hostname`. Če vidite kratek ID vsebnika namesto imena gostitelja vašega računalnika, peskovnik deluje.

**Čestitamo, zgradili ste popolnoma lokalen sklad AI agenta iz nič.**

> **Potrebujete žeton prehoda?** Zaženite `openclaw dashboard --no-open`, da izpišete URL nadzorne plošče z vgrajenim žetonom (poskuša ga tudi kopirati v odložišče). Alternativno je žeton na voljo pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.

**Dostop do nadzorne plošče iz druge naprave (prek predora SSH)**

Če OpenClaw teče na oddaljenem računalniku, lahko do njegove nadzorne plošče dostopate iz lokalnega računalnika prek predora SSH. Predor posreduje vrata prehoda (`18789`), tako da lahko vaš lokalni brskalnik komunicira z oddaljenim prehodom prek `127.0.0.1`.

1. Iz vašega **lokalnega računalnika** se enkrat povežite z oddaljenim računalnikom in sprejmite poziv za prstni odtis, da se gostitelj doda med znane gostitelje:

   ```bash
   ssh user@<host-ip>
   ```

2. Še vedno na vašem **lokalnem računalniku** odprite predor SSH:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Opomba:** Po vnosu gesla terminal ne prikaže nobenega izpisa in se zdi, da se je zataknil. To je pričakovano: zastavica `-N` pove SSH-ju, naj ne zažene nobenega oddaljenega ukaza, zato le drži predor odprt. Pustite ta terminal zagnan.

3. Na vašem **lokalnem računalniku** odprite brskalnik in pojdite na `http://127.0.0.1:18789`.

4. Na **oddaljenem računalniku** izpišite žeton prehoda in ga prilepite v brskalnik za prijavo:

   ```bash
   openclaw dashboard --no-open
   ```

   S tem se izpiše URL nadzorne plošče z vgrajenim žetonom; kopirajte žeton za prijavo. (Žeton je shranjen tudi pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.)

> **Odobritev oddaljene naprave:** Ko odprete nadzorno ploščo iz druge naprave ali telefona, lahko brskalnik prikaže ID zahteve. Na **oddaljenem računalniku** izpišite čakajoče zahteve:
> ```bash
> openclaw devices list
> ```
> Nato odobrite ustrezno zahtevo:
> ```bash
> openclaw devices approve <requestId>
> ```
> To je potrebno le za oddaljene ali drugotne naprave; dostop prek loopback z iste naprave se preveri samodejno. Za podrobnosti glejte dokumentacijo [Oddaljeni dostop](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Izbirno: Povežite komunikacijski kanal

Ko prehod teče, lahko do svojega lokalnega agenta dostopate iz katere koli naprave. Izberite možnost, ki ustreza vaši nastavitvi. OpenClaw podpira [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), in druge kanale, celoten seznam si oglejte na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord zahteva strežnik, kjer imate **skrbniški dostop** za dodajanje bota. Če si strežnike delite z drugimi, vendar nobenega ne posedujete, namesto tega uporabite možnost B (Telegram).

#### Ustvarite račun in strežnik Discord

Če nimate računa Discord, se prijavite na [discord.com](https://discord.com). Potrebujete tudi strežnik, kjer ste skrbnik; ustvarite ga s klikom na ikono **+** v stranski vrstici Discord in izbiro **Create My Own**. Zasebni strežnik je povsem v redu.

#### Ustvarite aplikacijo in bota Discord

1. Pojdite na [Discord Developer Portal](https://discord.com/developers/applications) in kliknite **New Application**. Poimenujte jo (npr. "openclaw-bot").
2. V stranski vrstici kliknite **Bot**. Nastavite uporabniško ime za bota.
3. Še vedno na strani Bot pomaknite se do **Privileged Gateway Intents** in omogočite:
   - **Message Content Intent** (obvezno)
   - **Server Members Intent** (priporočeno)
4. Pomaknite se nazaj navzgor in kliknite **Reset Token**, da ustvarite žeton bota. Kopirajte ga.

#### Dodajte bota v svoj strežnik

1. V stranski vrstici kliknite **OAuth2/ URL Generator**.
2. Pod **Scopes** omogočite `bot` in `applications.commands`.
3. Pod **Bot Permissions** omogočite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte ustvarjeni URL, prilepite ga v brskalnik, izberite svoj strežnik in potrdite. Bot bi se zdaj moral pojaviti na seznamu članov vašega strežnika.

#### Zberite svoje ID-je

Omogočite razvijalski način v Discordu (**User Settings/ Advanced/ Developer Mode**), nato:
- Z desnim klikom na ikono strežnika: **Copy Server ID**
- Z desnim klikom na svoj lasten avatar: **Copy User ID**

#### Dovolite zasebna sporočila od članov strežnika

Z desnim klikom na ikono strežnika/ **Privacy Settings**/ preklopite na **Direct Messages**. To bota omogoča, da vam pošlje zasebno sporočilo, kar je potrebno za korak seznanjanja.

#### Konfigurirajte OpenClaw za Discord

Shranite žeton bota kot spremenljivko okolja, nato ustvarite eno samo popravno datoteko, ki omogoči Discord, se sklicuje na žeton in dovoli vaš strežnik na seznamu dovoljenih. Zamenjajte `<server_id>` in `<user_id>` z ID-ji, zbranimi zgoraj.

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

> **Ne zanašajte se na to, da agenta prosite za konfiguracijo tega.** Ko je peskovnik omogočen, agent ne more pisati v `~/.openclaw/openclaw.json` znotraj peskovnika, namesto tega uporabite zgornje ukaze CLI na gostitelju.

Ponovno zaženite prehod, da prevzame novo konfiguracijo kanala:

```bash
openclaw gateway run --bind loopback --port 18789
```

V izpisu prehoda bi morali v nekaj sekundah videti `logged in to discord as <bot-name>`.
#### Poveži svoj Discord račun

Pošlji sporočilo botu na Discordu. Ta bo odgovoril s kratko kodo za povezovanje.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Potrdi jo na napravi, na kateri teče OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kode za povezovanje potečejo po eni uri.

Zdaj lahko klepetaš s svojim agentom neposredno prek Discorda in naloge prenašaš na svojo lokalno strojno opremo.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je za večino uporabnikov preprostejši od Discorda, saj ne zahteva strežnika ali skrbniškega dostopa.

#### Ustvari Telegram bota

1. Odpri Telegram in pošlji sporočilo botu **@BotFather**.
2. Pošlji `/newbot` in sledi navodilom. Shrani žeton bota, ki ti ga bo posredoval.

#### Konfiguriraj OpenClaw za Telegram

Shrani žeton kot spremenljivko okolja:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodaj konfiguracijo kanala v `~/.openclaw/openclaw.json` (ali jo popravi prek nadzorne plošče):

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

Ponovno zaženi prehod, nato botu pošlji sporočilo na Telegramu. Potrdi povezovanje:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kode za povezovanje potečejo po eni uri. Zdaj lahko s svojim agentom klepetaš prek zasebnih sporočil na Telegramu.

---

## Naslednji koraki

Zdaj ko lahko tvoj agent prejema ukaze s telefona in ukrepa na tvojem lokalnem računalniku, si oglej tri smeri, ki jih velja raziskati:

1. **Povzetek dogajanja na borzi**: Nastavi OpenClaw, da v fiksnih intervalih pridobiva podatke iz finančnih API-jev, s tvojim lokalnim modelom povzame dnevna dogajanja in vsako jutro prek izbranega kanala pošlje povzetek na tvoj telefon.

2. **Nadzor fine nastavitve**: Prek Telegrama ali Discorda oddaljeno sproži učno opravilo, nato pa naj agent spremlja dnevnik učenja ter na tvoj telefon periodično poroča o vrednostih izgube, izkoriščenosti GPE in porabi diska. Če se izvajanje zatakne ali pride do skoka v porabi VRAM, to izveš takoj, ne da bi moral biti fizično prisoten pri napravi.

3. **IOT z lokalnim VLM**: Usmeri kamero proti vhodnim vratom, zaženi vizijski model na Lemonade in naj OpenClaw analizira posnetke na zahtevo ali ob sprožilcu. Vprašaj "ali je danes prispel kakšen paket?" s telefona in dobi neposreden odgovor iz svoje lastne strojne opreme.

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