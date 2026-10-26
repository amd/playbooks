<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

LM Studio je moćan omotač zasnovan na grafičkom korisničkom interfejsu (GUI) za [llama.cpp](https://github.com/ggml-org/llama.cpp), a takođe pruža i [OpenAI kompatibilnu krajnju tačku](https://lmstudio.ai/docs/developer/openai-compat) za lokalno serviranje modela. LM Studio nudi jednostavan, ali moćan interfejs za lako preuzimanje i pokretanje modela. LM Studio nudi i Vulkan i AMD ROCm™ softverske pozadinske sisteme (nazvane runtime) za AMD korisnike.


## Šta ćete naučiti
- Kako da konfigurišete i koristite LM Studio kako biste iskoristili svoj lokalni hardver
- Kako da testirate i upravljate LLM-ovima u potpuno offline okruženju
- Kako da servisirate modele putem OpenAI kompatibilnog API-ja za pokretanje prilagođenih tokova rada i aplikacija


<!-- @device:halo_box,halo,stx,krk -->
## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Provera softverskih ažuriranja

<!-- @os:linux -->
> **Napomena**: VS Code možete instalirati preko AMD Ryzen™ AI Developer Center-a. Za LM Studio, pratite uputstva za instalaciju ispod.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Ako VS Code ili LM Studio nisu instalirani, možete ih instalirati preko AMD Ryzen™ AI Developer Center-a. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Preuzimanje modela

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

## Ćaskanje sa LLM-om
Naučite kako da počnete da ćaskate sa LLM-om na nivou ChatGPT-a, potpuno lokalno.  

1. Otvorite LMStudio. 
2. Pritisnite `Ctrl + L` da otvorite Model Loader, izaberite `Manually choose model load parameters`, a zatim kliknite na `${model_name}`
3. Proverite da li je opcija „show advanced settings” označena.  
4. Promenite `Context Length` po želji. Veća dužina konteksta znači veću potrošnju memorije modela, ali i veće opterećenje sistemske memorije. Preporučena vrednost za ovaj playbook je 4096.
5. Postarajte se da je `GPU Offload` postavljen na maksimum i da je `Flash Attention` uključen (Cache Quantizations mogu ostati isključeni)
6. Označite `Remember settings` i kliknite na `Load Model`.
7. Ako niste u prozoru za ćaskanje, pritisnite `Ctrl + 1` ili kliknite na dugme 👾 u gornjem levom uglu ekrana.
8. Pošaljite poruku i počnite da komunicirate sa modelom!

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

> **Savet**: Dužina konteksta se odnosi na memoriju modela. Flash attention poboljšava brzinu obrade uz smanjenje potrošnje memorije. GPU Offload prebacuje izračunavanja na grafičku karticu radi bržih odgovora.

## Serviranje LLM-ova preko OpenAI kompatibilne krajnje tačke

LM Studio takođe nudi OpenAI kompatibilnu krajnju tačku u vidu LM Studio servera. Ovo je već demonstrirano u agentnom radnom toku kodiranja sa Cline [ovde](../playbooks/vscode-qwen3-coder). Drugi uobičajen slučaj upotrebe je povezivanje LM Studio servera sa bilo kojom veb aplikacijom (React, Node.js, Python) slanjem standardnih HTTP zahteva na krajnju tačku za zaključivanje (inference).

Za podešavanje LM Studio servera, pratite sledeća uputstva:

1. Na levoj strani, kliknite na karticu `Developer` (ikonica komandne linije) ili pritisnite `Ctrl + 2`, a zatim kliknite na `Server Settings`.  
2. (Opciono): Ako želite da servirate model preko svoje lokalne mreže (LAN), označite `Serve on Local Network`. Ako želite da ga koristite sa veb sajtom ili za opsežno pozivanje unutar VS Code-a, označite `Enable CORS`. 
3. U gornjem levom uglu, proverite da li server radi tako što ćete kliknuti na dugme za prebacivanje pored `Status`.
4. Sada će raditi OpenAI kompatibilna krajnja tačka. Adresa je obično http://127.0.0.1:1234  
5. Ako model već nije učitan, možete ga učitati klikom na `Load Model` i praćenjem ranije opisanih koraka. 

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


Ovaj model će sada biti dostupan preko LM Studio Server krajnje tačke i podržavaće OpenAI krajnje tačke, uključujući:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Primer: Pingovanje vašeg endpoint-a
Pošto smo upravo kreirali OpenAI Compatible endpoint, hajde da vidimo kako da ga integrišemo u razvojno okruženje za Python (kao što je VSCode) i koristimo naš sistem kao lokalnog API Provider-a.

1. Kreirajte Python virtuelno okruženje:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Dodelite vašem korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
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
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Korisnicima Windows-a možda će biti potrebno da izmene svoju PowerShell Execution Policy (npr.
    > tako što će je postaviti na RemoteSigned ili Unrestricted) pre pokretanja pojedinih Powershell komandi.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Korisnicima Windows-a možda će biti potrebno da izmene svoju PowerShell Execution Policy (npr.
    > tako što će je postaviti na RemoteSigned ili Unrestricted) pre pokretanja pojedinih Powershell komandi.

<!-- @device:end -->
<!-- @os:end -->

2. Instalirajte OpenAI paket
    ```bash
    pip install openai
    ```

3. Pokrenite sledeću skriptu da biste pingovali endpoint koji smo upravo kreirali.
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

#### (Opciono): Prebacivanje između Runtime-ova

1. Pritisnite `Ctrl + Shift + R` na tastaturi. Alternativno, kliknite na karticu `Discover` (lupa) na levoj strani, a zatim kliknite na `Runtime` u iskačućem prozoru.   
2. Zatim treba da vidite `Runtime Selections`, gde padajući meni možete koristiti za promenu runtime-a.


## Sledeći koraci

- **Integracija sopstvene aplikacije**: Integrišite sopstvene Python skripte ili aplikacije koristeći lokalni OpenAI-compatible API.
- **Napredni front-end-ovi**: Povežite moćne interfejse poput Open WebUI sa vašim serverom radi istorije razgovora i upravljanja personama.

Za dodatnu dokumentaciju, posetite: https://lmstudio.ai/docs/developer