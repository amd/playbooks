<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

LM Studio is een krachtige GUI-gebaseerde wrapper voor [llama.cpp](https://github.com/ggml-org/llama.cpp) en biedt ook een [OpenAI-compatibel endpoint](https://lmstudio.ai/docs/developer/openai-compat) voor het lokaal serveren van modellen. LM Studio biedt een eenvoudige maar krachtige interface om eenvoudig modellen te downloaden en te implementeren. LM Studio biedt zowel Vulkan- als AMD ROCm™-softwarebackends (runtimes genoemd) voor AMD-gebruikers.


## Wat je zult leren
- Hoe je LM Studio configureert en gebruikt om je lokale hardware optimaal te benutten
- LLM's testen en beheren in een volledig offline omgeving
- Modellen serveren via een OpenAI-compatibele API om aangepaste workflows en apps aan te sturen


## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @os:linux -->
> **Opmerking**: Je kunt VS Code installeren via het AMD Ryzen™ AI Developer Center. Volg voor LM Studio de onderstaande installatie-instructies.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking**: Als VS Code of LM Studio niet is geïnstalleerd, kun je deze installeren via het AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## De softwarevereisten installeren

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Modellen downloaden

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

## Chatten met een LLM
Leer hoe je volledig lokaal kunt beginnen met chatten met een LLM van ChatGPT-niveau.  

1. Open LMStudio. 
2. Druk op `Ctrl + L` om de Model Loader te openen, selecteer `Manually choose model load parameters`, en klik op `${model_name}`
3. Zorg ervoor dat "show advanced settings" is aangevinkt.  
4. Wijzig `Context Length` naar wens. Een hogere contextlengte betekent meer modelgeheugen, maar ook meer systeemgeheugengebruik. Voor dit playbook wordt 4096 aanbevolen.
5. Zorg ervoor dat `GPU Offload` op maximum staat en dat `Flash Attention` is ingeschakeld (Cache Quantizations mag uitgeschakeld blijven)
6. Vink `Remember settings` aan en klik op `Load Model`.
7. Als je niet in het chatvenster bent, druk dan op `Ctrl + 1` of klik op de 👾-knop linksboven in het scherm.
8. Stuur een bericht en begin met interactie met het model!

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

> **Tip**: Contextlengte verwijst naar het geheugen van het model. Flash attention verbetert de verwerkingssnelheid en vermindert tegelijkertijd het geheugengebruik. GPU Offload verplaatst rekenwerk naar de grafische kaart voor snellere reacties.

## LLM's serveren via een OpenAI-compatibel endpoint

LM Studio biedt ook een OpenAI-compatibel endpoint in de vorm van LM Studio Server. Dit is al gedemonstreerd in een agentische coderingsworkflow met Cline [hier](../playbooks/vscode-qwen3-coder). Een ander veelvoorkomend gebruiksscenario is het verbinden van LM Studio Server met een willekeurige webapplicatie (React, Node.js, Python) door standaard HTTP-verzoeken naar het inference-endpoint te sturen.

Volg deze instructies om LM Studio Server in te stellen:

1. Klik aan de linkerkant op het tabblad `Developer` (het icoon van de opdrachtregel) of druk op `Ctrl + 2` en klik vervolgens op `Server Settings`.  
2. (Optioneel): Als je het model via je LAN wilt serveren, vink dan `Serve on Local Network` aan. Als je het wilt gebruiken met een website of uitgebreide aanroepen binnen VS Code, vink dan `Enable CORS` aan. 
3. Controleer linksboven of de server draait door op de schakelknop voor `Status` te klikken.
4. Er draait nu een OpenAI-compatibel endpoint. Het adres is doorgaans http://127.0.0.1:1234  
5. Als er nog geen model is geladen, kun je dit doen door op `Load Model` te klikken en de eerder genoemde stappen te volgen. 

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


Dit model is nu toegankelijk via het LM Studio Server-endpoint en ondersteunt OpenAI-endpoints, waaronder:

| Endpoint | Methode | Documentatie |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Voorbeeld: Uw Endpoint pingen
Nu we net het OpenAI Compatible endpoint hebben aangemaakt, laten we bekijken hoe u dit kunt integreren in een Python-ontwikkelomgeving (zoals VSCode) en uw systeem kunt gebruiken als lokale API-provider.

1. Maak een Python virtual environment aan:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Open op Linux een terminal in de map van uw keuze en volg de commando's om een venv aan te maken.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Geef uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Open op Linux een terminal in de map van uw keuze en volg de commando's om een venv aan te maken.
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
    Open op Windows een terminal in de map van uw keuze en volg de commando's om een venv aan te maken.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell Execution Policy aanpassen (bijvoorbeeld
    > door deze in te stellen op RemoteSigned of Unrestricted) voordat ze bepaalde Powershell-commando's uitvoeren.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Open op Windows een terminal in de map van uw keuze en volg de commando's om een venv aan te maken.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell Execution Policy aanpassen (bijvoorbeeld
    > door deze in te stellen op RemoteSigned of Unrestricted) voordat ze bepaalde Powershell-commando's uitvoeren.

<!-- @device:end -->
<!-- @os:end -->

2. Installeer het OpenAI-pakket
    ```bash
    pip install openai
    ```

3. Voer het volgende script uit om het zojuist aangemaakte endpoint te pingen.
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

#### (Optioneel): Wisselen tussen Runtimes

1. Druk op `Ctrl + Shift + R` op uw toetsenbord. U kunt ook op het tabblad `Discover` (vergrootglas) aan de linkerkant klikken en vervolgens op `Runtime` in het pop-upvenster klikken.
2. U ziet dan `Runtime Selections`, waar het dropdownmenu kan worden gebruikt om de runtime te wijzigen.


## Volgende stappen

- **Aangepaste app-integratie**: Integreer uw eigen Python-scripts of applicaties met behulp van de lokale OpenAI-compatibele API.
- **Geavanceerde frontends**: Verbind krachtige interfaces zoals Open WebUI met uw server voor chatgeschiedenis en persona-beheer.

Bezoek voor meer documentatie: https://lmstudio.ai/docs/developer