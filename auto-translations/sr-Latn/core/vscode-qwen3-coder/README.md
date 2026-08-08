<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ovaj vodič zahteva minimum **32GB** sistemske memorije.
<!-- @device:end -->

## Pregled

Agenti za programiranje su moćni alati koji osnažuju programere kroz saradnju sa AI agentima koje pokreću veliki jezički modeli (LLM). Mogu se ugraditi u razvojno okruženje, kao što je terminal ili VS Code, omogućavajući besprekornu integraciju u tok rada programera.

Ovaj vodič prikazuje kako da koristite Cline, VS Code i LM Studio za pokretanje agenta za programiranje u potpunosti na vašem lokalnom računaru.

## Šta ćete naučiti

* Kako da pokrenete VS Code sa Cline agentom za programiranje kako biste pomogli u zadacima softverskog inženjeringa.
* Kako da konfigurišete Cline za komunikaciju sa LM Studio radi lokalnog izvođenja zaključivanja za agente za programiranje.
* Kako da koristite lokalne agente za programiranje za rešavanje stvarnih zadataka softverskog inženjeringa.

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati pomoću Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje preduslova za softver

<!-- @require:lmstudio,vscode -->

## Pokretanje i konfigurisanje LM Studio

Koristićemo LM Studio za posluživanje LLM-a koji pokreće agenta za programiranje.

- U traci za pretragu, pretražite `LM Studio` i pokrenite aplikaciju. Dočekaće vas sledeća stranica.

![Početni ekran LM Studio](assets/initial-lm-studio.png)

Zatim, moramo učitati LLM na sistemu. Koristićemo model `Qwen3-Coder-30B-A3B` sa velikom dužinom konteksta. (Koristite karticu Model da ga instalirate ako to već niste uradili).
- Kliknite na traku za pretragu na vrhu prozora LM Studio ili pritisnite `CTRL+L`. Kliknite prekidač `Manually choose model load parameters`, a zatim kliknite na model Qwen3-Coder-30B-A3B.
- Promenite dužinu konteksta sa `4096` na `32768` i uverite se da je `GPU Offload` na maksimumu. Zatim kliknite `Load Model`

![Izbor modela](assets/model-list-zoomed.png)

Koristimo veliku dužinu konteksta kako bi agent mogao da obrađuje velike baze koda i pamti napravljene izmene.

![Konfigurisanje modela](assets/selecting-model-zoomed.png)

Zatim, moramo omogućiti LM Studio Server.
- Kliknite na karticu Developer ili pritisnite `CTRL+2` u LM Studio na levoj strani.
- Proverite prekidač statusa i uverite se da je postavljen na `Running`.

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

![Status servera](assets/lm-studio-server-status.png)

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

## Pokretanje i konfigurisanje VS Code

Instaliraćemo Cline ekstenziju u VS Code i povezati je sa LM Studio serverom koji smo upravo napravili.
- U traci za pretragu, pretražite `VS Code` i pokrenite aplikaciju.
- Kliknite na ikonu `Extensions` u levoj koloni VS Code i pretražite `Cline`. Zatim kliknite dugme `Install`.

![Instaliranje Cline ekstenzije](assets/installing-cline-vscode-extension.png)

- Ikona Cline bi trebalo da bude prisutna sa leve strane. Kliknite na nju da otvorite Cline. Pojaviće se prozor sa pitanjem `How will you use Cline?` Pošto ćemo koristiti lokalni LLM koji se pokreće preko LM Studio, izaberite `Bring my own API Key` i kliknite `Continue`.

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

![Kreiranje naloga](assets/cline-how-will-you-use-cline-zoomed.png)

Zatim, potrebno je da konfigurišemo Cline za komunikaciju sa LM Studio serverom koji smo podesili.
- Postavite API Provider na `LM Studio`, a model na `Qwen3-Coder-30B-A3B-GGUF`.

>**Savet**: Noviji modeli mogu biti dostupni. Razmislite o preuzimanju i prelasku na Qwen3.6 modele ako želite.


![Konfiguracija modela](assets/cline-model-configuration-zoomed.png)

## Kreiranje vašeg prvog projekta

Iskoristimo našeg lokalnog agenta da napravimo veb-sajt! Otvorite VSCode u direktorijumu po vašem izboru u kojem će Cline kreirati fajlove.
- Da biste to uradili, idite na `File -> Open Folder` u gornjem levom uglu VS Code i izaberite folder poput `Documents`.

![Prazan folder u VS Code](assets/open-cline-test.png)

Sada smo spremni da damo instrukciju lokalnom agentu za programiranje.
- Kliknite na Cline ekstenziju u levoj koloni i unesite instrukciju da pokrenete agenta. Kao primer, iskoristimo sledeću instrukciju:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent će zatim početi da kreira fajlove u skladu sa instrukcijom. Kao korisnik, možete pratiti kako se kod generiše u VS Code, kao što je prikazano ispod. Možda ćete morati da kliknete `Save` svaki put kada Cline želi da kreira fajl.

![Generisanje koda pomoću Cline](assets/cline-code-generation.png)

Nakon generisanja softvera, agent je završio i možete pokrenuti aplikaciju. U ovom slučaju, agent je napisao u tri fajla: `index.html`, `script.js` i `styles.css`. Jednostavnim dvoklikom na HTML fajl možemo učitati i interagovati sa generisanim veb-sajtom.

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
## Sledeći koraci

Nakon generisanja sajta, možete nastaviti da radite sa Cline-om kako biste unapredili sajt. Dva moguća unapređenja su:

- **Dokumentacija**: Dovoljno je da agentu zadate `Add a README` da bi agent generisao fajl `README.md` koji dokumentuje sajt.
- **Animacija**: Zadajte modelu `Add an animation that visually represents a large language model running on a laptop.` da biste generisali animaciju za sajt.

Podstičemo čitaoca da pokuša da generiše i druge aplikacije koristeći ovu postavku. Ispod su neki zanimljivi primeri koje smo isprobali:

- **Retro arkadne igre**: Isprobajte i druge upite. Agentu takođe može biti zabavno da kreira igre u retro stilu u Python-u koristeći paket `PyGame` uz sledeći upit:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza podataka**: Jedna oblast u kojoj su agenti za kodiranje posebno korisni jeste pisanje skripti i analiza podataka. Ovo je upit koji demonstrira sposobnost lokalnog modela da generiše softver za analizu podataka za vizuelizaciju cena akcija:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resursi

Ispod su dodatni resursi za više informacija o agentima za kodiranje, Cline-u i pokretanju radnih opterećenja na 

* Više informacija o AMD LM Studio partnerstvu i integraciji: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD blog koji provodi kroz pokretanje Cline-a na AMD Ryzen™ AI i Radeon™ grafičkim karticama: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline blog o pokretanju agenata za kodiranje lokalno na AI PC računarima: https://cline.bot/blog/local-models-amd