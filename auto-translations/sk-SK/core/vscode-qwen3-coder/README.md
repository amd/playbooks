<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Táto príručka vyžaduje minimálne **32 GB** systémovej pamäte.
<!-- @device:end -->

## Prehľad

Kódovacie agenty sú výkonné nástroje, ktoré posilňujú vývojárov prostredníctvom spolupráce s AI agentmi poháňanými veľkými jazykovými modelmi (LLM). Dajú sa vložiť priamo do vývojového prostredia, ako je terminál alebo VS Code, čo umožňuje bezproblémovú integráciu do pracovného postupu vývojára.

Tento tutoriál demonštruje, ako pomocou Cline, VS Code a LM Studio spustiť kódovacieho agenta úplne lokálne na vašom počítači.

## Čo sa naučíte

* Ako spustiť VS Code s kódovacím agentom Cline na pomoc pri úlohách softvérového inžinierstva.
* Ako nakonfigurovať Cline na komunikáciu s LM Studio pre lokálnu inferenciu kódovacích agentov.
* Ako použiť lokálnych kódovacích agentov na riešenie reálnych softvérovo-inžinierskych úloh. 

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @require:lmstudio,vscode -->

## Spustenie a konfigurácia LM Studio

Na spustenie LLM poháňajúceho kódovacieho agenta použijeme LM Studio.

- Do vyhľadávacieho panela zadajte `LM Studio` a spustite aplikáciu. Zobrazí sa vám nasledujúca obrazovka.

![Úvodná obrazovka LM Studio](assets/initial-lm-studio.png)

Ďalej musíme do systému načítať LLM. Použijeme model `Qwen3-Coder-30B-A3B` s veľkou dĺžkou kontextu. (Ak ho ešte nemáte nainštalovaný, použite na to kartu Model).
- Kliknite na vyhľadávací panel v hornej časti okna LM Studio alebo stlačte `CTRL+L`. Zapnite prepínač `Manually choose model load parameters` a potom kliknite na model Qwen3-Coder-30B-A3B.
- Zmeňte dĺžku kontextu zo `4096` na `32768` a uistite sa, že `GPU Offload` je nastavené na maximum. Potom kliknite na `Load Model`

![Výber modelu](assets/model-list-zoomed.png)

Používame veľkú dĺžku kontextu, aby agent dokázal spracovať rozsiahle kódové bázy a pamätal si vykonané zmeny.

![Konfigurácia modelu](assets/selecting-model-zoomed.png)

Ďalej musíme povoliť LM Studio Server. 
- Kliknite na kartu Developer alebo stlačte `CTRL+2` vľavo v LM Studio.
- Skontrolujte prepínač stavu a uistite sa, že je nastavený na `Running`.

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

![Stav servera](assets/lm-studio-server-status.png)

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

## Spustenie a konfigurácia VS Code

Nainštalujeme rozšírenie Cline vo VS Code a pripojíme ho k serveru LM Studio, ktorý sme práve vytvorili.
- Do vyhľadávacieho panela zadajte `VS Code` a spustite aplikáciu.
- Kliknite na ikonu `Extensions` v ľavom stĺpci VS Code a vyhľadajte `Cline`. Potom kliknite na tlačidlo `Install`. 

![Inštalácia rozšírenia Cline](assets/installing-cline-vscode-extension.png)

- Vľavo by sa mala zobraziť ikona Cline. Kliknutím na ňu otvoríte Cline. Zobrazí sa okno s otázkou `How will you use Cline?` Keďže budeme používať lokálny LLM spustený cez LM Studio, vyberte `Bring my own API Key` a stlačte `Continue`. 

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

![Vytvorenie účtu](assets/cline-how-will-you-use-cline-zoomed.png)

Ďalej musíme nakonfigurovať Cline na komunikáciu so serverom LM Studio, ktorý sme nastavili. 
- Nastavte API Provider na `LM Studio` a model na `Qwen3-Coder-30B-A3B-GGUF`. 

>**Tip**: Môžu byť dostupné novšie modely. Ak chcete, zvážte stiahnutie a prechod na modely Qwen3.6.


![Konfigurácia modelu](assets/cline-model-configuration-zoomed.png)

## Vytvorenie vášho prvého projektu

Použime nášho lokálneho agenta na vytvorenie webovej stránky! Otvorte VS Code v adresári podľa vlastného výberu, kde Cline vytvorí súbory.
- Urobíte to tak, že kliknete na `File -> Open Folder` v ľavej hornej časti VS Code a vyberiete priečinok, napríklad `Documents`.

![Prázdny priečinok vo VS Code](assets/open-cline-test.png)

Teraz sme pripravení zadať lokálnemu kódovaciemu agentovi prompt. 
- Kliknite na rozšírenie Cline v ľavom stĺpci a zadajte prompt na spustenie agenta. Ako príklad použime nasledujúci prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent následne začne vytvárať súbory podľa promptu. Ako používateľ môžete sledovať generovanie kódu priamo vo VS Code, ako je znázornené nižšie. Zakaždým, keď Cline chce vytvoriť súbor, možno budete musieť kliknúť na `Save`. 

![Generovanie kódu pomocou Cline](assets/cline-code-generation.png)

Po vygenerovaní softvéru je práca agenta dokončená a aplikáciu môžete spustiť. V tomto prípade agent zapísal do troch súborov: `index.html`, `script.js` a `styles.css`. Jednoduchým dvojklikom na HTML súbor môžeme načítať vygenerovanú webovú stránku a interagovať s ňou.

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
## Ďalšie kroky

Po vygenerovaní webovej stránky môžete pokračovať v spolupráci s Cline na jej vylepšovaní. Dve možné vylepšenia sú:

- **Dokumentácia**: Stačí zadať agentovi prompt `Add a README` a agent vygeneruje súbor `README.md`, ktorý dokumentuje webovú stránku.
- **Animácia**: Zadajte modelu prompt `Add an animation that visually represents a large language model running on a laptop.`, aby vygeneroval animáciu pre webovú stránku.

Odporúčame čitateľovi, aby sa pokúsil vygenerovať aj iné aplikácie pomocou tohto nastavenia. Nižšie sú uvedené niektoré zaujímavé príklady, ktoré sme vyskúšali:

- **Retro arkádové hry**: Vyskúšajte aj iné prompty. Pre agenta môže byť tiež zábavné vytvoriť hry v retro štýle v jazyku Python pomocou balíka `PyGame` s nasledujúcim promptom:

```code
Create a simple pong game using the PyGame python package.
```

- **Analýza dát**: Jednou z oblastí, kde sú kódovací agenti mimoriadne užitoční, je skriptovanie a analýza dát. Tento prompt ukazuje schopnosť lokálneho modelu vygenerovať softvér na analýzu dát pre vizualizáciu cien akcií:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Zdroje

Nižšie sú uvedené ďalšie zdroje, kde sa môžete dozvedieť viac o kódovacích agentoch, Cline a spúšťaní pracovných záťaží na 

* Ďalšie informácie o partnerstve a integrácii AMD a LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD s návodom na spúšťanie Cline na grafických kartách AMD Ryzen™ AI a Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline o spúšťaní kódovacích agentov lokálne na AI PC: https://cline.bot/blog/local-models-amd