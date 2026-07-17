<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

LM Studio je moćan GUI wrapper za [llama.cpp](https://github.com/ggml-org/llama.cpp) i takođe pruža [OpenAI kompatibilan endpoint](https://lmstudio.ai/docs/developer/openai-compat) za lokalno posluživanje modela. LM Studio pruža jednostavan, ali moćan interfejs za lako preuzimanje i postavljanje modela. LM Studio nudi i Vulkan i AMD ROCm™ softverske bekende (nazvane runtimeovi) za AMD korisnike.


## Šta ćete naučiti
- Kako da konfigurišete i koristite LM Studio za iskorišćavanje lokalnog hardvera
- Testiranje i upravljanje LLM-ovima u potpuno oflajn okruženju
- Posluživanje modela putem OpenAI kompatibilnog API-ja za pokretanje prilagođenih tokova rada i aplikacija


## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera softverskih ažuriranja

<!-- @os:linux -->
> **Napomena**: Možete instalirati VS Code putem AMD Ryzen™ AI Developer Center-a. Za LM Studio, pratite uputstva za instalaciju u nastavku.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena**: Ako VS Code ili LM Studio nisu instalirani, možete ih instalirati iz AMD Ryzen™ AI Developer Center-a.
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

## Razgovor sa LLM-om
Naučite kako da počnete da razgovarate sa LLM-om na nivou ChatGPT-a potpuno lokalno.

1. Otvorite LMStudio.
2. Pritisnite `Ctrl + L` da otvorite Model Loader, izaberite `Manually choose model load parameters` i kliknite na `${model_name}`
3. Proverite da je opcija "show advanced settings" označena.
4. Promenite `Context Length` po želji. Veća dužina konteksta znači više memorije modela, ali i više korišćene sistemske memorije. Preporučeno za ovaj playbook je 4096.
5. Proverite da je `GPU Offload` postavljen na maksimum i da je `Flash Attention` uključen (Cache Quantizations može ostati isključeno)
6. Označite `Remember settings` i kliknite na `Load Model`.
7. Ako niste u prozoru za razgovor, pritisnite `Ctrl + 1` ili kliknite na dugme 👾 u gornjem levom uglu ekrana.
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

> **Savet**: Dužina konteksta odnosi se na memoriju modela. Flash attention poboljšava brzinu obrade uz smanjenje korišćenja memorije. GPU Offload prebacuje računanje na grafičku karticu radi bržih odgovora.

## Posluživanje LLM-ova putem OpenAI kompatibilnog endpointa

LM Studio takođe nudi OpenAI kompatibilan endpoint u obliku LM Studio Server-a. Ovo je već demonstrirano u agentnom toku rada za kodiranje sa Cline-om [ovde](../playbooks/vscode-qwen3-coder). Još jedan čest slučaj upotrebe je povezivanje LM Studio Server-a sa bilo kojom veb aplikacijom (React, Node.js, Python) slanjem standardnih HTTP zahteva na endpoint za inferenciju.

Da biste podesili LM Studio Server, koristite sledeća uputstva:

1. Na levoj strani, kliknite na karticu `Developer` (ikona komandne linije) ili `Ctrl + 2`, a zatim kliknite na `Server Settings`.
2. (Opciono): Ako želite da poslužujete model preko vaše LAN mreže, označite `Serve on Local Network`. Ako želite da koristite sa veb sajtom ili opsežnim pozivanjem unutar VS Code, označite `Enable CORS`.
3. U gornjem levom uglu, proverite da server radi klikom na dugme za prebacivanje ispred `Status`.
4. OpenAI kompatibilan endpoint će sada biti pokrenut. Adresa je obično na http://127.0.0.1:1234
5. Ako model već nije učitan, možete ga učitati klikom na `Load Model` i praćenjem prethodno pomenutih koraka.

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


Ovaj model će sada biti dostupan putem LM Studio Server endpointa i podržavaće OpenAI endpointe uključujući:

| Endpoint | Metod | Dokumentacija |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Primer: Pingovanje vašeg endpointa
Pošto smo upravo kreirali OpenAI kompatibilan endpoint, pogledajmo kako da ga integrišemo u Python razvojno okruženje (kao što je VSCode) i koristimo vaš sistem kao lokalni API provajder.

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
**Dodelite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

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

    > **Savet**: Korisnici Windows-a možda će morati da izmene svoju PowerShell politiku izvršavanja (npr.
    > postavljanjem na RemoteSigned ili Unrestricted) pre pokretanja nekih Powershell komandi.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Savet**: Korisnici Windows-a možda će morati da izmene svoju PowerShell politiku izvršavanja (npr.
    > postavljanjem na RemoteSigned ili Unrestricted) pre pokretanja nekih Powershell komandi.

<!-- @device:end -->
<!-- @os:end -->

2. Instalirajte OpenAI paket
    ```bash
    pip install openai
    ```

3. Pokrenite sledeću skriptu da pingujete endpoint koji smo upravo kreirali.
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

#### (Opciono): Prebacivanje između runtimeova

1. Pritisnite `Ctrl + Shift + R` na tastaturi. Alternativno, kliknite na karticu `Discover` (lupa) na levoj strani, a zatim kliknite na `Runtime` u iskačućem prozoru.
2. Trebalo bi da vidite `Runtime Selections`, gde se padajući meni može koristiti za promenu runtimea.


## Sledeći koraci

- **Integracija prilagođenih aplikacija**: Integrišite sopstvene Python skripte ili aplikacije koristeći lokalni OpenAI kompatibilan API.
- **Napredni frontendovi**: Povežite moćne interfejse poput Open WebUI sa vašim serverom za upravljanje istorijom razgovora i personama.

Za više dokumentacije, posetite: https://lmstudio.ai/docs/developer