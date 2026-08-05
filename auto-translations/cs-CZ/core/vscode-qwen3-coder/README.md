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
> Tato příručka vyžaduje minimálně **32GB** systémové paměti.
<!-- @device:end -->

## Přehled

Kódovací agenti jsou výkonné nástroje, které umožňují vývojářům spolupracovat s AI agenty postavenými na velkých jazykových modelech (LLM). Lze je začlenit přímo do vývojového prostředí, například do terminálu nebo VS Code, což umožňuje jejich hladkou integraci do pracovního postupu vývojáře.

Tento tutoriál ukazuje, jak spustit kódovacího agenta zcela lokálně na vašem počítači pomocí Cline, VS Code a LM Studio.

## Co se naučíte

* Jak spustit VS Code s kódovacím agentem Cline, který pomáhá při softwarově-inženýrských úlohách.
* Jak nakonfigurovat Cline pro komunikaci s LM Studio za účelem lokální inference kódovacích agentů.
* Jak používat lokální kódovací agenty k řešení reálných softwarově-inženýrských úloh.

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

K obsluze LLM, který pohání kódovacího agenta, použijeme LM Studio.

- Do vyhledávacího pole zadejte `LM Studio` a spusťte aplikaci. Zobrazí se vám následující obrazovka.

![Úvodní obrazovka LM Studio](assets/initial-lm-studio.png)

Dále je třeba do systému načíst LLM. Použijeme model `Qwen3-Coder-30B-A3B` s velkou délkou kontextu. (Pokud jej ještě nemáte nainstalovaný, použijte kartu Model.)
- Klikněte na vyhledávací pole v horní části okna LM Studio nebo stiskněte `CTRL+L`. Klikněte na přepínač `Manually choose model load parameters` a poté klikněte na model Qwen3-Coder-30B-A3B.
- Změňte délku kontextu ze `4096` na `32768` a ujistěte se, že `GPU Offload` je nastaveno na maximum. Poté klikněte na `Load Model`.

![Výběr modelu](assets/model-list-zoomed.png)

Používáme velkou délku kontextu, aby agent mohl zpracovávat rozsáhlé kódové báze a pamatoval si provedené změny.

![Konfigurace modelu](assets/selecting-model-zoomed.png)

Dále je třeba povolit server LM Studio.
- Klikněte v LM Studio vlevo na kartu Developer nebo stiskněte `CTRL+2`.
- Zaškrtněte přepínač stavu a ujistěte se, že je nastaven na `Running`.

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

Nainstalujeme rozšíření Cline do VS Code a připojíme jej k serveru LM Studio, který jsme právě vytvořili.
- Do vyhledávacího pole zadejte `VS Code` a spusťte aplikaci.
- Klikněte na ikonu `Extensions` v levém sloupci VS Code a vyhledejte `Cline`. Poté klikněte na tlačítko `Install`.

![Instalace rozšíření Cline](assets/installing-cline-vscode-extension.png)

- Vlevo by se měla objevit ikona Cline. Kliknutím na ni Cline otevřete. Zobrazí se okno s otázkou `How will you use Cline?`. Vzhledem k tomu, že budeme používat lokální LLM běžící přes LM Studio, vyberte možnost `Bring my own API Key` a klikněte na `Continue`.

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

Dále je třeba nakonfigurovat Cline pro komunikaci se serverem LM Studio, který jsme nastavili.
- Nastavte API Provider na `LM Studio` a model na `Qwen3-Coder-30B-A3B-GGUF`.

>**Tip**: Mohou být dostupné novější modely. Pokud chcete, zvažte stažení a přechod na modely Qwen3.6.


![Konfigurace modelu](assets/cline-model-configuration-zoomed.png)

## Vytvoření prvního projektu

Použijme našeho lokálního agenta k vytvoření webové stránky! Otevřete VS Code s adresářem podle vlastního výběru, kam bude Cline vytvářet soubory.
- To provedete tak, že v levé horní části VS Code vyberete `File -> Open Folder` a zvolíte složku, například `Documents`.

![Prázdná složka ve VS Code](assets/open-cline-test.png)

Nyní jsme připraveni zadat pokyn lokálnímu kódovacímu agentovi.
- Klikněte na rozšíření Cline v levém sloupci a zadejte pokyn pro spuštění agenta. Jako příklad použijme následující pokyn:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agent poté začne vytvářet soubory podle zadaného pokynu. Jako uživatel můžete sledovat, jak se kód generuje přímo ve VS Code, jak je znázorněno níže. Při každém vytváření souboru budete pravděpodobně muset kliknout na `Save`, aby jej Cline mohl uložit.

![Generování kódu pomocí Cline](assets/cline-code-generation.png)

Po vygenerování softwaru je práce agenta dokončena a aplikaci můžete spustit. V tomto případě agent zapsal do tří souborů: `index.html`, `script.js` a `styles.css`. Pouhým dvojklikem na soubor HTML můžeme vygenerovanou webovou stránku načíst a pracovat s ní.

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

Po vygenerování webu můžete pokračovat ve spolupráci s agentem Cline a web dále vylepšovat. Dvě možná vylepšení jsou:

- **Dokumentace**: Stačí zadat agentovi pokyn `Add a README`, a agent vygeneruje soubor `README.md`, který web dokumentuje.
- **Animace**: Zadejte modelu pokyn `Add an animation that visually represents a large language model running on a laptop.` a vygenerujte pro web animaci.

Doporučujeme čtenáři vyzkoušet vygenerování dalších aplikací pomocí tohoto nastavení. Níže uvádíme několik zajímavých příkladů, které jsme vyzkoušeli:

- **Retro arkádové hry**: Vyzkoušejte i jiné pokyny. Pro agenta může být také zábavné vytvořit retro hry v Pythonu pomocí balíčku `PyGame` s následujícím pokynem:

```code
Create a simple pong game using the PyGame python package.
```

- **Analýza dat**: Jednou z oblastí, kde jsou kódovací agenti obzvlášť užiteční, je psaní skriptů a analýza dat. Tento pokyn ukazuje schopnost lokálního modelu vygenerovat software pro analýzu dat určený k vizualizaci cen akcií:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Zdroje

Níže je uvedeno několik dalších zdrojů, kde se dozvíte více o kódovacích agentech, nástroji Cline a spouštění úloh na 

* Další informace o partnerství a integraci AMD s LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blog AMD popisující spuštění nástroje Cline na grafických kartách AMD Ryzen™ AI a Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blog Cline o lokálním spouštění kódovacích agentů na AI PC: https://cline.bot/blog/local-models-amd