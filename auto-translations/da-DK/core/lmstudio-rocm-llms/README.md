<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

LM Studio er en effektiv GUI-baseret wrapper til [llama.cpp](https://github.com/ggml-org/llama.cpp) og tilbyder også et [OpenAI-kompatibelt endpoint](https://lmstudio.ai/docs/developer/openai-compat) til lokal model-servering. LM Studio tilbyder en simpel, men kraftfuld grænseflade til nemt at downloade og udrulle modeller. LM Studio tilbyder både Vulkan- og AMD ROCm™ software-backends (kaldet runtimes) til AMD-brugere.


## Hvad du vil lære
- Hvordan du konfigurerer og bruger LM Studio til at udnytte din lokale hardware
- Test og administrer LLM'er i et helt offline miljø
- Server modeller via et OpenAI-kompatibelt API for at drive tilpassede workflows og apps


## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollér for softwareopdateringer

<!-- @os:linux -->
> **Bemærk**: Du kan installere VS Code via AMD Ryzen™ AI Developer Center. For LM Studio skal du følge installationsvejledningen nedenfor.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk**: Hvis VS Code eller LM Studio ikke er installeret, kan du installere dem fra AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Download af modeller

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

## Chat med en LLM
Lær hvordan du starter en chat med en LLM af ChatGPT-kvalitet helt lokalt.  

1. Åbn LMStudio. 
2. Tryk `Ctrl + L` for at åbne Model Loader, vælg `Manually choose model load parameters`, og klik på `${model_name}`
3. Sørg for, at "show advanced settings" er markeret.  
4. Ændr `Context Length` efter ønske. En højere kontekstlængde betyder mere modelhukommelse, men også mere brugt systemhukommelse. Anbefalet for denne playbook er 4096.
5. Sørg for, at `GPU Offload` er sat til maksimum, og at `Flash Attention` er slået til (Cache Quantizations kan forblive slået fra)
6. Marker `Remember settings`, og klik på `Load Model`.
7. Hvis du ikke er i chatvinduet, skal du trykke `Ctrl + 1` eller klikke på 👾-knappen øverst til venstre på skærmen.
8. Send en besked, og begynd at interagere med modellen!

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

> **Tip**: Kontekstlængde refererer til modellens hukommelse. Flash attention forbedrer behandlingshastigheden og reducerer samtidig hukommelsesforbruget. GPU Offload flytter beregning over til grafikkortet for hurtigere svar.

## Server LLM'er via et OpenAI-kompatibelt endpoint

LM Studio tilbyder også et OpenAI-kompatibelt endpoint i form af LM Studio Server. Dette er allerede blevet demonstreret i et agentbaseret kodningsworkflow med Cline [her](../playbooks/vscode-qwen3-coder). Et andet almindeligt anvendelsestilfælde er at forbinde LM Studio Server til en hvilken som helst webapplikation (React, Node.js, Python) ved at sende standard HTTP-forespørgsler til inference-endpointet.

For at konfigurere LM Studio Server skal du følge nedenstående vejledning:

1. I venstre side skal du klikke på fanen `Developer` (kommandolinjeikon) eller trykke `Ctrl + 2` og derefter klikke på `Server Settings`.  
2. (Valgfrit): Hvis du vil servere modellen over dit LAN, skal du markere `Serve on Local Network`. Hvis du vil bruge den med en hjemmeside eller omfattende kald i VS Code, skal du markere `Enable CORS`. 
3. Øverst i venstre hjørne skal du sikre dig, at serveren kører, ved at klikke på til/fra-knappen foran `Status`.
4. Der vil nu køre et OpenAI-kompatibelt endpoint. Adressen er typisk http://127.0.0.1:1234  
5. Hvis en model ikke allerede er indlæst, kan du indlæse den ved at klikke på `Load Model` og følge de tidligere nævnte trin. 

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


Denne model vil nu være tilgængelig via LM Studio Server-endpointet og vil understøtte OpenAI-endpoints, herunder:

| Endpoint | Metode | Dokumentation |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Eksempel: Ping af dit Endpoint
Efter at have oprettet det OpenAI-kompatible endpoint, lad os se på, hvordan man integrerer dette i et Python-udviklermiljø (såsom VSCode) og bruger dit system som en lokal API-udbyder. 

1. Opret et Python virtuelt miljø:

<!-- @os:linux -->
<!-- @device:halo_box -->
    På Linux, åbn en terminal i den mappe, du ønsker, og følg kommandoerne for at oprette et venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen, for at dette træder i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

    På Linux, åbn en terminal i den mappe, du ønsker, og følg kommandoerne for at oprette et venv.
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
    På Windows, åbn en terminal i den mappe, du ønsker, og følg kommandoerne for at oprette et venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Windows-brugere kan være nødt til at ændre deres PowerShell Execution Policy (f.eks.
    > sætte den til RemoteSigned eller Unrestricted), før de kan køre visse PowerShell-kommandoer.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    På Windows, åbn en terminal i den mappe, du ønsker, og følg kommandoerne for at oprette et venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Windows-brugere kan være nødt til at ændre deres PowerShell Execution Policy (f.eks.
    > sætte den til RemoteSigned eller Unrestricted), før de kan køre visse PowerShell-kommandoer.

<!-- @device:end -->
<!-- @os:end -->

2. Installer OpenAI-pakken
    ```bash
    pip install openai
    ```

3. Kør følgende script for at ping det endpoint, vi lige har oprettet.
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

#### (Valgfrit): Skift mellem Runtimes

1. Tryk på `Ctrl + Shift + R` på dit tastatur. Alternativt kan du klikke på fanen `Discover` (forstørrelsesglas) i venstre side og derefter klikke på `Runtime` i pop op-vinduet.   
2. Du bør derefter se `Runtime Selections`, hvor rullemenuen kan bruges til at skifte runtime.


## Næste trin

- **Tilpasset appintegration**: Integrer dine egne Python-scripts eller applikationer ved hjælp af det lokale OpenAI-kompatible API.
- **Avancerede frontends**: Forbind kraftfulde grænseflader som Open WebUI til din server for chathistorik og personahåndtering.

For yderligere dokumentation, besøg venligst: https://lmstudio.ai/docs/developer