<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tento návod vyžaduje minimálně **32GB** systémové paměti.
<!-- @device:end -->

## Přehled

Kódovací agenti jsou výkonné nástroje, které posilují vývojáře díky spolupráci s AI agenty poháněnými velkými jazykovými modely (LLM). Lze je integrovat přímo do vývojového prostředí, například do terminálu nebo VS Code, což umožňuje bezproblémové začlenění do pracovního postupu vývojáře.

Tento tutoriál ukazuje, jak pomocí Cline, VS Code a LM Studio spustit kódovacího agenta zcela lokálně na vašem počítači.

## Co se naučíte

* Jak spustit VS Code s kódovacím agentem Cline, který pomáhá při úlohách softwarového inženýrství.
* Jak nakonfigurovat Cline pro komunikaci s LM Studio za účelem lokální inference kódovacích agentů.
* Jak používat lokální kódovací agenty k řešení reálných úloh softwarového inženýrství. 

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud VS Code není nainstalován, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových požadavků

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b,lmstudio,vscode -->

## Spuštění a konfigurace LM Studio

K provozu LLM, který pohání kódovacího agenta, použijeme LM Studio.

- Do vyhledávacího pole zadejte `LM Studio` a spusťte aplikaci. Zobrazí se vám následující stránka.

![Úvodní obrazovka LM Studio](assets/initial-lm-studio.png)

Dále musíme do systému načíst LLM. Použijeme model `Qwen3-Coder-30B-A3B` s velkou délkou kontextu. (Pokud jej ještě nemáte, nainstalujte jej pomocí karty Model).
- Klikněte na vyhledávací pole v horní části okna LM Studio nebo stiskněte `CTRL+L`. Zapněte přepínač `Manually choose model load parameters` a poté klikněte na model Qwen3-Coder-30B-A3B.
- Změňte délku kontextu ze `4096` na `32768` a ujistěte se, že `GPU Offload` je nastaveno na maximum. Poté klikněte na `Load Model`

![Výběr modelu](assets/model-list-zoomed.png)

Používáme velkou délku kontextu, aby agent mohl zpracovávat rozsáhlé codebase a pamatovat si provedené změny.

![Konfigurace modelu](assets/selecting-model-zoomed.png)

Dále musíme povolit LM Studio Server. 
- Klikněte na kartu Developer nebo stiskněte `CTRL+2` v levé části LM Studio.
- Zkontrolujte přepínač stavu a ujistěte se, že je nastaven na `Running`.

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

![Stav serveru](assets/lm-studio-server-status.png)

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

## Spuštění a konfigurace VS Code

Nainstalujeme rozšíření Cline ve VS Code a propojíme jej se serverem LM Studio, který jsme právě vytvořili.
- Do vyhledávacího pole zadejte `VS Code` a spusťte aplikaci.
- Klikněte na ikonu `Extensions` v levém sloupci VS Code a vyhledejte `Cline`. Poté klikněte na tlačítko `Install`. 

![Instalace rozšíření Cline](assets/installing-cline-vscode-extension.png)

- Na levé straně by se měla objevit ikona Cline. Kliknutím na ni otevřete Cline. Zobrazí se okno s dotazem `How will you use Cline?` Jelikož budeme používat lokální LLM běžící přes LM Studio, vyberte možnost `Bring my own API Key` a klikněte na `Continue`. 

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

![Vytvoření účtu](assets/cline-how-will-you-use-cline-zoomed.png)

Dále musíme nakonfigurovat Cline tak, aby komunikoval se serverem LM Studio, který jsme nastavili. 
- Nastavte API Provider na `LM Studio` a model na `Qwen3-Coder-30B-A3B-GGUF`. 

>**Tip**: Mohou být k dispozici novější modely. Pokud chcete, zvažte stažení a přechod na modely Qwen3.6.


![Konfigurace modelu](assets/cline-model-configuration-zoomed.png)

## Vytvoření prvního projektu

Pojďme použít našeho lokálního agenta k vytvoření webové stránky! Otevřete VS Code ve vámi zvoleném adresáři, kde Cline vytvoří soubory.
- Za tímto účelem přejděte na `File -> Open Folder` v levé horní části VS Code a vyberte složku, například `Documents`.

![Prázdná složka VS Code](assets/open-cline-test.png)

Nyní jsme připraveni zadat prompt lokálnímu kódovacímu agentovi. 
- Klikněte na rozšíření Cline v levém sloupci a zadejte prompt, který agenta spustí. Jako příklad použijme následující prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent poté začne vytvářet soubory podle zadaného promptu. Jako uživatel můžete sledovat, jak se kód generuje přímo ve VS Code, jak je ukázáno níže. Může být potřeba kliknout na `Save` pokaždé, když chce Cline vytvořit soubor. 

![Generování kódu v Cline](assets/cline-code-generation.png)

Po vygenerování softwaru je úloha agenta dokončena a aplikaci můžete spustit. V tomto případě agent zapsal tři soubory: `index.html`, `script.js` a `styles.css`. Pouhým dvojklikem na HTML soubor můžeme vygenerovanou webovou stránku načíst a začít s ní pracovat.

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

## Další kroky

Po vygenerování webové stránky můžete pokračovat ve spolupráci s Cline a webovou stránku dále vylepšovat. Dvě možná vylepšení jsou:

- **Dokumentace**: Stačí agentovi zadat prompt `Add a README` a agent vygeneruje soubor `README.md`, který webovou stránku zdokumentuje.
- **Animace**: Zadejte modelu prompt `Add an animation that visually represents a large language model running on a laptop.` pro vygenerování animace na webové stránce.

Doporučujeme čtenáři, aby se pomocí tohoto nastavení pokusil vygenerovat i jiné aplikace. Níže uvádíme několik zajímavých příkladů, které jsme vyzkoušeli:

- **Retro arkádové hry**: Vyzkoušejte další prompty. Agent si také může poradit s vytvořením her ve stylu retro v Pythonu pomocí balíčku `PyGame`, a to s následujícím promptem:

```code
Create a simple pong game using the PyGame python package.
```

- **Analýza dat**: Jednou z oblastí, kde jsou kódovací agenti obzvlášť užiteční, je skriptování a analýza dat. Zde je prompt, který předvádí schopnost lokálního modelu vygenerovat software pro analýzu dat určený k vizualizaci cen akcií:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Zdroje

Níže je uvedeno několik dalších zdrojů, kde se můžete dozvědět více o Coding Agents, Cline a spouštění úloh na 

* Další informace o partnerství a integraci AMD a LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD popisující spouštění Cline na grafických kartách AMD Ryzen™ AI a Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline o spouštění coding agentů lokálně na AI PC: https://cline.bot/blog/local-models-amd