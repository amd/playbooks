<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## Pregled

Agenti za kodiranje su moćni alati koji osnažuju programere kroz saradnju sa AI agentima podržanim velikim jezičkim modelima (LLM). Mogu biti ugrađeni u razvojno okruženje, kao što su terminal ili VS Code, omogućavajući besprekorno integrisanje u tok rada programera.

Ovaj tutorijal demonstrira kako koristiti Cline, VS Code i LM Studio za pokretanje agenta za kodiranje u potpunosti na lokalnoj mašini.

## Šta ćete naučiti

* Kako pokrenuti VS Code sa Cline agentom za kodiranje radi pomoći u zadacima softverskog inženjeringa.
* Kako konfigurisati Cline da komunicira sa LM Studio za lokalno izvođenje agenata za kodiranje.
* Kako koristiti lokalne agente za kodiranje za rešavanje stvarnih zadataka softverskog inženjeringa.

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite softverska ažuriranja
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

<!-- @require:lmstudio,vscode -->

## Pokretanje i konfiguracija LM Studio

Koristićemo LM Studio za posluživanje LLM-a koji pokreće agenta za kodiranje.

- U traci za pretragu, potražite `LM Studio` i pokrenite aplikaciju. Dočekaće vas sledeća stranica.

![LM Studio početni ekran](assets/initial-lm-studio.png)

Zatim, moramo učitati LLM na sistem. Koristićemo model `Qwen3-Coder-30B-A3B` sa velikim kontekstnim prozorom. (Koristite karticu Model da ga instalirate ako to već niste uradili).
- Kliknite na traku za pretragu na vrhu prozora LM Studio ili pritisnite `CTRL+L`. Kliknite na prekidač `Manually choose model load parameters`, a zatim kliknite na model Qwen3-Coder-30B-A3B.
- Promenite dužinu konteksta sa `4096` na `32768` i proverite da je `GPU Offload` na maksimumu. Zatim kliknite `Load Model`.

![Izbor modela](assets/model-list-zoomed.png)

Koristimo veliki kontekstni prozor kako bi agent mogao da obrađuje velike baze koda i pamti promene koje su napravljene.

![Konfiguracija modela](assets/selecting-model-zoomed.png)

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

## Pokretanje i konfiguracija VS Code

Instaliraćemo Cline ekstenziju u VS Code i povezati je sa LM Studio serverom koji smo upravo napravili.
- U traci za pretragu, potražite `VS Code` i pokrenite aplikaciju.
- Kliknite na ikonu `Extensions` u levoj koloni VS Code i potražite `Cline`. Zatim kliknite dugme `Install`.

![Instalacija Cline ekstenzije](assets/installing-cline-vscode-extension.png)

- Ikona Cline trebalo bi da bude prisutna na levoj strani. Kliknite na nju da otvorite Cline. Pojaviće se prozor sa pitanjem `How will you use Cline?` Pošto ćemo koristiti lokalni LLM koji se pokreće putem LM Studio, izaberite `Bring my own API Key` i kliknite `Continue`.

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

Zatim, moramo konfigurisati Cline da komunicira sa LM Studio serverom koji smo podesili.
- Postavite API Provider na `LM Studio` i model na `Qwen3-Coder-30B-A3B-GGUF`.

>**Savet**: Noviji modeli mogu biti dostupni. Razmotrite preuzimanje i prelazak na Qwen3.6 modele ako to želite.


![Konfiguracija modela](assets/cline-model-configuration-zoomed.png)

## Kreiranje prvog projekta

Hajde da koristimo naš lokalni agent za kreiranje veb sajta! Otvorite VSCode u direktorijumu po vašem izboru gde će Cline kreirati fajlove.
- Da biste to uradili, idite na `File -> Open Folder` u gornjem levom uglu VS Code i izaberite fasciklu kao što je `Documents`.

![VS Code prazna fascikla](assets/open-cline-test.png)

Sada smo spremni da zadamo upit lokalnom agentu za kodiranje.
- Kliknite na Cline ekstenziju u levoj koloni i unesite upit za pokretanje agenta. Kao primer, koristimo sledeći upit:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent će zatim početi da kreira fajlove prema upitu. Kao korisnik, možete pratiti kako se kod generiše u VS Code kao što je prikazano ispod. Možda ćete morati da kliknete `Save` svaki put kada Cline želi da kreira fajl.

![Cline generisanje koda](assets/cline-code-generation.png)

Nakon generisanja softvera, agent završava rad i možete pokrenuti aplikaciju. U ovom slučaju, agent je pisao u tri fajla: `index.html`, `script.js` i `styles.css`. Jednostavnim dvostrukim klikom na HTML fajl možemo učitati i interagovati sa generisanim veb sajtom.

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

## Sledeći koraci

Nakon generisanja veb sajta, možete nastaviti da radite sa Cline kako biste poboljšali veb sajt. Dva moguća poboljšanja su:

- **Dokumentacija**: Zadavanje upita agentu sa `Add a README` je sve što je potrebno da agent generiše `README.md` fajl koji dokumentuje veb sajt.
- **Animacija**: Zadajte modelu upit `Add an animation that visually represents a large language model running on a laptop.` da biste generisali animaciju za veb sajt.

Podsticemo čitaoca da pokuša da generiše druge aplikacije koristeći ovo podešavanje. Ispod su neki zabavni primeri koje smo isprobali:

- **Retro arkadne igre**: Isprobajte neke druge upite. Može biti zabavno da agent kreira igre u retro stilu u Python-u koristeći paket `PyGame` sa sledećim upitom:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza podataka**: Jedna oblast gde su agenti za kodiranje posebno korisni jeste oblast skriptovanja i analize podataka. Ovo je upit koji prikazuje sposobnost lokalnog modela da generiše softver za analizu podataka za vizualizaciju cena akcija:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resursi

Ispod su neki dodatni resursi za više informacija o agentima za kodiranje, Cline i pokretanju radnih opterećenja na

* Više informacija o AMD LM Studio partnerstvu i integraciji: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD blog koji prolazi kroz pokretanje Cline na AMD Ryzen™ AI i Radeon™ grafičkim karticama: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline blog o pokretanju agenata za kodiranje lokalno na AI računarima: https://cline.bot/blog/local-models-amd