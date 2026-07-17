<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

LM Studio er en kraftig GUI-basert innpakning for [llama.cpp](https://github.com/ggml-org/llama.cpp) og tilbyr også et [OpenAI-kompatibelt endepunkt](https://lmstudio.ai/docs/developer/openai-compat) for lokal modelltjeneste. LM Studio gir et enkelt, men kraftig grensesnitt for enkelt å laste ned og distribuere modeller. LM Studio tilbyr både Vulkan- og AMD ROCm™-programvarebackender (kalt kjøretidsmiljøer) for AMD-brukere.


## Hva du vil lære
- Hvordan konfigurere og bruke LM Studio for å utnytte din lokale maskinvare
- Teste og administrere LLM-er i et fullstendig frakoblet miljø
- Serve modeller via OpenAI-kompatibelt API for å drive egendefinerte arbeidsflyter og apper


## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer

<!-- @os:linux -->
> **Merk**: Du kan installere VS Code via AMD Ryzen™ AI Developer Center. For LM Studio, følg installasjonsinstruksjonene nedenfor.
<!-- @os:end -->

<!-- @os:windows -->
> **Merk**: Hvis VS Code eller LM Studio ikke er installert, kan du installere dem fra AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Laste ned modeller

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

## Chatte med en LLM
Lær hvordan du starter en samtale med en LLM av ChatGPT-kvalitet helt lokalt.

1. Åpne LMStudio.
2. Trykk `Ctrl + L` for å åpne Model Loader, velg `Manually choose model load parameters`, og klikk på `${model_name}`
3. Sørg for at "show advanced settings" er avhuket.
4. Endre `Context Length` etter ønske. Høyere kontekstlengde betyr mer modellminne, men mer systemminne brukes. Anbefalt for dette playbook er 4096.
5. Sørg for at `GPU Offload` er satt til maksimum og at `Flash Attention` er På (Cache Quantizations kan forbli av)
6. Huk av `Remember settings` og klikk på `Load Model`.
7. Hvis du ikke er i chatvinduet, trykk `Ctrl + 1` eller klikk på 👾-knappen øverst til venstre på skjermen.
8. Send en melding og begynn å samhandle med modellen!

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

> **Tips**: Kontekstlengde refererer til modellens minne. Flash attention forbedrer behandlingshastigheten samtidig som minnebruken reduseres. GPU Offload flytter beregning til grafikkortet for raskere svar.

## Serve LLM-er gjennom et OpenAI-kompatibelt endepunkt

LM Studio tilbyr også et OpenAI-kompatibelt endepunkt i form av LM Studio Server. Dette har allerede blitt demonstrert i en agentisk kodingsarbeidsflyt med Cline [her](../playbooks/vscode-qwen3-coder). Et annet vanlig brukstilfelle er å koble LM Studio Server til en hvilken som helst nettapplikasjon (React, Node.js, Python) ved å sende standard HTTP-forespørsler til inferansendepunktet.

For å sette opp LM Studio Server, bruk følgende instruksjoner:

1. På venstre side, klikk på `Developer`-fanen (kommandolinjeikonet) eller `Ctrl + 2`, og klikk deretter på `Server Settings`.
2. (Valgfritt): Hvis du vil serve modellen over ditt LAN, huk av `Serve on Local Network`. Hvis du vil bruke den med et nettsted eller omfattende kalling innen VS Code, huk av `Enable CORS`.
3. Øverst til venstre, sørg for at serveren kjører ved å klikke på veksleknappen foran `Status`.
4. Et OpenAI-kompatibelt endepunkt vil nå kjøre. Adressen er vanligvis http://127.0.0.1:1234
5. Hvis en modell ikke allerede er lastet, kan du laste den ved å klikke `Load Model` og følge de tidligere nevnte trinnene.

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


Denne modellen vil nå være tilgjengelig via LM Studio Server-endepunktet og vil støtte OpenAI-endepunkter inkludert:

| Endepunkt | Metode | Dokumentasjon |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Eksempel: Pinge endepunktet ditt
Nå som vi nettopp har opprettet det OpenAI-kompatible endepunktet, la oss se på hvordan vi integrerer dette i et Python-utviklermiljø (som VSCode) og bruker systemet ditt som en lokal API-leverandør.

1. Opprett et virtuelt Python-miljø:

<!-- @os:linux -->
<!-- @device:halo_box -->
    På Linux, åpne en terminal i ønsket katalog og følg kommandoene for å opprette et venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

    På Linux, åpne en terminal i ønsket katalog og følg kommandoene for å opprette et venv.
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
    På Windows, åpne en terminal i ønsket katalog og følg kommandoene for å opprette et venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tips**: Windows-brukere må kanskje endre PowerShell-kjøringspolicyen (f.eks.
    > sette den til RemoteSigned eller Unrestricted) før de kjører noen PowerShell-kommandoer.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    På Windows, åpne en terminal i ønsket katalog og følg kommandoene for å opprette et venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tips**: Windows-brukere må kanskje endre PowerShell-kjøringspolicyen (f.eks.
    > sette den til RemoteSigned eller Unrestricted) før de kjører noen PowerShell-kommandoer.

<!-- @device:end -->
<!-- @os:end -->

2. Installer OpenAI-pakken
    ```bash
    pip install openai
    ```

3. Kjør følgende skript for å pinge endepunktet vi nettopp har opprettet.
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

#### (Valgfritt): Bytte mellom kjøretidsmiljøer

1. Trykk `Ctrl + Shift + R` på tastaturet. Alternativt kan du klikke på `Discover`-fanen (forstørrelsesglassikonet) på venstre side og deretter klikke på `Runtime` i popup-vinduet.
2. Du skal da se `Runtime Selections`, der rullegardinmenyen kan brukes til å endre kjøretidsmiljøet.


## Neste steg

- **Egendefinert appintegrasjon**: Integrer dine egne Python-skript eller applikasjoner ved hjelp av det lokale OpenAI-kompatible API-et.
- **Avanserte grensesnitt**: Koble kraftige grensesnitt som Open WebUI til serveren din for chathistorikk og personaadministrasjon.

For mer dokumentasjon, besøk: https://lmstudio.ai/docs/developer