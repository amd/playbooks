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

## Přehled

LM Studio je výkonný obalový program s grafickým rozhraním pro [llama.cpp](https://github.com/ggml-org/llama.cpp), který zároveň poskytuje [koncový bod kompatibilní s OpenAI](https://lmstudio.ai/docs/developer/openai-compat) pro lokální obsluhu modelů. LM Studio nabízí jednoduché, ale výkonné rozhraní pro snadné stažení a nasazení modelů. Pro uživatele AMD nabízí LM Studio jak backend Vulkan, tak backend AMD ROCm™ software (nazývané runtime).


## Co se naučíte
- Jak nakonfigurovat a používat LM Studio k využití vašeho lokálního hardwaru
- Testovat a spravovat LLM zcela offline
- Poskytovat modely přes API kompatibilní s OpenAI pro pohon vlastních workflow a aplikací


## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @os:linux -->
> **Poznámka**: VS Code lze nainstalovat prostřednictvím AMD Ryzen™ AI Developer Center. Pro LM Studio postupujte podle níže uvedených instalací.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Pokud nemáte nainstalovaný VS Code nebo LM Studio, můžete je nainstalovat z AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace požadovaného softwaru

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Stahování modelů

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

## Konverzace s LLM
Naučte se, jak začít komunikovat s LLM na úrovni ChatGPT zcela lokálně.  

1. Otevřete LMStudio. 
2. Stisknutím `Ctrl + L` otevřete nástroj pro načítání modelu (Model Loader), vyberte `Manually choose model load parameters` a klikněte na `${model_name}`
3. Ujistěte se, že je zaškrtnuto „show advanced settings“.  
4. Změňte `Context Length` podle potřeby. Vyšší délka kontextu znamená více paměti modelu, ale i vyšší spotřebu systémové paměti. Pro tuto příručku se doporučuje hodnota 4096.
5. Ujistěte se, že je `GPU Offload` nastaveno na maximum a `Flash Attention` je zapnuté (kvantizace mezipaměti mohou zůstat vypnuté)
6. Zaškrtněte `Remember settings` a klikněte na `Load Model`.
7. Pokud se nenacházíte v okně chatu, stiskněte `Ctrl + 1` nebo klikněte na tlačítko 👾 v levém horním rohu obrazovky.
8. Odešlete zprávu a začněte s modelem komunikovat!

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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
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

> **Tip**: Délka kontextu odkazuje na paměť modelu. Flash attention zlepšuje rychlost zpracování a zároveň snižuje spotřebu paměti. GPU Offload přenáší výpočty na grafickou kartu pro rychlejší odezvy.

## Poskytování LLM prostřednictvím koncového bodu kompatibilního s OpenAI

LM Studio nabízí také koncový bod kompatibilní s OpenAI ve formě LM Studio Server. To bylo již předvedeno v agentním workflow pro programování s Cline [zde](../playbooks/vscode-qwen3-coder). Dalším běžným případem použití je připojení LM Studio Server k libovolné webové aplikaci (React, Node.js, Python) pomocí odesílání standardních HTTP požadavků na koncový bod pro inferenci.

Pro nastavení LM Studio Server postupujte podle následujících pokynů:

1. Na levé straně klikněte na kartu `Developer` (ikona příkazové řádky) nebo stiskněte `Ctrl + 2` a poté klikněte na `Server Settings`.  
2. (Volitelné): Pokud chcete model poskytovat přes vaši LAN, zaškrtněte `Serve on Local Network`. Pokud jej chcete používat s webovou stránkou nebo pro rozsáhlé volání v rámci VS Code, zaškrtněte `Enable CORS`. 
3. V levém horním rohu se ujistěte, že server běží kliknutím na přepínací tlačítko u `Status`.
4. Nyní bude spuštěn koncový bod kompatibilní s OpenAI. Adresa je obvykle na http://127.0.0.1:1234  
5. Pokud model ještě není načtený, můžete jej načíst kliknutím na `Load Model` a postupem podle výše uvedených kroků. 

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


Tento model bude nyní přístupný prostřednictvím koncového bodu LM Studio Server a bude podporovat koncové body OpenAI, včetně:

| Koncový bod | Metoda | Dokumentace |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Příklad: Ping vašeho endpointu
Nyní, když jsme vytvořili endpoint kompatibilní s OpenAI, podívejme se, jak jej integrovat do vývojářského prostředí pro Python (například VSCode) a použít váš systém jako lokálního poskytovatele API.

1. Vytvořte virtuální prostředí Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udělte svému uživateli přístup ke GPU zařízením** (aby se změna projevila, odhlaste se a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
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
    Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Uživatelé Windows možná budou muset upravit zásady spouštění PowerShell (Execution Policy) (např.
    > nastavit ji na RemoteSigned nebo Unrestricted), než budou moci spustit některé příkazy PowerShellu.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Uživatelé Windows možná budou muset upravit zásady spouštění PowerShell (Execution Policy) (např.
    > nastavit ji na RemoteSigned nebo Unrestricted), než budou moci spustit některé příkazy PowerShellu.

<!-- @device:end -->
<!-- @os:end -->

2. Nainstalujte balíček OpenAI
    ```bash
    pip install openai
    ```

3. Spusťte následující skript pro ping endpointu, který jsme právě vytvořili.
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

#### (Volitelné): Přepínání mezi Runtime prostředími

1. Stiskněte na klávesnici `Ctrl + Shift + R`. Případně klikněte na kartu `Discover` (lupa) na levé straně a poté klikněte na `Runtime` ve vyskakovacím okně.   
2. Poté byste měli vidět `Runtime Selections`, kde lze pomocí rozevírací nabídky změnit runtime prostředí.


## Další kroky

- **Integrace vlastní aplikace**: Integrujte vlastní Python skripty nebo aplikace pomocí lokálního API kompatibilního s OpenAI.
- **Pokročilá rozhraní**: Připojte k serveru výkonná rozhraní jako Open WebUI pro historii chatu a správu person.

Další dokumentaci naleznete na: https://lmstudio.ai/docs/developer