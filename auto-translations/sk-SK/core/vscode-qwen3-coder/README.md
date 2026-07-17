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

## Prehľad

Kódovacie agenty sú výkonné nástroje, ktoré umožňujú vývojárom spolupracovať s AI agentmi podporovanými veľkými jazykovými modelmi (LLM). Môžu byť integrované priamo do vývojového prostredia, napríklad do terminálu alebo VS Code, čo umožňuje bezproblémové začlenenie do pracovného postupu vývojára.

Tento návod ukazuje, ako používať Cline, VS Code a LM Studio na spustenie kódovacieho agenta úplne na vašom lokálnom počítači.

## Čo sa naučíte

* Ako spustiť VS Code s kódovacím agentom Cline na pomoc pri úlohách softvérového inžinierstva.
* Ako nakonfigurovať Cline na komunikáciu s LM Studio pre lokálnu inferenciu kódovacích agentov.
* Ako používať lokálne kódovacie agenty na riešenie reálnych úloh softvérového inžinierstva.

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

Na obsluhu LLM, ktorý poháňa kódovacieho agenta, použijeme LM Studio.

- Do vyhľadávacieho panela zadajte `LM Studio` a spustite aplikáciu. Zobrazí sa vám nasledujúca stránka.

![Úvodná obrazovka LM Studio](assets/initial-lm-studio.png)

Ďalej musíme načítať LLM do systému. Použijeme model `Qwen3-Coder-30B-A3B` s veľkou dĺžkou kontextu. (Ak ste ho ešte nenainštalovali, použite kartu Model na jeho inštaláciu).
- Kliknite na vyhľadávací panel v hornej časti okna LM Studio alebo stlačte `CTRL+L`. Kliknite na prepínač `Manually choose model load parameters` a potom kliknite na model Qwen3-Coder-30B-A3B.
- Zmeňte dĺžku kontextu z `4096` na `32768` a uistite sa, že `GPU Offload` je nastavený na maximum. Potom kliknite na `Load Model`.

![Výber modelu](assets/model-list-zoomed.png)

Používame veľkú dĺžku kontextu, aby agent mohol spracovávať rozsiahle kódové základne a pamätať si vykonané zmeny.

![Konfigurácia modelu](assets/selecting-model-zoomed.png)

Ďalej musíme povoliť server LM Studio.
- Kliknite na kartu Developer alebo stlačte `CTRL+2` v LM Studio na ľavej strane.
- Skontrolujte stavový prepínač a uistite sa, že je nastavený na `Running`.

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

## Spustenie a konfigurácia VS Code

Nainštalujeme rozšírenie Cline vo VS Code a prepojíme ho so serverom LM Studio, ktorý sme práve vytvorili.
- Do vyhľadávacieho panela zadajte `VS Code` a spustite aplikáciu.
- Kliknite na ikonu `Extensions` v ľavom stĺpci VS Code a vyhľadajte `Cline`. Potom kliknite na tlačidlo `Install`.

![Inštalácia rozšírenia Cline](assets/installing-cline-vscode-extension.png)

- Na ľavej strane by mala byť prítomná ikona Cline. Kliknite na ňu, aby ste otvorili Cline. Zobrazí sa okno s otázkou `How will you use Cline?` Keďže budeme používať lokálny LLM spustený cez LM Studio, vyberte `Bring my own API Key` a kliknite na `Continue`.

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

>**Tip**: Môžu byť dostupné novšie modely. Ak chcete, zvážte stiahnutie a prepnutie na modely Qwen3.6.


![Konfigurácia modelu](assets/cline-model-configuration-zoomed.png)

## Vytvorenie vášho prvého projektu

Použijeme nášho lokálneho agenta na vytvorenie webovej stránky! Otvorte VSCode v ľubovoľnom adresári, kde Cline vytvorí súbory.
- Ak to chcete urobiť, prejdite na `File -> Open Folder` v ľavom hornom rohu VS Code a vyberte priečinok, napríklad `Documents`.

![Prázdny priečinok VS Code](assets/open-cline-test.png)

Teraz sme pripravení zadať pokyn lokálnemu kódovaciemu agentovi.
- Kliknite na rozšírenie Cline v ľavom stĺpci a zadajte výzvu na spustenie agenta. Ako príklad použijeme nasledujúcu výzvu:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent potom začne vytvárať súbory podľa výzvy. Ako používateľ môžete sledovať generovanie kódu vo VS Code, ako je znázornené nižšie. Možno budete musieť kliknúť na `Save` zakaždým, keď Cline chce vytvoriť súbor.

![Generovanie kódu v Cline](assets/cline-code-generation.png)

Po vygenerovaní softvéru je agent hotový a môžete spustiť aplikáciu. V tomto prípade agent zapísal do troch súborov: `index.html`, `script.js` a `styles.css`. Jednoduchým dvojitým kliknutím na súbor HTML môžeme načítať a interagovať s vygenerovanou webovou stránkou.

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

## Ďalšie kroky

Po vygenerovaní webovej stránky môžete pokračovať v práci s Cline na jej vylepšení. Dve možné vylepšenia sú:

- **Dokumentácia**: Na vygenerovanie súboru `README.md`, ktorý dokumentuje webovú stránku, stačí agentovi zadať výzvu `Add a README`.
- **Animácia**: Zadajte modelu výzvu `Add an animation that visually represents a large language model running on a laptop.` na pridanie animácie na webovú stránku.

Odporúčame čitateľovi skúsiť generovať ďalšie aplikácie pomocou tohto nastavenia. Nižšie sú uvedené niektoré zábavné príklady, ktoré sme vyskúšali:

- **Retro arkádové hry**: Vyskúšajte ďalšie výzvy. Môže byť tiež zábavné nechať agenta vytvárať retro hry v Pythone pomocou balíka `PyGame` s nasledujúcou výzvou:

```code
Create a simple pong game using the PyGame python package.
```

- **Analýza dát**: Jednou z oblastí, kde sú kódovacie agenty obzvlášť užitočné, je skriptovanie a analýza dát. Toto je výzva na ukázanie schopnosti lokálneho modelu generovať softvér na analýzu dát pre vizualizáciu cien akcií:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Zdroje

Nižšie sú uvedené niektoré ďalšie zdroje, kde sa môžete dozvedieť viac o kódovacích agentoch, Cline a spúšťaní pracovných záťaží na

* Viac informácií o partnerstve a integrácii AMD LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD s návodom na spustenie Cline na AMD Ryzen™ AI a Radeon™ Graphics Cards: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline o spúšťaní kódovacích agentov lokálne na AI PC: https://cline.bot/blog/local-models-amd