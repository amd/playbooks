<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

LM Studio je výkonný GUI wrapper pre [llama.cpp](https://github.com/ggml-org/llama.cpp) a zároveň poskytuje [endpoint kompatibilný s OpenAI](https://lmstudio.ai/docs/developer/openai-compat) pre lokálne nasadenie modelov. LM Studio ponúka jednoduché, ale výkonné rozhranie na jednoduché sťahovanie a nasadzovanie modelov. LM Studio ponúka pre používateľov AMD backendy (nazývané runtime) Vulkan aj AMD ROCm™.


## Čo sa naučíte
- Ako nakonfigurovať a používať LM Studio na využitie lokálneho hardvéru
- Testovať a spravovať LLM v úplne offline prostredí
- Obsluhovať modely prostredníctvom API kompatibilného s OpenAI na napájanie vlastných pracovných postupov a aplikácií


## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @os:linux -->
> **Poznámka**: VS Code môžete nainštalovať prostredníctvom AMD Ryzen™ AI Developer Center. Pre LM Studio postupujte podľa pokynov na inštaláciu uvedených nižšie.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Ak VS Code alebo LM Studio nie sú nainštalované, môžete ich nainštalovať z AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Sťahovanie modelov

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Chatovanie s LLM
Naučte sa, ako začať chatovať s LLM na úrovni ChatGPT úplne lokálne.

1. Otvorte LMStudio.
2. Stlačte `Ctrl + L` na otvorenie Model Loader, vyberte `Manually choose model load parameters` a kliknite na `${model_name}`
3. Uistite sa, že je zaškrtnutá možnosť „show advanced settings".
4. Zmeňte `Context Length` podľa potreby. Väčšia dĺžka kontextu znamená väčšiu pamäť modelu, ale aj väčšie využitie systémovej pamäte. Pre tento playbook sa odporúča hodnota 4096.
5. Uistite sa, že `GPU Offload` je nastavený na maximum a `Flash Attention` je zapnutý (Cache Quantizations môže zostať vypnuté).
6. Zaškrtnite `Remember settings` a kliknite na `Load Model`.
7. Ak nie ste v okne chatu, stlačte `Ctrl + 1` alebo kliknite na tlačidlo 👾 v ľavom hornom rohu obrazovky.
8. Pošlite správu a začnite interagovať s modelom!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
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

> **Tip**: Dĺžka kontextu sa vzťahuje na pamäť modelu. Flash attention zlepšuje rýchlosť spracovania pri súčasnom znížení využitia pamäte. GPU Offload presúva výpočty na grafickú kartu pre rýchlejšie odpovede.

## Obsluhovanie LLM prostredníctvom endpointu kompatibilného s OpenAI

LM Studio tiež ponúka endpoint kompatibilný s OpenAI vo forme LM Studio Server. Toto už bolo demonštrované v agentickom kódovacom pracovnom postupe s Cline [tu](../playbooks/vscode-qwen3-coder). Ďalším bežným prípadom použitia je pripojenie LM Studio Server k ľubovoľnej webovej aplikácii (React, Node.js, Python) odosielaním štandardných HTTP požiadaviek na inferenčný endpoint.

Na nastavenie LM Studio Server použite nasledujúce pokyny:

1. Na ľavej strane kliknite na kartu `Developer` (ikona príkazového riadka) alebo `Ctrl + 2` a potom kliknite na `Server Settings`.
2. (Voliteľné): Ak chcete obsluhovať model cez vašu LAN, zaškrtnite `Serve on Local Network`. Ak chcete používať s webovou stránkou alebo rozsiahlym volaním v rámci VS Code, zaškrtnite `Enable CORS`.
3. V ľavom hornom rohu sa uistite, že server beží, kliknutím na prepínač pred `Status`.
4. Endpoint kompatibilný s OpenAI bude teraz spustený. Adresa je zvyčajne http://127.0.0.1:1234
5. Ak model ešte nie je načítaný, môžete ho načítať kliknutím na `Load Model` a postupovaním podľa predtým uvedených krokov.

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


Tento model bude teraz prístupný prostredníctvom endpointu LM Studio Server a bude podporovať endpointy OpenAI vrátane:

| Endpoint | Metóda | Dokumentácia |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Príklad: Testovanie vášho endpointu
Po vytvorení endpointu kompatibilného s OpenAI sa pozrime na to, ako ho integrovať do vývojového prostredia Python (napríklad VSCode) a použiť váš systém ako lokálneho poskytovateľa API.

1. Vytvorte virtuálne prostredie Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Na Linuxe otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie zmeny sa odhláste a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Na Linuxe otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
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
    Na Windows otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Používatelia Windows môžu pred spustením niektorých príkazov PowerShell potrebovať upraviť svoju politiku spúšťania PowerShell (napr.
    > nastaviť ju na RemoteSigned alebo Unrestricted).

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Používatelia Windows môžu pred spustením niektorých príkazov PowerShell potrebovať upraviť svoju politiku spúšťania PowerShell (napr.
    > nastaviť ju na RemoteSigned alebo Unrestricted).

<!-- @device:end -->
<!-- @os:end -->

2. Nainštalujte balík OpenAI
    ```bash
    pip install openai
    ```

3. Spustite nasledujúci skript na otestovanie endpointu, ktorý sme práve vytvorili.
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

#### (Voliteľné): Prepínanie medzi runtime prostrediami

1. Stlačte `Ctrl + Shift + R` na klávesnici. Prípadne kliknite na kartu `Discover` (lupa) na ľavej strane a potom kliknite na `Runtime` vo vyskakovacom okne.
2. Následne by ste mali vidieť `Runtime Selections`, kde môžete pomocou rozbaľovacieho menu zmeniť runtime.


## Ďalšie kroky

- **Integrácia vlastnej aplikácie**: Integrujte vlastné Python skripty alebo aplikácie pomocou lokálneho API kompatibilného s OpenAI.
- **Pokročilé frontendy**: Pripojte výkonné rozhrania ako Open WebUI k vášmu serveru pre správu histórie chatu a správu persón.

Pre viac dokumentácie navštívte: https://lmstudio.ai/docs/developer