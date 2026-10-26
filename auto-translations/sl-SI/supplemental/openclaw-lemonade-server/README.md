<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Zaženite OpenClaw z Lemonade Server kot zaledjem

## Pregled

[**OpenClaw**](https://openclaw.ai/) je avtonomni AI agent, ki lahko piše in izvaja kodo, upravlja datoteke ter izvaja zapletene večstopenjske naloge v vašem imenu. Za razliko od klepetalnega pomočnika, ki le odgovarja na vprašanja, OpenClaw na vašem sistemu izvaja dejanska dejanja, kar pomeni, da potrebuje hitro in zmogljivo AI zaledje, ki lahko sledi zahtevni agentski zanki.

[**Lemonade Server**](https://lemonade-server.ai/) je prav to zaledje. Gre za odprtokodni lokalni strežnik za sklepanje, ki zažene GenAI modele neposredno na vaši strojni opremi in jih izpostavi prek standardnega API-ja OpenAI.

Skupaj tvorita popolnoma lokalen sklad AI agenta: Lemonade skrbi za sklepanje modela, OpenClaw pa zagotavlja agentsko zanko, ki izhode modela spremeni v dejanska dejanja.

> **Preden nadaljujete:** OpenClaw je izjemno avtonomen AI agent. Dodelitev dostopa kateremukoli AI agentu do vašega sistema lahko povzroči nepredvidljive ali nenamerne izide. Nadaljujte le, če razumete tveganja in se vam zdi sprejemljivo, da v vašem imenu deluje avtonomna programska oprema.

---

## Kaj se boste naučili

Do konca tega vodnika boste znali:

- Spoznati **Lemonade Server**
- **Namestiti OpenClaw** in ga **usmeriti na Lemonade Server** kot svoje AI zaledje.
- **Zagnati prehod OpenClaw** in potrditi, da je vaš agent pripravljen za delo.
- **Povezati komunikacijski kanal** (Discord ali Telegram), da se boste lahko s svojim agentom pogovarjali s katere koli naprave.

---

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev za programsko opremo

<!-- @os:linux -->
- Računalnik z operacijskim sistemom **Ubuntu 24.04+** ali združljivo distribucijo Linuxa, ki temelji na Debianu in uporablja `apt-get`
- Vsaj **12 GB RAM-a** (priporočeno 64 GB+ za večje modele)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (neobvezno, za peskovnik OpenClaw)
- **~10–30 GB prostega prostora na disku** za uteži modela
<!-- @os:end -->

<!-- @os:windows -->
- Računalnik z operacijskim sistemom **Windows 10/11**
- Vsaj **12 GB RAM-a** (priporočeno 64 GB+ za večje modele)
- **~10–30 GB prostega prostora na disku** za uteži modela
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (neobvezno, za peskovnik OpenClaw)
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @os:linux -->
<!-- @prereq:nodejs -->
<!-- @os:end -->
<!-- On Windows OpenClaw runs in WSL, so its Node.js is covered by the openclaw prereq. -->
<!-- @prereq:docker,openclaw,lemonade-models-qwen3-6-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Prenesite in naložite priporočeni model

Priporočeni model za ta vodnik je **Qwen3.6-35B-A3B-GGUF** podjetja Unsloth, zmogljiv model MoE z okni konteksta velikosti 263k žetonov, ki je dobro prilagojen agentskim obremenitvam. Ta model uporablja kvantizacijo UD-Q4_K_XL. Prenesite ga zdaj:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Nato ga naložite z velikim oknom konteksta in to nastavitev shranite za prihodnje zagone:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Model ima privzeto dolžino konteksta 262.144 žetonov. Če naletite na napake zaradi pomanjkanja pomnilnika (OOM), razmislite o zmanjšanju okna konteksta. Ker pa Qwen3.6 za zapletene naloge izkorišča razširjen kontekst, priporočamo ohranitev dolžine konteksta vsaj 128 tisoč žetonov, da se ohrani zmožnost razmišljanja.

> **Nasvet: onemogočite razmišljanje za hitrejše odzive agenta:** Qwen3.6-35B-A3B privzeto deluje v načinu razmišljanja, kar pred vsakim odzivom doda zakasnitev. Pri agentskih zankah se ta dodatni čas hitro nabira. Repozitorij [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) ponuja pripravljeno konfiguracijo, ki onemogoči razmišljanje. Za uporabo prenesite datoteko in jo uvozite:
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

OpenClaw zaženemo znotraj WSL (priporočeno) in ga povežemo z Lemonade, ki deluje izvorno v sistemu Windows. To vam omogoča lupino okolja Linux za OpenClaw, hkrati pa ohranja pospeševanje GPU za Lemonade na strani Windows.

### Namestitev WSL in Ubuntu

Odprite PowerShell kot skrbnik in namestite jedro WSL:

```powershell
wsl --install --no-distribution
```

Nato namestite Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Omogočite systemd v WSL

To zaženite znotraj terminala Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Zaprite WSL in ga znova zaženite:

```powershell
exit
wsl --shutdown
wsl
```

### Povežite Lemonade iz Windows v WSL

WSL2 deluje v virtualnem omrežju. Lemonade v sistemu Windows se poveže na `127.0.0.1`, do katerega WSL ne more neposredno dostopati. Prehod vrat Windows posreduje promet z IP-naslova prehoda WSL na lokalni gostitelj Windows.

**Poiščite svoj IP-naslov prehoda WSL** (zaženite znotraj WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Dodajte prehod vrat** (zaženite v PowerShell kot skrbnik, pri čemer `<WSL-Gateway-IP>` zamenjajte s svojim IP-naslovom prehoda WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Opomba: Če naletite na napako `netsh: command not found`, poskusite namesto tega uporabiti eksplicitno ime izvedljive datoteke – `netsh.exe`

**Dodajte pravilo požarnega zidu** (isti povišani PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Preverite iz WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Če ste v prejšnjem koraku že naložili model Qwen3.6-35B-A3B-GGUF, bi morali videti izhod JSON, podoben temu:

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

Pravilo `netsh portproxy` preživi ponovne zagone, vendar se lahko IP naslov prehoda WSL spremeni po `wsl --shutdown` ali ponovnem zagonu. Ko se to zgodi, proxy še vedno kaže na stari IP naslov in Lemonade postane nedosegljiv iz WSL. Če se to zgodi, uporabite eno od spodnjih možnosti.

**Možnost 1 (priporočeno) — Samodejno popravilo mostu.** Da se temu ne bi bilo treba posvečati ročno vsakič, uporabite načrtovano opravilo, ki preveri most ob vsakem zagonu in prijavi ter ga obnovi le, ko se je IP naslov prehoda spremenil. Oglejte si [vodnik za samodejno popravilo mostu Lemonade WSL](assets/RepairLemonadeWslBridge.md).

**Možnost 2 — Ročno popravilo mostu.** Najprej pridobite trenutni IP naslov prehoda WSL z zagonom tega znotraj WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Kopirajte to vrednost; uporabili jo boste namesto `<new-WSL-Gateway-IP>` spodaj.

Nato v **povišanem PowerShellu** (zagnanem kot skrbnik) izpišite obstoječa pravila, izbrišite samo zastarelo pravilo za Lemonade in dodajte novo z trenutnim IP naslovom:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

V izhodu ukaza `show all` je zastarelo pravilo za Lemonade vnos, katerega naslov za povezavo je `127.0.0.1` na vratih `13305`; njegov naslov za poslušanje je vaš `<old-WSL-Gateway-IP>`. Brisanje po tem naslovu odstrani samo to pravilo in pusti vsa druga pravila port-proxy na vašem računalniku nespremenjena.

Pravilo požarnega zidu, ki ste ga dodali med namestitvijo, je vezano na vrata `13305` (ne na IP naslov), zato še naprej deluje in ga ni treba ponovno ustvariti.

> **Priporočilo:** Da se izognete težavam s prehodom, močno priporočamo naslednjo konfiguracijo lupine:
> - **Ukazi za Windows** naj se izvajajo v **PowerShellu**
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

### Namestitev OpenClaw
<!-- @os:windows -->
> Zaženite ukaze iz tega razdelka znotraj svojega **terminala WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Zastavica `--no-onboard` preskoči interaktivnega čarovnika za nastavitev; zaledje modela boste ročno konfigurirali v naslednjem koraku, kar vam omogoča natančen nadzor nad tem, kateri model in strežnik se uporabljata.

Odprite nov terminal in potrdite namestitev:

```bash
openclaw --version
```

> **Nasvet:** Če po namestitvi vidite `command not found`, dodajte npm-ov globalni bin imenik v svojo PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Da bo to trajno, dodajte zgornjo vrstico v svojo datoteko `~/.bashrc` ali `~/.zshrc`.

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


### Konfiguracija OpenClaw za uporabo Lemonade

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

> **Dimenzioniranje kontekstnega okna OpenClaw:** Stiskanje (compaction) OpenClaw se sproži, ko `contextTokens > contextWindow − reserveTokens`. Privzeti `reserveTokensFloor` je 20.000 žetonov, kar je spodnja meja, ki prepiše `reserveTokens`, kadar je ta nižji, zato bo vsak kontekst modela pod ~37k sprožil neskončno zanko stiskanja. Nastavite nizko rezervo in enkrat onemogočite spodnjo mejo v svoji konfiguraciji, in se bo uporabila za vsak model, brez potrebe po nastavitvi za posamezen model:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` je *spodnja meja* (minimalna zaščita), ne sama rezerva; nastavitev samo spodnje meje nima učinka. `reserveTokensFloor: 0` onemogoči zaščito, tako da je nižji `reserveTokens` sprejet.
>
> **Kdaj to uporabiti:** To konfiguracijo uporabite, če je dejansko kontekstno okno vašega modela pod ~37k, bodisi ker je model majhen (npr. 8k, 16k, 32k) bodisi ker ste ga namerno omejili na nižjo vrednost (npr. nalaganje modela s 128k, vendar nastavitev konteksta na 16k v Lemonade). Brez tega OpenClaw ob zagonu zapade v neskončno zanko stiskanja.
>
> **Modeli z velikim kontekstom pri polnem kontekstu:** To lahko povsem preskočite. Privzete nastavitve delujejo dobro, stiskanje se bo sprožilo precej pred zapolnitvijo okna, model pa ima dovolj prostora za ustvarjanje dolgih odgovorov. Če to vseeno uporabite, upoštevajte, da `reserveTokens: 4096` omeji dolžino odgovora na približno 4k žetonov, kar lahko prekine ustvarjanje dolgih datotek ali podrobnih načrtov.
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
> Preostanek vaše konfiguracije (gateway, channels, models itd.) ostane nespremenjen, dodati je treba le ključ `compaction`.
### (Priporočeno) Omogočite peskovnik Docker

OpenClaw lahko vse operacije agenta z datotekami in kodo preusmeri skozi izoliran vsebnik Docker, namesto da jih izvaja neposredno na vašem gostitelju. To omeji domet morebitnega nenamernega dejanja na peskovnik, pri čemer ostaneta datotečni sistem in omrežje vašega gostitelja nedotaknjena.

Zgradite sliko peskovnika enkrat (Docker mora biti nameščen):

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

Vsebniki peskovnika privzeto **nimajo dostopa do omrežja**. Glejte [referenco za peskovnik](https://docs.openclaw.ai/gateway/sandboxing) za vezne priklope in omrežne razveljavitve.

> #### Odpravljanje težav: Docker zavrne dovoljenje (Permission Denied)
> 
> Če pri izvajanju ukazov Docker dobite "permission denied":
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
> **Korak 2: Če se napaka ponavlja, uveljavite trajno rešitev**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Nato **ponovno zaženite** sistem.
> 
> **Hitra začasna rešitev** (ponastavi se po ponovnem zagonu):
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

[Firecrawl](https://docs.firecrawl.dev/introduction) ponuja samostojno gostovano storitev za pajkanje spleta in izločanje vsebine, ki lahko obide te izzive in sprosti polni potencial avtomatizacije OpenClaw. 

V tej postavitvi se OpenClaw izvaja kot niz vsebnikov Docker, upravljanih s Podman. Za poenostavitev upravljanja življenjskega cikla in samodejnega zagona Firecrawl registriramo kot uporabniško storitev `systemd`, ki orkestrira osnovni sklad Podman Compose. To omogoča, da OpenClaw zažene prehod (gateway), ustavi in preveri storitev Firecrawl z uporabo standardnih ukazov `systemctl --user` namesto neposrednega komuniciranja z vsebniki. 

Da bi ostalo preprosto, smo celoten postopek razdelili na štiri korake:

---

### 1. Registracija sistemske storitve
Pomaknite se v uporabniški konfiguracijski imenik systemd:
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
V tej točki je storitev definirana, vendar še ni registrirana pri `systemd`. 
Prepričajte se, da se ime datoteke natančno ujema s tistim, ki ste ga ustvarili zgoraj, nato zaženite:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Če je uspešno, bi morali videti naslednji izpis:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` vsebuje simbolne povezave do storitev, ki so konfigurirane za samodejni zagon.

### 2. Konfiguracija Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) je idealen za tiste, ki potrebujejo popoln nadzor nad svojim okoljem za pajkanje in obdelavo podatkov, vendar prinaša kompromis dodatnega vzdrževanja in konfiguracijskih naporov.

Začnite s kloniranjem repozitorija:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Ustvarite datoteko `.env` v imeniku `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Uvedba OpenClaw s Podman Compose

Preden nadaljujete, se prepričajte, da ste povlekli najnovejšo sliko Docker za OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Ko je to opravljeno, prenesite datoteko Compose za OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) in jo postavite v korenski imenik `/firecrawl`:

> Ta konvencija je potrebna, da `systemd` pravilno najde in zažene storitev, kot je določeno v `WorkingDirectory=${HOME}/firecrawl`.

> Sklad lahko vedno razširite z dodajanjem dodatnih storitev Firecrawl po potrebi. Celoten seznam razpoložljivih storitev najdete v uradni datoteki [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Zagon storitve OpenClaw prek Firecrawl 

Preden predate nadzor `systemd`, preverite, da vse deluje pravilno tako, da sklad zaženete ročno:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Če je vse pravilno konfigurirano, bi morali videti, da se vsebnik OpenClaw zažene, izpis ukazne vrstice pa naj bo podoben temu:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Ko ste preverili, pred nadaljevanjem sklad ponovno zaustavite:
```bash
podman compose -f openclaw-compose.yaml down
```
Preden zaženete storitev, se morate prepričati, da sta pravilno nastavljena lastništvo in dovoljenja za imenik `firecrawl` in njegovo datoteko `.env`. 
To je ključnega pomena, da lahko storitev ob zagonu zapiše vaše poverilnice.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Zdaj, ko je vse preverjeno, zaženite storitev prek `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Dejanja OpenClaw](https://docs.openclaw.ai/) so dostopna znotraj interaktivnega vsebnika, nadzorna plošča za splet (Web Dashboard) pa je na voljo na istem gostitelju in vratih na naslovu http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Pridobivanje vašega `OPENCLAW_GATEWAY_TOKEN`

Ko je storitev vzpostavljena in deluje, boste opazili nov imenik `.openclaw`, ustvarjen v vaši domači mapi (~/.openclaw). Ta imenik je privzeto zaklenjen, zato ga boste morali odkleniti, da pridobite svoj žeton za prehod (gateway token).

1. Dodelite dostop do imenika:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Preberite svoj žeton za prehod:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Poiščite vrednost `OPENCLAW_GATEWAY_TOKEN` v izpisu.

3. Odprite nadzorno ploščo prehoda v svojem brskalniku na naslovu http://127.0.0.1:18789. Ko boste pozvani k preverjanju pristnosti, prilepite svoj žeton.

Za zaustavitev storitve zaženite:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Zaženite OpenClaw Gateway

Gateway je proces OpenClaw, ki upravlja agentno zanko in streže nadzorno ploščo:

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

Za odprtje nadzorne plošče zaženite naslednje v drugem terminalu, medtem ko gateway še vedno teče:

```bash
openclaw dashboard
```

Ker se gateway veže na loopback, se nadzorna plošča samodejno avtenticira, ko je odprta na isti napravi, za lokalni dostop ni potrebno vnašanje žetona ali odobritev naprave. Videti bi morali nadzorno ploščo OpenClaw z vašim modelom Lemonade, navedenim kot aktivni backend.

> Če ste omogočili peskovnik (sandboxing), lahko to preverite tako, da agentu iz nadzorne plošče naročite `run hostname`. Če vidite kratek ID vsebnika namesto imena gostitelja vašega računalnika, peskovnik deluje.

**Čestitamo, zgradili ste povsem lokalen sklad AI agenta iz nič.**

> **Potrebujete žeton za gateway?** Zaženite `openclaw dashboard --no-open`, da izpišete URL nadzorne plošče z vgrajenim žetonom (poskuša ga tudi kopirati v odložišče). Druga možnost je, da je žeton na voljo pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.

**Dostop do nadzorne plošče iz druge naprave (prek SSH tunela)**

Če OpenClaw teče na oddaljenem računalniku, lahko do njegove nadzorne plošče dostopate iz svojega lokalnega računalnika prek SSH tunela. Tunel posreduje vrata gatewaya (`18789`), tako da lahko vaš lokalni brskalnik komunicira z oddaljenim gatewayem prek `127.0.0.1`.

1. Z vašega **lokalnega računalnika** se enkrat povežite z oddaljenim računalnikom in sprejmite poziv za prstni odtis, da se gostitelj doda med znane gostitelje:

   ```bash
   ssh user@<host-ip>
   ```

2. Še vedno na vašem **lokalnem računalniku** odprite SSH tunel:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Opomba:** Potem ko vnesete geslo, terminal ne prikaže nobenega izpisa in se zdi, kot da je obviseli. To je pričakovano: zastavica `-N` pove SSH-ju, naj ne zažene nobenega oddaljenega ukaza, zato preprosto drži tunel odprt. Pustite ta terminal teči.

3. Na vašem **lokalnem računalniku** odprite brskalnik in pojdite na `http://127.0.0.1:18789`.

4. Na **oddaljenem računalniku** izpišite žeton gatewaya in ga prilepite v brskalnik za prijavo:

   ```bash
   openclaw dashboard --no-open
   ```

   To izpiše URL nadzorne plošče z vgrajenim žetonom; kopirajte žeton za prijavo. (Žeton je prav tako shranjen pod `gateway.auth.token` v `~/.openclaw/openclaw.json`.)

> **Odobritev oddaljene naprave:** Ko odprete nadzorno ploščo iz druge naprave ali telefona, lahko brskalnik prikaže ID zahteve. Na **oddaljenem računalniku** naštejte čakajoče zahteve:
> ```bash
> openclaw devices list
> ```
> Nato odobrite ustrezno zahtevo:
> ```bash
> openclaw devices approve <requestId>
> ```
> To je potrebno le za oddaljene ali sekundarne naprave; dostop prek loopbacka iz istega računalnika se avtenticira samodejno. Za podrobnosti glejte dokumentacijo [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Izbirno: Povežite komunikacijski kanal

Ko gateway teče, lahko do svojega lokalnega agenta dostopate iz katere koli naprave. Izberite možnost, ki ustreza vaši postavitvi. OpenClaw podpira [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) in druge kanale, celoten seznam si oglejte na [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Možnost A: Discord

Discord zahteva strežnik, na katerem imate **skrbniški dostop**, da dodate bota. Če si strežnike delite, vendar niste lastnik nobenega, uporabite Možnost B (Telegram).

#### Ustvarite Discord račun in strežnik

Če nimate Discord računa, se prijavite na [discord.com](https://discord.com). Potrebujete tudi strežnik, na katerem ste skrbnik, ustvarite ga s klikom na ikono **+** v stranski vrstici Discorda in izbiro **Create My Own**. Zasebni strežnik je dovolj.

#### Ustvarite Discord aplikacijo in bota

1. Pojdite na [Discord Developer Portal](https://discord.com/developers/applications) in kliknite **New Application**. Poimenujte jo (npr. »openclaw-bot«).
2. V stranski vrstici kliknite **Bot**. Nastavite uporabniško ime za bota.
3. Še vedno na strani Bot pomaknite se do **Privileged Gateway Intents** in omogočite:
   - **Message Content Intent** (obvezno)
   - **Server Members Intent** (priporočeno)
4. Pomaknite se nazaj navzgor in kliknite **Reset Token**, da ustvarite žeton za bota. Kopirajte ga.

#### Dodajte bota v svoj strežnik

1. V stranski vrstici kliknite **OAuth2/ URL Generator**.
2. Pod **Scopes** omogočite `bot` in `applications.commands`.
3. Pod **Bot Permissions** omogočite: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Kopirajte ustvarjeni URL, prilepite ga v brskalnik, izberite svoj strežnik in potrdite. Bot bi se moral zdaj pojaviti na seznamu članov vašega strežnika.

#### Zberite svoje ID-je

Omogočite razvijalski način v Discordu (**User Settings/ Advanced/ Developer Mode**), nato:
- Z desnim klikom na ikono strežnika: **Copy Server ID**
- Z desnim klikom na svoj avatar: **Copy User ID**

#### Dovolite zasebna sporočila od članov strežnika

Z desnim klikom na ikono strežnika/ **Privacy Settings**/ vklopite **Direct Messages**. To omogoča botu, da vam pošlje zasebno sporočilo, kar je potrebno za korak seznanjanja.

#### Konfigurirajte OpenClaw za Discord

Shranite žeton bota kot spremenljivko okolja, nato ustvarite eno samo popravno datoteko, ki omogoči Discord, se sklicuje na žeton in doda vaš strežnik na seznam dovoljenih. Zamenjajte `<server_id>` in `<user_id>` z ID-ji, zbranimi zgoraj.

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

> **Ne zanašajte se na to, da boste agenta prosili za konfiguracijo tega.** Ko je omogočen peskovnik, agent ne more pisati v `~/.openclaw/openclaw.json` iz znotraj peskovnika, namesto tega uporabite zgornje ukaze CLI na gostitelju.

Znova zaženite gateway, da prevzame novo konfiguracijo kanala:

```bash
openclaw gateway run --bind loopback --port 18789
```

V nekaj sekundah bi morali v izpisu gatewaya videti `logged in to discord as <bot-name>`.
#### Seznanite svoj Discord račun

Pošljite botu zasebno sporočilo (DM) v Discordu. Odgovoril bo s kratko kodo za seznanjanje.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Potrdite jo v napravi, ki poganja OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Kode za seznanjanje potečejo po eni uri.

Zdaj se lahko s svojim agentom pogovarjate neposredno iz Discorda in prenesete naloge na svojo lokalno strojno opremo.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Možnost B: Telegram

Telegram je za večino uporabnikov preprostejši od Discorda, saj ne zahteva strežnika ali skrbniškega dostopa.

#### Ustvarite Telegram bota

1. Odprite Telegram in pošljite sporočilo botu **@BotFather**.
2. Pošljite `/newbot` in sledite navodilom. Shranite žeton bota, ki vam ga posreduje.

#### Konfigurirajte OpenClaw za Telegram

Shranite žeton kot spremenljivko okolja:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Dodajte konfiguracijo kanala v `~/.openclaw/openclaw.json` (ali jo popravite prek nadzorne plošče):

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

Znova zaženite prehod, nato pošljite svojemu botu poljubno sporočilo v Telegramu. Potrdite seznanjanje:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Kode za seznanjanje potečejo po eni uri. Zdaj se lahko s svojim agentom pogovarjate prek zasebnih sporočil v Telegramu.

---

## Naslednji koraki

Zdaj, ko lahko vaš agent prejema ukaze s telefona in deluje na vašem lokalnem računalniku, so tu tri smeri, ki jih velja raziskati:

1. **Povzemalec dogajanja na borzi**: Nastavite OpenClaw, da v rednih intervalih pridobiva podatke iz finančnih API-jev, povzame dnevna gibanja z vašim lokalnim modelom in vsako jutro prek izbranega kanala pošlje povzetek na vaš telefon.

2. **Nadzor fine nastavitve**: Sprožite učno opravilo na daljavo prek Telegrama ali Discorda, nato naj agent sledi dnevniku učenja in vam na telefon periodično poroča vrednosti izgube, izkoriščenost GPE in zasedenost diska. Če se postopek ustavi ali pride do konice pri porabi VRAM, to takoj izveste, ne da bi morali biti pri napravi.

3. **IOT z lokalnim VLM**: Usmerite kamero na svoja vhodna vrata, zaženite vizijski model na Lemonade in naj OpenClaw analizira sličice na zahtevo ali ob sprožilcu. Vprašajte »Ali so danes prispeli kakšni paketi?« s telefona in dobite neposreden odgovor iz lastne strojne opreme.

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