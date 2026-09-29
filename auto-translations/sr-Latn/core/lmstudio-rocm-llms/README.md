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

LM Studio je moćan omotač zasnovan na GUI-ju za [llama.cpp](https://github.com/ggml-org/llama.cpp) i takođe pruža [OpenAI kompatibilan endpoint](https://lmstudio.ai/docs/developer/openai-compat) za lokalno posluživanje modela. LM Studio pruža jednostavan, ali moćan interfejs za lako preuzimanje i implementaciju modela. LM Studio nudi i Vulkan i AMD ROCm™ softverske pozadinske sisteme (nazvane runtime-ovi) za AMD korisnike.


## Šta ćete naučiti
- Kako da konfigurišete i koristite LM Studio da biste iskoristili svoj lokalni hardver
- Testiranje i upravljanje LLM-ovima u potpuno offline okruženju
- Posluživanje modela putem OpenAI kompatibilnog API-ja za pokretanje prilagođenih radnih tokova i aplikacija


<!-- @device:halo_box,halo,stx,krk -->
## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Provera softverskih ažuriranja

<!-- @os:linux -->
> **Napomena**: VS Code možete instalirati preko AMD Ryzen™ AI Developer Center-a. Za LM Studio, pratite uputstva za instalaciju u nastavku.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Ako VS Code ili LM Studio nisu instalirani, možete ih instalirati sa AMD Ryzen™ AI Developer Center-a. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje softverskih preduslova

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
Naučite kako da započnete ćaskanje sa LLM-om kvaliteta ChatGPT-a potpuno lokalno.  

1. Otvorite LMStudio. 
2. Pritisnite `Ctrl + L` da otvorite Model Loader, izaberite `Manually choose model load parameters`, i kliknite na `${model_name}`
3. Proverite da li je opcija „show advanced settings“ uključena.  
4. Promenite `Context Length` po želji. Veća dužina konteksta znači veću memoriju modela, ali i veće korišćenje sistemske memorije. Za ovaj playbook se preporučuje 4096.
5. Proverite da je `GPU Offload` podešen na maksimum i da je `Flash Attention` uključen (Cache Quantizations mogu ostati isključeni)
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

## Posluživanje LLM-ova putem OpenAI kompatibilnog endpoint-a

LM Studio takođe nudi OpenAI kompatibilan endpoint u obliku LM Studio Server-a. Ovo je već demonstrirano u agentskom radnom toku kodiranja sa Cline-om [ovde](../playbooks/vscode-qwen3-coder). Još jedan uobičajen slučaj upotrebe je povezivanje LM Studio Server-a sa bilo kojom veb aplikacijom (React, Node.js, Python) slanjem standardnih HTTP zahteva ka inference endpoint-u.

Da biste podesili LM Studio Server, pratite sledeća uputstva:

1. Sa leve strane kliknite na karticu `Developer` (ikonica komandne linije) ili `Ctrl + 2`, a zatim kliknite na `Server Settings`.  
2. (Opciono): Ako želite da poslužujete model preko svoje lokalne mreže (LAN), označite `Serve on Local Network`. Ako želite da ga koristite sa veb-sajtom ili za opsežno pozivanje unutar VS Code-a, označite `Enable CORS`. 
3. U gornjem levom uglu, proverite da li je server pokrenut klikom na prekidač ispred `Status`.
4. Sada će biti pokrenut OpenAI kompatibilan endpoint. Adresa je obično http://127.0.0.1:1234  
5. Ako model još uvek nije učitan, možete ga učitati klikom na `Load Model` i praćenjem prethodno navedenih koraka. 

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


Ovaj model će sada biti dostupan preko LM Studio Server endpoint-a i podržavaće OpenAI endpoint-e, uključujući:

| Endpoint | Metod | Dokumentacija |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Primer: Testiranje veze sa vašim Endpoint-om
Nakon što smo kreirali OpenAI Compatible endpoint, pogledajmo kako da ga integrišemo u Python razvojno okruženje (kao što je VSCode) i koristimo vaš sistem kao lokalnog API provajdera. 

1. Kreirajte Python virtuelno okruženje:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da kreirate venv.
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

    Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da kreirate venv.
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
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da kreirate venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Korisnici Windows-a možda će morati da izmene svoju PowerShell Execution Policy (npr.
    > postavljajući je na RemoteSigned ili Unrestricted) pre pokretanja pojedinih PowerShell komandi.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da kreirate venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Korisnici Windows-a možda će morati da izmene svoju PowerShell Execution Policy (npr.
    > postavljajući je na RemoteSigned ili Unrestricted) pre pokretanja pojedinih PowerShell komandi.

<!-- @device:end -->
<!-- @os:end -->

2. Instalirajte OpenAI paket
    ```bash
    pip install openai
    ```

3. Pokrenite sledeći skript da testirate vezu sa endpoint-om koji smo upravo kreirali.
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

#### (Opciono): Prebacivanje između Runtime okruženja

1. Pritisnite `Ctrl + Shift + R` na tastaturi. Alternativno, kliknite na karticu `Discover` (Lupa) na levoj strani, a zatim kliknite na `Runtime` u iskačućem prozoru.   
2. Zatim biste trebali videti `Runtime Selections`, gde se padajući meni može koristiti za promenu runtime okruženja.


## Sledeći koraci

- **Integracija sopstvenih aplikacija**: Integrišite sopstvene Python skripte ili aplikacije koristeći lokalni OpenAI-compatible API.
- **Napredni frontend-i**: Povežite moćne interfejse poput Open WebUI sa vašim serverom radi istorije razgovora i upravljanja personama.

Za više dokumentacije, posetite: https://lmstudio.ai/docs/developer