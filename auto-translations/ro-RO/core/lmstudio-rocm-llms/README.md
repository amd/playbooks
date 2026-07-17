<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală

LM Studio este un wrapper GUI puternic pentru [llama.cpp](https://github.com/ggml-org/llama.cpp) și oferă, de asemenea, un [endpoint compatibil OpenAI](https://lmstudio.ai/docs/developer/openai-compat) pentru servirea modelelor locale. LM Studio oferă o interfață simplă, dar puternică, pentru descărcarea și implementarea ușoară a modelelor. LM Studio oferă atât backend-uri Vulkan, cât și AMD ROCm™ software (numite runtime-uri) pentru utilizatorii AMD.


## Ce vei învăța
- Cum să configurezi și să utilizezi LM Studio pentru a valorifica hardware-ul local
- Testarea și gestionarea LLM-urilor într-un mediu complet offline
- Servirea modelelor prin API compatibil OpenAI pentru a alimenta fluxuri de lucru și aplicații personalizate


## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificarea actualizărilor de software

<!-- @os:linux -->
> **Notă**: Poți instala VS Code prin AMD Ryzen™ AI Developer Center. Pentru LM Studio, urmează instrucțiunile de instalare de mai jos.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Dacă VS Code sau LM Studio nu este instalat, le poți instala din AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor software

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Descărcarea modelelor

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

## Conversație cu un LLM
Află cum să începi o conversație cu un LLM de nivel ChatGPT complet local.

1. Deschide LMStudio.
2. Apasă `Ctrl + L` pentru a deschide Model Loader, selectează `Manually choose model load parameters` și fă clic pe `${model_name}`
3. Asigură-te că opțiunea „show advanced settings" este bifată.
4. Modifică `Context Length` după dorință. O lungime mai mare a contextului înseamnă mai multă memorie pentru model, dar mai multă memorie de sistem utilizată. Recomandat pentru acest playbook este 4096.
5. Asigură-te că `GPU Offload` este setat la maximum și că `Flash Attention` este activat (Cache Quantizations poate rămâne dezactivat)
6. Bifează `Remember settings` și fă clic pe `Load Model`.
7. Dacă nu ești în fereastra de chat, apasă `Ctrl + 1` sau fă clic pe butonul 👾 din colțul din stânga sus al ecranului.
8. Trimite un mesaj și începe să interacționezi cu modelul!

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

> **Sfat**: Lungimea contextului se referă la memoria modelului. Flash attention îmbunătățește viteza de procesare reducând în același timp utilizarea memoriei. GPU Offload transferă calculul către placa grafică pentru răspunsuri mai rapide.

## Servirea LLM-urilor printr-un endpoint compatibil OpenAI

LM Studio oferă, de asemenea, un endpoint compatibil OpenAI sub forma LM Studio Server. Acesta a fost deja demonstrat într-un flux de lucru de codare agentică cu Cline [aici](../playbooks/vscode-qwen3-coder). Un alt caz de utilizare frecvent este conectarea LM Studio Server la orice aplicație web (React, Node.js, Python) prin trimiterea de cereri HTTP standard către endpoint-ul de inferență.

Pentru a configura LM Studio Server, urmează instrucțiunile de mai jos:

1. Pe partea stângă, fă clic pe fila `Developer` (pictograma liniei de comandă) sau `Ctrl + 2`, apoi fă clic pe `Server Settings`.
2. (Opțional): Dacă dorești să servești modelul în rețeaua LAN, bifează `Serve on Local Network`. Dacă dorești să îl utilizezi cu un site web sau apeluri extinse în VS Code, bifează `Enable CORS`.
3. În colțul din stânga sus, asigură-te că serverul rulează făcând clic pe butonul de comutare din fața `Status`.
4. Un endpoint compatibil OpenAI va rula acum. Adresa este de obicei la http://127.0.0.1:1234
5. Dacă un model nu este deja încărcat, îl poți încărca făcând clic pe `Load Model` și urmând pașii menționați anterior.

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


Acest model va fi acum accesibil prin endpoint-ul LM Studio Server și va suporta endpoint-urile OpenAI, inclusiv:

| Endpoint | Metodă | Documentație |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Exemplu: Testarea endpoint-ului
Tocmai am creat endpoint-ul compatibil OpenAI; să vedem cum să îl integrăm într-un mediu de dezvoltare Python (cum ar fi VSCode) și să utilizăm sistemul ca furnizor local de API.

1. Creează un mediu virtual Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Pe Linux, deschide un terminal în directorul ales și urmează comenzile pentru a crea un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Acordă utilizatorului tău acces la dispozitivele GPU** (deconectează-te și reconectează-te pentru ca modificarea să intre în vigoare):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Pe Linux, deschide un terminal în directorul ales și urmează comenzile pentru a crea un venv.
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
    Pe Windows, deschide un terminal în directorul ales și urmează comenzile pentru a crea un venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Sfat**: Utilizatorii Windows poate fi necesar să modifice politica de execuție PowerShell (de ex.
    > setând-o la RemoteSigned sau Unrestricted) înainte de a rula unele comenzi Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Pe Windows, deschide un terminal în directorul ales și urmează comenzile pentru a crea un venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Sfat**: Utilizatorii Windows poate fi necesar să modifice politica de execuție PowerShell (de ex.
    > setând-o la RemoteSigned sau Unrestricted) înainte de a rula unele comenzi Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Instalează pachetul OpenAI
    ```bash
    pip install openai
    ```

3. Rulează următorul script pentru a testa endpoint-ul pe care tocmai l-am creat.
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

#### (Opțional): Schimbarea între runtime-uri

1. Apasă `Ctrl + Shift + R` pe tastatură. Alternativ, fă clic pe fila `Discover` (Lupă) din partea stângă, apoi fă clic pe `Runtime` în fereastra pop-up.
2. Ar trebui să vezi `Runtime Selections`, unde meniul derulant poate fi utilizat pentru a schimba runtime-ul.


## Pași următori

- **Integrarea aplicațiilor personalizate**: Integrează propriile scripturi sau aplicații Python folosind API-ul local compatibil OpenAI.
- **Frontend-uri avansate**: Conectează interfețe puternice precum Open WebUI la serverul tău pentru gestionarea istoricului conversațiilor și a personajelor.

Pentru mai multă documentație, vizitează: https://lmstudio.ai/docs/developer