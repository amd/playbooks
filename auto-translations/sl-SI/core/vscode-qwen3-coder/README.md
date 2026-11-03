<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ta vodnik zahteva vsaj **32 GB** sistemskega pomnilnika.
<!-- @device:end -->

## Pregled

Kodirni agenti so zmogljiva orodja, ki razvijalcem omogočajo sodelovanje z AI agenti, podprtimi z velikimi jezikovnimi modeli (LLM). Vgraditi jih je mogoče v razvojno okolje, na primer v terminal ali VS Code, kar omogoča nemoteno vključitev v razvijalčev delovni proces.

Ta vadnica prikazuje, kako z orodji Cline, VS Code in LM Studio zaženete kodirnega agenta v celoti na lokalnem računalniku.

## Kaj se boste naučili

* Kako zagnati VS Code s kodirnim agentom Cline za pomoč pri nalogah programskega inženirstva.
* Kako konfigurirati Cline za komunikacijo z LM Studio za lokalno sklepanje kodirnih agentov.
* Kako uporabiti lokalne kodirne agente za reševanje resničnih nalog programskega inženirstva. 

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtev programske opreme

<!-- @require:lmstudio,vscode -->

## Zagon in konfiguracija LM Studio

LM Studio bomo uporabili za strežbo LLM, ki poganja kodirnega agenta.

- V iskalno vrstico vnesite `LM Studio` in zaženite aplikacijo. Prikazala se vam bo naslednja stran.

![Začetni zaslon LM Studio](assets/initial-lm-studio.png)

Nato moramo naložiti LLM v sistem. Uporabili bomo model `Qwen3-Coder-30B-A3B` z veliko dolžino konteksta. (Če ga še niste namestili, ga namestite prek zavihka Model).
- Kliknite iskalno vrstico na vrhu okna LM Studio ali pritisnite `CTRL+L`. Kliknite stikalo `Manually choose model load parameters` in nato kliknite model Qwen3-Coder-30B-A3B.
- Spremenite dolžino konteksta iz `4096` na `32768` in preverite, da je `GPU Offload` nastavljen na maksimum. Nato kliknite `Load Model`

![Izbira modela](assets/model-list-zoomed.png)

Veliko dolžino konteksta uporabljamo, da lahko agent obdela velike kodne baze in si zapomni izvedene spremembe.

![Konfiguracija modela](assets/selecting-model-zoomed.png)

Nato moramo omogočiti strežnik LM Studio. 
- Kliknite zavihek Developer ali pritisnite `CTRL+2` v LM Studio na levi strani.
- Preverite preklopnik statusa in se prepričajte, da je nastavljen na `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Status strežnika](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Zagon in konfiguracija VS Code

Namestili bomo razširitev Cline v VS Code in jo povezali s strežnikom LM Studio, ki smo ga pravkar ustvarili.
- V iskalno vrstico vnesite `VS Code` in zaženite aplikacijo.
- Kliknite ikono `Extensions` na levem stolpcu VS Code in poiščite `Cline`. Nato kliknite gumb `Install`. 

![Namestitev razširitve Cline](assets/installing-cline-vscode-extension.png)

- Na levi strani bi se morala pojaviti ikona Cline. Kliknite nanjo, da odprete Cline. Pojavilo se bo okno z vprašanjem `How will you use Cline?` Ker bomo uporabljali lokalni LLM, ki teče prek LM Studio, izberite `Bring my own API Key` in kliknite `Continue`. 

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Ustvarjanje računa](assets/cline-how-will-you-use-cline-zoomed.png)

Nato moramo konfigurirati Cline za komunikacijo s strežnikom LM Studio, ki smo ga nastavili. 
- Nastavite API Provider na `LM Studio` in model na `Qwen3-Coder-30B-A3B-GGUF`. 

>**Nasvet**: Na voljo so lahko novejši modeli. Če želite, razmislite o prenosu in preklopu na modele Qwen3.6.


![Konfiguracija modela](assets/cline-model-configuration-zoomed.png)

## Ustvarjanje vašega prvega projekta

Uporabimo našega lokalnega agenta za ustvarjanje spletnega mesta! Odprite VS Code v mapi po vaši izbiri, kjer bo Cline ustvaril datoteke.
- To storite tako, da v zgornjem levem kotu VS Code izberete `File -> Open Folder` in izberete mapo, na primer `Documents`.

![Prazna mapa VS Code](assets/open-cline-test.png)

Zdaj smo pripravljeni podati poziv lokalnemu kodirnemu agentu. 
- Kliknite razširitev Cline na levem stolpcu in vnesite poziv za začetek dela agenta. Kot primer uporabimo naslednji poziv:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent bo nato začel ustvarjati datoteke v skladu s pozivom. Kot uporabnik lahko spremljate ustvarjanje kode v VS Code, kot je prikazano spodaj. Vsakič, ko želi Cline ustvariti datoteko, boste morda morali klikniti `Save`. 

![Generiranje kode s Cline](assets/cline-code-generation.png)

Po ustvarjanju programske opreme je agent zaključil delo in lahko zaženete aplikacijo. V tem primeru je agent zapisal v tri datoteke: `index.html`, `script.js` in `styles.css`. Z enostavnim dvoklikom na HTML datoteko lahko naložimo in vzajemno delujemo z ustvarjenim spletnim mestom.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Naslednji koraki

Po ustvarjanju spletnega mesta lahko nadaljujete delo s Cline za izboljšanje spletnega mesta. Dve možni izboljšavi sta:

- **Dokumentacija**: Poziv agentu z `Add a README` je vse, kar je potrebno, da agent ustvari datoteko `README.md`, ki dokumentira spletno mesto.
- **Animacija**: Pozovite model z `Add an animation that visually represents a large language model running on a laptop.`, da spletnemu mestu dodate animacijo.

Bralca spodbujamo, naj s to nastavitvijo poskusi ustvariti tudi druge aplikacije. Spodaj so nekateri zanimivi primeri, ki smo jih preizkusili:

- **Retro arkadne igre**: Preizkusite tudi druge pozive. Agentu je lahko tudi zabavno ustvariti retro igre v Pythonu z uporabo paketa `PyGame` z naslednjim pozivom:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza podatkov**: Eno od področij, kjer so kodirni agenti še posebej uporabni, je pisanje skriptov in analiza podatkov. To je poziv za prikaz sposobnosti lokalnega modela za ustvarjanje programske opreme za analizo podatkov za vizualizacijo cen delnic:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Viri

Spodaj je nekaj dodatnih virov za nadaljnje spoznavanje agentov za kodiranje, orodja Cline in izvajanje delovnih obremenitev na

* Več informacij o partnerstvu in integraciji AMD z LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD z vodenim prikazom izvajanja Cline na grafičnih karticah AMD Ryzen™ AI in Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline o lokalnem izvajanju agentov za kodiranje na AI PC-jih: https://cline.bot/blog/local-models-amd