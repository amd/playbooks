<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može da prikaže. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->

## Pregled

LM Studio je moćan omotač zasnovan na grafičkom korisničkom interfejsu za [llama.cpp](https://github.com/ggml-org/llama.cpp), a takođe pruža i [krajnju tačku kompatibilnu sa OpenAI](https://lmstudio.ai/docs/developer/openai-compat) za lokalno posluživanje modela. LM Studio pruža jednostavan, ali moćan interfejs za jednostavno preuzimanje i primenu modela. LM Studio nudi kako Vulkan tako i AMD ROCm™ softverske pozadinske sisteme (nazvane runtime-ovi) za AMD korisnike.


## Šta ćete naučiti
- Kako da konfigurišete i koristite LM Studio da biste iskoristili svoj lokalni hardver
- Testiranje i upravljanje LLM-ovima u potpuno offline okruženju
- Posluživanje modela putem OpenAI kompatibilnog API-ja za pokretanje prilagođenih radnih tokova i aplikacija


## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @os:linux -->
> **Napomena**: VS Code možete instalirati putem AMD Ryzen™ AI Developer Center-a. Za LM Studio pratite instalaciona uputstva ispod.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Ako VS Code ili LM Studio nisu instalirani, možete ih instalirati putem AMD Ryzen™ AI Developer Center-a. 
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
2. Pritisnite `Ctrl + L` da otvorite učitavač modela, izaberite `Manually choose model load parameters`, i kliknite na `${model_name}`
3. Proverite da li je opcija „show advanced settings“ označena.  
4. Promenite `Context Length` po želji. Veća dužina konteksta znači veću memoriju modela, ali i veću potrošnju sistemske memorije. Za ovaj priručnik se preporučuje 4096.
5. Proverite da je `GPU Offload` podešen na maksimum i da je `Flash Attention` uključen (Cache Quantizations mogu ostati isključeni)
6. Označite `Remember settings` i kliknite na `Load Model`.
7. Ako niste u prozoru za ćaskanje, pritisnite `Ctrl + 1` ili kliknite na dugme 👾 u gornjem levom uglu ekrana.
8. Pošaljite poruku i počnite da komunicirate sa modelom!

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

> **Savet**: Dužina konteksta se odnosi na memoriju modela. Flash attention poboljšava brzinu obrade uz smanjenje potrošnje memorije. GPU Offload prebacuje obradu na grafičku karticu radi bržih odgovora.

## Posluživanje LLM-ova putem OpenAI kompatibilne krajnje tačke

LM Studio takođe nudi krajnju tačku kompatibilnu sa OpenAI u vidu LM Studio Server-a. Ovo je već demonstrirano u radnom toku agentskog kodiranja sa Cline [ovde](../playbooks/vscode-qwen3-coder). Drugi čest slučaj upotrebe je povezivanje LM Studio Server-a sa bilo kojom veb aplikacijom (React, Node.js, Python) slanjem standardnih HTTP zahteva ka inferentnoj krajnjoj tački.

Da biste podesili LM Studio Server, koristite sledeća uputstva:

1. Na levoj strani kliknite na karticu `Developer` (ikona komandne linije) ili pritisnite `Ctrl + 2`, a zatim kliknite na `Server Settings`.  
2. (Opciono): Ako želite da poslužujete model preko svoje lokalne mreže, označite `Serve on Local Network`. Ako želite da ga koristite sa veb-sajtom ili opsežnim pozivanjem unutar VS Code-a, označite `Enable CORS`. 
3. U gornjem levom uglu, proverite da li je server pokrenut klikom na prekidač ispred natpisa `Status`.
4. Sada će raditi krajnja tačka kompatibilna sa OpenAI. Adresa je obično na http://127.0.0.1:1234  
5. Ako model nije već učitan, možete ga učitati klikom na `Load Model` i sledeći prethodno pomenute korake. 

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


Ovaj model će sada biti dostupan putem LM Studio Server krajnje tačke i podržavaće OpenAI krajnje tačke, uključujući:

| Krajnja tačka | Metod | Dokumentacija |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Primer: Pingovanje vašeg Endpoint-a
Pošto smo upravo kreirali OpenAI Compatible endpoint, hajde da vidimo kako da ga integrišete u razvojno okruženje za Python (kao što je VSCode) i koristite svoj sistem kao lokalnog API Provider-a.

1. Kreirajte Python virtuelno okruženje:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da biste kreirali venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Odobrite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da biste kreirali venv.
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
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da biste kreirali venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Windows korisnicima će možda biti potrebno da izmene svoju PowerShell Execution Policy (npr.
    > da je postave na RemoteSigned ili Unrestricted) pre pokretanja pojedinih Powershell komandi.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande da biste kreirali venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Windows korisnicima će možda biti potrebno da izmene svoju PowerShell Execution Policy (npr.
    > da je postave na RemoteSigned ili Unrestricted) pre pokretanja pojedinih Powershell komandi.

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

#### (Opciono): Menjanje između Runtime-ova

1. Pritisnite `Ctrl + Shift + R` na tastaturi. Alternativno, kliknite na karticu `Discover` (lupa) sa leve strane, a zatim kliknite na `Runtime` u iskačućem prozoru.
2. Zatim biste trebalo da vidite `Runtime Selections`, gde možete koristiti padajući meni da promenite runtime.


## Sledeći koraci

- **Integracija prilagođene aplikacije**: Integrišite sopstvene Python skripte ili aplikacije koristeći lokalni OpenAI-compatible API.
- **Napredni frontend-ovi**: Povežite moćne interfejse poput Open WebUI sa svojim serverom radi istorije čata i upravljanja personama.

Za više dokumentacije, posetite: https://lmstudio.ai/docs/developer