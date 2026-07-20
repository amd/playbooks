<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more prikazati. Za pravilen predogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ta priročnik zahteva vsaj **32GB** pomnilnika sistema.
<!-- @device:end -->

## Pregled

Agenti za kodiranje so zmogljiva orodja, ki razvijalcem omogočajo sodelovanje z AI agenti, podprtimi z velikimi jezikovnimi modeli (LLM). Vgradimo jih lahko v razvojno okolje, kot je terminal ali VS Code, kar omogoča nemoteno integracijo v razvijalčev delovni tok.

Ta vadnica prikazuje, kako uporabiti Cline, VS Code in LM Studio za izvajanje agenta za kodiranje v celoti na lokalnem računalniku.

## Kaj se boste naučili

* Kako zagnati VS Code z agentom za kodiranje Cline za pomoč pri nalogah programskega inženirstva.
* Kako konfigurirati Cline za komunikacijo z LM Studio za lokalno sklepanje agentov za kodiranje.
* Kako uporabljati lokalne agente za kodiranje za reševanje resničnih nalog programskega inženirstva.

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite prek Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev potrebne programske opreme

<!-- @require:lmstudio,vscode -->

## Zagon in konfiguracija LM Studio

Za posluževanje LLM, ki poganja agenta za kodiranje, bomo uporabili LM Studio.

- V iskalno vrstico vnesite `LM Studio` in zaženite aplikacijo. Prikazala se vam bo naslednja stran.

![Začetni zaslon LM Studio](assets/initial-lm-studio.png)

Nato moramo v sistem naložiti LLM. Uporabili bomo model `Qwen3-Coder-30B-A3B` z veliko dolžino konteksta. (Če ga še niste namestili, ga namestite prek zavihka Model.)
- Kliknite na iskalno vrstico na vrhu okna LM Studio ali pritisnite `CTRL+L`. Kliknite stikalo `Manually choose model load parameters` in nato kliknite na model Qwen3-Coder-30B-A3B.
- Spremenite dolžino konteksta iz `4096` na `32768` in se prepričajte, da je `GPU Offload` nastavljen na maksimum. Nato kliknite `Load Model`

![Izbira modela](assets/model-list-zoomed.png)

Uporabimo veliko dolžino konteksta, da lahko agent obdela velike kodne baze in si zapomni izvedene spremembe.

![Konfiguracija modela](assets/selecting-model-zoomed.png)

Nato moramo omogočiti LM Studio strežnik.
- Kliknite zavihek Developer ali pritisnite `CTRL+2` v LM Studio na levi strani.
- Preverite stikalo statusa in se prepričajte, da je nastavljeno na `Running`.

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Zagon in konfiguracija VS Code

Namestili bomo razširitev Cline v VS Code in jo povezali s strežnikom LM Studio, ki smo ga pravkar ustvarili.
- V iskalno vrstico vnesite `VS Code` in zaženite aplikacijo.
- Kliknite ikono `Extensions` na levem stolpcu VS Code in poiščite `Cline`. Nato kliknite gumb `Install`.

![Nameščanje razširitve Cline](assets/installing-cline-vscode-extension.png)

- Na levi strani bi se morala pojaviti ikona Cline. Kliknite nanjo, da odprete Cline. Odprlo se bo okno z vprašanjem `How will you use Cline?` Ker bomo uporabljali lokalni LLM, ki teče prek LM Studio, izberite `Bring my own API Key` in kliknite `Continue`.

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

Uporabimo naš lokalni agent za ustvarjanje spletne strani! Odprite VSCode v mapi po vaši izbiri, kjer bo Cline ustvaril datoteke.
- To storite tako, da v zgornjem levem kotu VS Code izberete `File -> Open Folder` in izberete mapo, na primer `Documents`.

![Prazna mapa VS Code](assets/open-cline-test.png)

Zdaj smo pripravljeni podati poziv lokalnemu agentu za kodiranje.
- Kliknite na razširitev Cline na levem stolpcu in vnesite poziv za zagon agenta. Kot primer uporabimo naslednji poziv:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent bo nato začel ustvarjati datoteke v skladu s pozivom. Kot uporabnik lahko spremljate ustvarjanje kode v VS Code, kot je prikazano spodaj. Vsakič, ko želi Cline ustvariti datoteko, boste morda morali klikniti `Save`.

![Ustvarjanje kode s Cline](assets/cline-code-generation.png)

Po ustvarjanju programske opreme je delo agenta zaključeno in aplikacijo lahko poženete. V tem primeru je agent zapisal tri datoteke: `index.html`, `script.js` in `styles.css`. Z dvoklikom na HTML datoteko lahko naložimo in uporabljamo ustvarjeno spletno stran.

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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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

Po ustvarjanju spletne strani lahko z orodjem Cline nadaljujete z izboljševanjem spletne strani. Dve možni izboljšavi sta:

- **Dokumentacija**: Za to, da agent ustvari datoteko `README.md`, ki dokumentira spletno stran, zadostuje, da mu podate poziv `Add a README`.
- **Animacija**: Modelu podajte poziv `Add an animation that visually represents a large language model running on a laptop.`, da ustvari animacijo za spletno stran.

Bralca spodbujamo, naj s to nastavitvijo poskusi ustvariti tudi druge aplikacije. Spodaj je nekaj zanimivih primerov, ki smo jih preizkusili:

- **Retro igre za igralne avtomate**: Preizkusite tudi druge pozive. Zabavno je lahko tudi, če agent v Pythonu z uporabo paketa `PyGame` ustvari igre v retro slogu, in sicer z naslednjim pozivom:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza podatkov**: Eno od področij, kjer so agenti za kodiranje še posebej uporabni, je pisanje skript in analiza podatkov. To je poziv za prikaz zmožnosti lokalnega modela za ustvarjanje programske opreme za analizo podatkov za vizualizacijo cen delnic:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Viri

Spodaj je nekaj dodatnih virov, kjer lahko izveste več o agentih za kodiranje, orodju Cline in izvajanju delovnih obremenitev na 

* Več informacij o partnerstvu in integraciji med AMD in LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog podjetja AMD, ki vodi skozi izvajanje orodja Cline na grafičnih karticah AMD Ryzen™ AI in Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog podjetja Cline o lokalnem izvajanju agentov za kodiranje na računalnikih AI PC: https://cline.bot/blog/local-models-amd