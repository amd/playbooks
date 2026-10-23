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

## Prehľad

LM Studio je výkonný grafický nadstavbový nástroj pre [llama.cpp](https://github.com/ggml-org/llama.cpp) a zároveň poskytuje [koncový bod kompatibilný s OpenAI](https://lmstudio.ai/docs/developer/openai-compat) na lokálne nasadenie modelov. LM Studio ponúka jednoduché, no výkonné rozhranie na jednoduché stiahnutie a nasadenie modelov. Pre používateľov AMD poskytuje LM Studio dve backendové riešenia (nazývané runtime) – Vulkan a AMD ROCm™ software.

<!-- @device:halo_box -->
> **Poznámka:** Niektoré systémy AMD Ryzen AI Halo majú model pre tento playbook už predinštalovaný, zatiaľ čo iné nie. Podporované sú oba prípady. Keď sa dostanete k časti **Sťahovanie modelov**, skontrolujte, či je model v LM Studio už dostupný – ak áno, stiahnutie môžete preskočiť; ak nie, postupujte podľa uvedených krokov a stiahnite si ho.
<!-- @device:end -->


## Čo sa naučíte
- Ako nakonfigurovať a používať LM Studio na využitie vášho lokálneho hardvéru
- Testovať a spravovať LLM modely v úplne offline prostredí
- Poskytovať modely prostredníctvom API kompatibilného s OpenAI na podporu vlastných pracovných postupov a aplikácií


<!-- @device:halo_box,halo,stx,krk -->
## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @os:linux -->
> **Poznámka**: VS Code môžete nainštalovať prostredníctvom AMD Ryzen™ AI Developer Center. Pre LM Studio postupujte podľa nižšie uvedených inštalačných pokynov.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Ak nemáte nainštalovaný VS Code alebo LM Studio, môžete ich nainštalovať z AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia požadovaného softvéru

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->
<!-- @prereq:lmstudio -->

## Sťahovanie modelov

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @prereq:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @prereq:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Konverzácia s LLM modelom
Naučte sa, ako začať úplne lokálne konverzovať s LLM modelom na úrovni ChatGPT.  

1. Otvorte LMStudio. 
2. Stlačením `Ctrl + L` otvorte nástroj na načítanie modelu, vyberte `Manually choose model load parameters` a kliknite na `${model_name}`
3. Uistite sa, že je začiarknuté „show advanced settings“.  
4. Zmeňte `Context Length` podľa potreby. Vyššia hodnota context length znamená väčšiu pamäť modelu, ale aj väčšie využitie systémovej pamäte. Odporúčaná hodnota pre tento playbook je 4096.
5. Uistite sa, že `GPU Offload` je nastavené na maximum a `Flash Attention` je zapnuté (Cache Quantizations môžu zostať vypnuté)
6. Začiarknite `Remember settings` a kliknite na `Load Model`.
7. Ak sa nenachádzate v okne konverzácie, stlačte `Ctrl + 1` alebo kliknite na tlačidlo 👾 v ľavom hornom rohu obrazovky.
8. Odošlite správu a začnite komunikovať s modelom!

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
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Tip**: Context length odkazuje na pamäť modelu. Flash attention zlepšuje rýchlosť spracovania a zároveň znižuje spotrebu pamäte. GPU Offload presúva výpočty na grafickú kartu kvôli rýchlejším odozvám.

## Poskytovanie LLM modelov prostredníctvom koncového bodu kompatibilného s OpenAI

LM Studio tiež ponúka koncový bod kompatibilný s OpenAI vo forme LM Studio Server. Toto bolo už predvedené v agentickom pracovnom postupe kódovania s Cline [tu](../playbooks/vscode-qwen3-coder). Ďalším bežným prípadom použitia je pripojenie LM Studio Server k ľubovoľnej webovej aplikácii (React, Node.js, Python) odosielaním štandardných HTTP požiadaviek na inferenčný koncový bod.

Na nastavenie LM Studio Server postupujte podľa nasledujúcich pokynov:

1. Na ľavej strane kliknite na kartu `Developer` (ikona príkazového riadku) alebo stlačte `Ctrl + 2` a potom kliknite na `Server Settings`.  
2. (Voliteľné): Ak chcete model poskytovať prostredníctvom vašej lokálnej siete, začiarknite `Serve on Local Network`. Ak ho chcete používať s webovou stránkou alebo s rozsiahlym volaním v rámci VS Code, začiarknite `Enable CORS`. 
3. V ľavom hornom rohu sa uistite, že server beží, kliknutím na prepínač pred nápisom `Status`.
4. Teraz bude bežať koncový bod kompatibilný s OpenAI. Adresa je zvyčajne http://127.0.0.1:1234  
5. Ak model ešte nie je načítaný, môžete ho načítať kliknutím na `Load Model` a postupom podľa vyššie uvedených krokov. 

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


Tento model bude teraz dostupný prostredníctvom koncového bodu LM Studio Server a bude podporovať koncové body OpenAI vrátane:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Príklad: Pingovanie vášho koncového bodu
Keď sme práve vytvorili OpenAI Compatible koncový bod, pozrime sa, ako ho integrovať do vývojárskeho prostredia Python (napríklad VSCode) a použiť váš systém ako lokálneho poskytovateľa API.

1. Vytvorte virtuálne prostredie Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    V systéme Linux otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (aby sa to prejavilo, odhláste sa a znova sa prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

    V systéme Linux otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    V systéme Windows otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Používatelia systému Windows môžu potrebovať upraviť svoju politiku vykonávania PowerShell (napr.
    > nastaviť ju na RemoteSigned alebo Unrestricted) pred spustením niektorých príkazov Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    V systéme Windows otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Používatelia systému Windows môžu potrebovať upraviť svoju politiku vykonávania PowerShell (napr.
    > nastaviť ju na RemoteSigned alebo Unrestricted) pred spustením niektorých príkazov Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Nainštalujte balík OpenAI
    ```bash
    pip install openai
    ```

3. Spustite nasledujúci skript na pingnutie koncového bodu, ktorý sme práve vytvorili.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
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
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
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

#### (Voliteľné): Prepínanie medzi Runtimes

1. Stlačte `Ctrl + Shift + R` na klávesnici. Prípadne kliknite na kartu `Discover` (Lupa) na ľavej strane a potom kliknite na `Runtime` vo vyskakovacom okne.
2. Následne by sa vám mala zobraziť možnosť `Runtime Selections`, kde môžete pomocou rozbaľovacej ponuky zmeniť runtime.


## Ďalšie kroky

- **Integrácia vlastnej aplikácie**: Integrujte vlastné skripty alebo aplikácie v jazyku Python pomocou lokálneho API kompatibilného s OpenAI.
- **Pokročilé frontendy**: Pripojte výkonné rozhrania, ako napríklad Open WebUI, k vášmu serveru na správu histórie chatu a personalizácie.

Ďalšiu dokumentáciu nájdete na: https://lmstudio.ai/docs/developer