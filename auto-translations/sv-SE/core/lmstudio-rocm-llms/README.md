<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt

LM Studio är en kraftfull GUI-baserad wrapper för [llama.cpp](https://github.com/ggml-org/llama.cpp) och tillhandahåller också en [OpenAI-kompatibel slutpunkt](https://lmstudio.ai/docs/developer/openai-compat) för lokal modellservering. LM Studio erbjuder ett enkelt men kraftfullt gränssnitt för att enkelt ladda ner och distribuera modeller. LM Studio erbjuder både Vulkan- och AMD ROCm™-programvarubackender (kallade runtimes) för AMD-användare.


## Vad du kommer att lära dig
- Hur du konfigurerar och använder LM Studio för att utnyttja din lokala hårdvara
- Testa och hantera LLM:er i en helt offline-miljö
- Servera modeller via ett OpenAI-kompatibelt API för att driva anpassade arbetsflöden och appar


## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera efter programvaruuppdateringar

<!-- @os:linux -->
> **Obs**: Du kan installera VS Code via AMD Ryzen™ AI Developer Center. För LM Studio, följ installationsinstruktionerna nedan.
<!-- @os:end -->

<!-- @os:windows -->
> **Obs**: Om VS Code eller LM Studio inte är installerat kan du installera dem från AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Ladda ner modeller

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

## Chatta med en LLM
Lär dig hur du börjar chatta med en LLM i ChatGPT-klass helt lokalt.  

1. Öppna LMStudio. 
2. Tryck `Ctrl + L` för att öppna Model Loader, välj `Manually choose model load parameters` och klicka på `${model_name}`
3. Se till att "show advanced settings" är markerat.  
4. Ändra `Context Length` efter önskemål. Högre kontextlängd innebär mer modellminne, men mer systemminne används. Rekommenderat för denna spelbok är 4096.
5. Se till att `GPU Offload` är inställt på maximum och att `Flash Attention` är på (Cache Quantizations kan förbli av)
6. Markera `Remember settings` och klicka på `Load Model`.
7. Om du inte är i chattfönstret, tryck `Ctrl + 1` eller klicka på 👾-knappen längst upp till vänster på skärmen.
8. Skicka ett meddelande och börja interagera med modellen!

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

> **Tips**: Kontextlängd avser modellens minne. Flash attention förbättrar bearbetningshastigheten samtidigt som minnesanvändningen minskar. GPU Offload flyttar beräkningar till grafikkortet för snabbare svar.

## Servera LLM:er via en OpenAI-kompatibel slutpunkt

LM Studio erbjuder också en OpenAI-kompatibel slutpunkt i form av LM Studio Server. Detta har redan demonstrerats i ett agentbaserat kodningsarbetsflöde med Cline [här](../playbooks/vscode-qwen3-coder). Ett annat vanligt användningsfall är att ansluta LM Studio Server till valfri webbapplikation (React, Node.js, Python) genom att skicka standard-HTTP-förfrågningar till slutpunkten för inferens.

Följ dessa instruktioner för att konfigurera LM Studio Server:

1. På vänster sida, klicka på fliken `Developer` (kommandoradsikonen) eller `Ctrl + 2` och klicka sedan på `Server Settings`.  
2. (Valfritt): Om du vill servera modellen över ditt lokala nätverk, markera `Serve on Local Network`. Om du vill använda den med en webbplats eller omfattande anrop inom VS Code, markera `Enable CORS`. 
3. I det övre vänstra hörnet, säkerställ att servern körs genom att klicka på växlingsknappen framför `Status`.
4. En OpenAI-kompatibel slutpunkt kommer nu att köras. Adressen är vanligtvis http://127.0.0.1:1234  
5. Om en modell inte redan är laddad kan du ladda den genom att klicka på `Load Model` och följa de tidigare nämnda stegen. 

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


Denna modell kommer nu att vara tillgänglig via LM Studio Server-slutpunkten och kommer att stödja OpenAI-slutpunkter, inklusive:

| Slutpunkt | Metod | Dokumentation |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Exempel: Pinga din slutpunkt
Nu när du precis har skapat den OpenAI-kompatibla slutpunkten ska vi titta på hur du integrerar detta i en Python-utvecklingsmiljö (till exempel VSCode) och använder ditt system som en lokal API-leverantör.

1. Skapa en virtuell Python-miljö:

<!-- @os:linux -->
<!-- @device:halo_box -->
    På Linux, öppna en terminal i katalogen du väljer och följ kommandona för att skapa en venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

    På Linux, öppna en terminal i katalogen du väljer och följ kommandona för att skapa en venv.
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
    På Windows, öppna en terminal i katalogen du väljer och följ kommandona för att skapa en venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tips**: Windows-användare kan behöva ändra sin PowerShell-körningsprincip (Execution Policy) (t.ex.
    > ställa in den till RemoteSigned eller Unrestricted) innan de kör vissa Powershell-kommandon.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    På Windows, öppna en terminal i katalogen du väljer och följ kommandona för att skapa en venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tips**: Windows-användare kan behöva ändra sin PowerShell-körningsprincip (Execution Policy) (t.ex.
    > ställa in den till RemoteSigned eller Unrestricted) innan de kör vissa Powershell-kommandon.

<!-- @device:end -->
<!-- @os:end -->

2. Installera OpenAI-paketet
    ```bash
    pip install openai
    ```

3. Kör följande skript för att pinga slutpunkten vi just har skapat.
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

#### (Valfritt): Byta mellan körtider

1. Tryck på `Ctrl + Shift + R` på tangentbordet. Alternativt klicka på fliken `Discover` (förstoringsglas) till vänster och klicka sedan på `Runtime` i popup-fönstret.
2. Du bör då se `Runtime Selections`, där rullgardinsmenyn kan användas för att ändra körtiden.


## Nästa steg

- **Anpassad appintegration**: Integrera dina egna Python-skript eller applikationer med den lokala OpenAI-kompatibla API:et.
- **Avancerade gränssnitt**: Anslut kraftfulla gränssnitt som Open WebUI till din server för chatthistorik och personahantering.

För mer dokumentation, besök: https://lmstudio.ai/docs/developer