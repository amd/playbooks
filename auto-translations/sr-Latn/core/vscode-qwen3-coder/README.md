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

Agenti za kodiranje su moćni alati koji osnažuju programere kroz saradnju sa AI agentima zasnovanim na velikim jezičkim modelima (LLM-ovima). Mogu biti ugrađeni u razvojno okruženje, kao što su terminal ili VS Code, omogućavajući nesmetanu integraciju u tok rada programera.

Ovaj vodič pokazuje kako da koristite Cline, VS Code i LM Studio za pokretanje agenta za kodiranje potpuno na vašem lokalnom računaru.

## Šta ćete naučiti

* Kako da pokrenete VS Code sa Cline agentom za kodiranje kako biste pomogli u zadacima softverskog inženjeringa.
* Kako da konfigurišete Cline da komunicira sa LM Studio-om za lokalno zaključivanje agenata za kodiranje.
* Kako da koristite lokalne agente za kodiranje za rešavanje stvarnih zadataka softverskog inženjeringa.

<!-- @device:halo_box,halo,stx,krk -->
## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center-a.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje preduslova za softver

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b -->

## Pokretanje i konfigurisanje LM Studio-a

Koristićemo LM Studio za posluživanje LLM-a koji pokreće agenta za kodiranje.

- U traci za pretragu potražite `LM Studio` i pokrenite aplikaciju. Dočekaće vas sledeća stranica.

![Početni ekran LM Studio-a](assets/initial-lm-studio.png)

Zatim moramo da učitamo LLM na sistem. Koristićemo model `Qwen3-Coder-30B-A3B` sa velikom dužinom konteksta. (Koristite karticu Model da ga instalirate ako to već niste uradili).
- Kliknite na traku za pretragu na vrhu prozora LM Studio-a ili pritisnite `CTRL+L`. Kliknite na prekidač `Manually choose model load parameters`, a zatim kliknite na model Qwen3-Coder-30B-A3B.
- Promenite dužinu konteksta sa `4096` na `32768` i proverite da li je `GPU Offload` postavljen na maksimum. Zatim kliknite `Load Model`

![Izbor modela](assets/model-list-zoomed.png)

Koristimo veliku dužinu konteksta kako bi agent mogao da obradi velike kodne baze i pamti izmene koje su napravljene.

![Konfigurisanje modela](assets/selecting-model-zoomed.png)

Zatim je potrebno da omogućimo LM Studio Server.
- Kliknite na karticu Developer ili pritisnite `CTRL+2` u LM Studio-u na levoj strani.
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

## Pokretanje i konfigurisanje VS Code-a

Instaliraćemo ekstenziju Cline u VS Code i povezati je sa LM Studio serverom koji smo upravo napravili.
- U traci za pretragu potražite `VS Code` i pokrenite aplikaciju.
- Kliknite na ikonicu `Extensions` u levoj koloni VS Code-a i potražite `Cline`. Zatim kliknite na dugme `Install`.

![Instaliranje ekstenzije Cline](assets/installing-cline-vscode-extension.png)

- Ikonica Cline bi trebalo da bude prisutna na levoj strani. Kliknite na nju da otvorite Cline. Pojaviće se prozor sa pitanjem `How will you use Cline?` Pošto ćemo koristiti lokalni LLM koji radi preko LM Studio-a, izaberite `Bring my own API Key` i pritisnite `Continue`.

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

Zatim je potrebno da konfigurišemo Cline da komunicira sa LM Studio serverom koji smo podesili.
- Postavite API Provider na `LM Studio`, a model na `Qwen3-Coder-30B-A3B-GGUF`.

>**Savet**: Mogu biti dostupni noviji modeli. Razmotrite preuzimanje i prelazak na Qwen3.6 modele ako želite.


![Konfiguracija modela](assets/cline-model-configuration-zoomed.png)

## Kreiranje vašeg prvog projekta

Hajde da upotrebimo našeg lokalnog agenta da napravimo veb-sajt! Otvorite VSCode u direktorijumu po vašem izboru gde će Cline kreirati fajlove.
- Da biste to uradili, idite na `File -> Open Folder` u gornjem levom uglu VS Code-a i izaberite fasciklu poput `Documents`.

![Prazna fascikla u VS Code-u](assets/open-cline-test.png)

Sada smo spremni da pošaljemo upit lokalnom agentu za kodiranje.
- Kliknite na ekstenziju Cline u levoj koloni i unesite upit da pokrenete agenta. Kao primer, upotrebimo sledeći upit:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent će zatim početi da kreira fajlove na osnovu upita. Kao korisnik, možete pratiti kako se kod generiše u VS Code-u kao što je prikazano ispod. Možda ćete morati da kliknete `Save` svaki put kada Cline želi da kreira fajl.

![Generisanje koda u Cline-u](assets/cline-code-generation.png)

Nakon generisanja softvera, agent je završio sa radom i možete pokrenuti aplikaciju. U ovom slučaju, agent je napisao tri fajla: `index.html`, `script.js` i `styles.css`. Jednostavnim duplim klikom na HTML fajl možemo učitati i komunicirati sa generisanim veb-sajtom.

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

Nakon generisanja veb-sajta, možete nastaviti da radite sa Cline-om kako biste poboljšali veb-sajt. Dva moguća poboljšanja su:

- **Dokumentacija**: Slanje upita agentu sa `Add a README` je sve što je potrebno da agent generiše fajl `README.md` koji dokumentuje veb-sajt.
- **Animacija**: Pošaljite upit modelu `Add an animation that visually represents a large language model running on a laptop.` da biste generisali animaciju za veb-sajt.

Podstičemo čitaoca da pokuša da generiše druge aplikacije koristeći ovo podešavanje. Ispod su neki zabavni primeri koje smo isprobali:

- **Retro arkadne igre**: Probajte neke druge upite. Takođe može biti zabavno da agent kreira igre u retro stilu u Python-u koristeći paket `PyGame` sa sledećim upitom:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza podataka**: Jedna od oblasti u kojoj su agenti za kodiranje posebno korisni jeste skriptovanje i analiza podataka. Ovo je upit koji prikazuje sposobnost lokalnog modela da generiše softver za analizu podataka za vizualizaciju cena akcija:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resursi

U nastavku su dodatni resursi za učenje o Coding Agents, Cline-u i pokretanju radnih opterećenja na

* Više informacija o AMD LM Studio partnerstvu i integraciji: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Blog koji prikazuje pokretanje Cline-a na AMD Ryzen™ AI i Radeon™ grafičkim karticama: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline Blog o pokretanju coding agenata lokalno na AI PC računarima: https://cline.bot/blog/local-models-amd