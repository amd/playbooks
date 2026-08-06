<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală

LM Studio este un wrapper puternic bazat pe interfață grafică pentru [llama.cpp](https://github.com/ggml-org/llama.cpp) și oferă, de asemenea, un [endpoint compatibil OpenAI](https://lmstudio.ai/docs/developer/openai-compat) pentru servirea locală a modelelor. LM Studio oferă o interfață simplă, dar puternică, pentru a descărca și implementa cu ușurință modele. LM Studio oferă atât backend-uri (numite runtime-uri) Vulkan, cât și AMD ROCm™ software pentru utilizatorii AMD.


## Ce veți învăța
- Cum să configurați și să utilizați LM Studio pentru a valorifica hardware-ul dvs. local
- Testarea și gestionarea LLM-urilor într-un mediu complet offline
- Servirea modelelor printr-un API compatibil OpenAI pentru a alimenta fluxuri de lucru și aplicații personalizate


## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările software

<!-- @os:linux -->
> **Notă**: Puteți instala VS Code prin AMD Ryzen™ AI Developer Center. Pentru LM Studio, urmați instrucțiunile de instalare de mai jos.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă**: Dacă VS Code sau LM Studio nu sunt instalate, le puteți instala din AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare software

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
Aflați cum să începeți să conversați complet local cu un LLM de nivelul ChatGPT.  

1. Deschideți LMStudio. 
2. Apăsați `Ctrl + L` pentru a deschide Model Loader, selectați `Manually choose model load parameters`, apoi faceți clic pe `${model_name}`
3. Asigurați-vă că opțiunea „show advanced settings” este bifată.  
4. Modificați `Context Length` după cum doriți. O lungime de context mai mare înseamnă mai multă memorie pentru model, dar și un consum mai mare de memorie de sistem. Recomandat pentru acest playbook este 4096.
5. Asigurați-vă că `GPU Offload` este setat la maxim și că `Flash Attention` este activat (Cache Quantizations pot rămâne dezactivate)
6. Bifați `Remember settings` și faceți clic pe `Load Model`.
7. Dacă nu vă aflați în fereastra de chat, apăsați `Ctrl + 1` sau faceți clic pe butonul 👾 din partea din stânga sus a ecranului.
8. Trimiteți un mesaj și începeți să interacționați cu modelul!

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

> **Sfat**: Lungimea contextului se referă la memoria modelului. Flash attention îmbunătățește viteza de procesare, reducând în același timp consumul de memorie. GPU Offload transferă calculul către placa grafică pentru răspunsuri mai rapide.

## Servirea LLM-urilor printr-un endpoint compatibil OpenAI

LM Studio oferă, de asemenea, un endpoint compatibil OpenAI sub forma LM Studio Server. Acest lucru a fost deja demonstrat într-un flux de lucru de codare agentică cu Cline [aici](../playbooks/vscode-qwen3-coder). Un alt caz de utilizare comun este conectarea LM Studio Server la orice aplicație web (React, Node.js, Python) prin trimiterea de cereri HTTP standard către endpoint-ul de inferență.

Pentru a configura LM Studio Server, utilizați următoarele instrucțiuni:

1. În partea stângă, faceți clic pe fila `Developer` (pictograma liniei de comandă) sau apăsați `Ctrl + 2`, apoi faceți clic pe `Server Settings`.  
2. (Opțional): Dacă doriți să serviți modelul prin rețeaua dvs. locală (LAN), bifați `Serve on Local Network`. Dacă doriți să îl utilizați cu un site web sau cu apeluri extinse în VS Code, bifați `Enable CORS`. 
3. În colțul din stânga sus, asigurați-vă că serverul rulează făcând clic pe butonul comutator din fața etichetei `Status`.
4. Un endpoint compatibil OpenAI va rula acum. Adresa este de obicei http://127.0.0.1:1234  
5. Dacă un model nu este deja încărcat, îl puteți încărca făcând clic pe `Load Model` și urmând pașii menționați anterior. 

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


Acest model va fi acum accesibil prin endpoint-ul LM Studio Server și va suporta endpoint-uri OpenAI, inclusiv:

| Endpoint | Metodă | Documentație |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Exemplu: Testarea endpoint-ului dvs.
Acum că am creat endpoint-ul compatibil cu OpenAI, să vedem cum îl putem integra într-un mediu de dezvoltare Python (precum VSCode) și cum să folosim sistemul dvs. ca furnizor local de API.

1. Creați un mediu virtual Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Pe Linux, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Acordați utilizatorului dvs. acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca acest lucru să aibă efect):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Pe Linux, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv.
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
    Pe Windows, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Sfat**: Este posibil ca utilizatorii Windows să trebuiască să modifice Politica de Execuție PowerShell (de exemplu,
    > setând-o la RemoteSigned sau Unrestricted) înainte de a rula anumite comenzi Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Pe Windows, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Sfat**: Este posibil ca utilizatorii Windows să trebuiască să modifice Politica de Execuție PowerShell (de exemplu,
    > setând-o la RemoteSigned sau Unrestricted) înainte de a rula anumite comenzi Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Instalați pachetul OpenAI
    ```bash
    pip install openai
    ```

3. Rulați următorul script pentru a testa endpoint-ul pe care tocmai l-am creat.
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

#### (Opțional): Schimbarea între medii de execuție (Runtimes)

1. Apăsați `Ctrl + Shift + R` de pe tastatură. Alternativ, faceți clic pe fila `Discover` (Lupă) din partea stângă și apoi faceți clic pe `Runtime` în fereastra pop-up.   
2. Ar trebui să vedeți apoi `Runtime Selections`, unde meniul derulant poate fi folosit pentru a schimba mediul de execuție.


## Pașii următori

- **Integrare aplicație personalizată**: Integrați propriile scripturi sau aplicații Python folosind API-ul local compatibil cu OpenAI.
- **Interfețe avansate**: Conectați interfețe puternice precum Open WebUI la serverul dvs. pentru istoricul conversațiilor și gestionarea persoanelor.

Pentru mai multă documentație, vă rugăm să vizitați: https://lmstudio.ai/docs/developer