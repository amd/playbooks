<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální tagy, které GitHub nedokáže vykreslit. Pro správné zobrazení tohoto obsahu navštivte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tento playbook vyžaduje minimálně **32 GB** systémové paměti.
<!-- @device:end -->

## Přehled

Kódovací agenti jsou výkonné nástroje, které umožňují vývojářům spolupracovat s agenty AI podporovanými velkými jazykovými modely (LLM). Mohou být integrovány do vývojového prostředí, například do terminálu nebo VS Code, což umožňuje bezproblémové začlenění do pracovního postupu vývojáře.

Tento tutoriál ukazuje, jak používat Cline, VS Code a LM Studio ke spuštění kódovacího agenta zcela na vašem lokálním počítači.

## Co se naučíte

* Jak spustit VS Code s kódovacím agentem Cline pro podporu při úlohách softwarového inženýrství.
* Jak nakonfigurovat Cline pro komunikaci s LM Studio pro lokální inferenci kódovacích agentů.
* Jak používat lokální kódovací agenty k řešení reálných úloh softwarového inženýrství.

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud VS Code není nainstalováno, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @require:lmstudio,vscode -->

## Spuštění a konfigurace LM Studio

K obsluze LLM pohánějícího kódovacího agenta použijeme LM Studio.

- Do vyhledávacího pole zadejte `LM Studio` a spusťte aplikaci. Zobrazí se vám následující stránka.

![Úvodní obrazovka LM Studio](assets/initial-lm-studio.png)

Dále musíme načíst LLM do systému. Použijeme model `Qwen3-Coder-30B-A3B` s velkou délkou kontextu. (Pokud jste tak ještě neučinili, nainstalujte jej pomocí záložky Model).
- Klikněte na vyhledávací lištu v horní části okna LM Studio nebo stiskněte `CTRL+L`. Klikněte na přepínač `Manually choose model load parameters` a poté klikněte na model Qwen3-Coder-30B-A3B.
- Změňte délku kontextu z `4096` na `32768` a ujistěte se, že `GPU Offload` je nastaven na maximum. Poté klikněte na `Load Model`.

![Výběr modelu](assets/model-list-zoomed.png)

Používáme velkou délku kontextu, aby agent mohl zpracovávat rozsáhlé kódové základny a pamatovat si provedené změny.

![Konfigurace modelu](assets/selecting-model-zoomed.png)

Dále musíme povolit server LM Studio.
- Klikněte na záložku Developer nebo stiskněte `CTRL+2` v LM Studio na levé straně.
- Zkontrolujte stavový přepínač a ujistěte se, že je nastaven na `Running`.

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

## Spuštění a konfigurace VS Code

Nainstalujeme rozšíření Cline do VS Code a připojíme jej k serveru LM Studio, který jsme právě vytvořili.
- Do vyhledávacího pole zadejte `VS Code` a spusťte aplikaci.
- Klikněte na ikonu `Extensions` v levém sloupci VS Code a vyhledejte `Cline`. Poté klikněte na tlačítko `Install`.

![Instalace rozšíření Cline](assets/installing-cline-vscode-extension.png)

- Na levé straně by měla být přítomna ikona Cline. Kliknutím na ni otevřete Cline. Zobrazí se okno s dotazem `How will you use Cline?` Protože budeme používat lokální LLM spuštěný přes LM Studio, vyberte `Bring my own API Key` a klikněte na `Continue`.

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

Dále musíme nakonfigurovat Cline pro komunikaci se serverem LM Studio, který jsme nastavili.
- Nastavte poskytovatele API na `LM Studio` a model na `Qwen3-Coder-30B-A3B-GGUF`.

>**Tip**: Mohou být dostupné novější modely. Pokud chcete, zvažte stažení a přepnutí na modely Qwen3.6.


![Konfigurace modelu](assets/cline-model-configuration-zoomed.png)

## Vytvoření prvního projektu

Použijme našeho lokálního agenta k vytvoření webové stránky! Otevřete VSCode ve vámi zvoleném adresáři, kde Cline vytvoří soubory.
- Chcete-li to provést, přejděte na `File -> Open Folder` v levém horním rohu VS Code a vyberte složku, například `Documents`.

![Prázdná složka VS Code](assets/open-cline-test.png)

Nyní jsme připraveni zadat pokyn lokálnímu kódovacímu agentovi.
- Klikněte na rozšíření Cline v levém sloupci a zadejte výzvu ke spuštění agenta. Jako příklad použijme následující výzvu:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent poté začne vytvářet soubory podle zadané výzvy. Jako uživatel můžete sledovat generování kódu ve VS Code, jak je znázorněno níže. Možná budete muset pokaždé kliknout na `Save`, když Cline chce vytvořit soubor.

![Generování kódu v Cline](assets/cline-code-generation.png)

Po vygenerování softwaru je agent hotov a vy můžete aplikaci spustit. V tomto případě agent zapsal do tří souborů: `index.html`, `script.js` a `styles.css`. Pouhým dvojitým kliknutím na soubor HTML můžeme načíst vygenerovanou webovou stránku a pracovat s ní.

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

## Další kroky

Po vygenerování webové stránky můžete pokračovat v práci s Cline a webovou stránku vylepšovat. Dvě možná vylepšení jsou:

- **Dokumentace**: Stačí zadat agentovi výzvu `Add a README` a agent vygeneruje soubor `README.md` dokumentující webovou stránku.
- **Animace**: Zadejte modelu výzvu `Add an animation that visually represents a large language model running on a laptop.` pro přidání animace na webovou stránku.

Doporučujeme čtenáři, aby se pokusil generovat další aplikace pomocí tohoto nastavení. Níže jsou uvedeny některé zábavné příklady, které jsme vyzkoušeli:

- **Retro arkádové hry**: Vyzkoušejte další výzvy. Může být také zábavné nechat agenta vytvářet retro hry v Pythonu pomocí balíčku `PyGame` s následující výzvou:

```code
Create a simple pong game using the PyGame python package.
```

- **Analýza dat**: Jednou z oblastí, kde jsou kódovací agenti obzvláště užiteční, je skriptování a analýza dat. Tato výzva demonstruje schopnost lokálního modelu generovat software pro analýzu dat pro vizualizaci cen akcií:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Zdroje

Níže jsou uvedeny některé další zdroje pro získání dalších informací o kódovacích agentech, Cline a spouštění úloh na

* Více informací o partnerství a integraci AMD a LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD popisující spuštění Cline na AMD Ryzen™ AI a grafických kartách Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline o spouštění kódovacích agentů lokálně na AI PC: https://cline.bot/blog/local-models-amd