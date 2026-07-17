<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

LM Studio è un potente wrapper con interfaccia grafica per [llama.cpp](https://github.com/ggml-org/llama.cpp) e fornisce anche un [endpoint compatibile con OpenAI](https://lmstudio.ai/docs/developer/openai-compat) per il serving di modelli in locale. LM Studio offre un'interfaccia semplice ma potente per scaricare e distribuire modelli con facilità. LM Studio mette a disposizione degli utenti AMD sia il backend Vulkan che il backend AMD ROCm™ (chiamati runtime).


## Cosa Imparerai
- Come configurare e utilizzare LM Studio per sfruttare l'hardware locale
- Testare e gestire LLM in un ambiente completamente offline
- Servire modelli tramite API compatibile con OpenAI per alimentare flussi di lavoro e applicazioni personalizzate


## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software

<!-- @os:linux -->
> **Nota**: Puoi installare VS Code tramite AMD Ryzen™ AI Developer Center. Per LM Studio, segui le istruzioni di installazione riportate di seguito.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Se VS Code o LM Studio non sono installati, puoi installarli dall'AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Download dei Modelli

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

## Chattare con un LLM
Scopri come iniziare a chattare con un LLM di livello ChatGPT completamente in locale.

1. Apri LMStudio.
2. Premi `Ctrl + L` per aprire il Model Loader, seleziona `Manually choose model load parameters` e clicca su `${model_name}`
3. Assicurati che "show advanced settings" sia selezionato.
4. Modifica il `Context Length` come desiderato. Una lunghezza del contesto maggiore significa più memoria per il modello, ma un maggiore utilizzo della memoria di sistema. Per questo playbook si consiglia 4096.
5. Assicurati che `GPU Offload` sia impostato al massimo e che `Flash Attention` sia attivo (le Cache Quantizations possono rimanere disattivate)
6. Seleziona `Remember settings` e clicca su `Load Model`.
7. Se non sei nella finestra di chat, premi `Ctrl + 1` o clicca sul pulsante 👾 in alto a sinistra dello schermo.
8. Invia un messaggio e inizia a interagire con il modello!

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

> **Suggerimento**: La lunghezza del contesto si riferisce alla memoria del modello. Flash attention migliora la velocità di elaborazione riducendo l'utilizzo della memoria. GPU Offload trasferisce il calcolo alla scheda grafica per risposte più rapide.

## Servire LLM tramite un endpoint compatibile con OpenAI

LM Studio offre anche un endpoint compatibile con OpenAI sotto forma di LM Studio Server. Questo è già stato dimostrato in un flusso di lavoro di codifica agentiva con Cline [qui](../playbooks/vscode-qwen3-coder). Un altro caso d'uso comune è la connessione di LM Studio Server a qualsiasi applicazione web (React, Node.js, Python) inviando richieste HTTP standard all'endpoint di inferenza.

Per configurare LM Studio Server, segui le istruzioni seguenti:

1. Sul lato sinistro, clicca sulla scheda `Developer` (icona della riga di comando) oppure premi `Ctrl + 2`, quindi clicca su `Server Settings`.
2. (Facoltativo): Se vuoi servire il modello sulla tua LAN, seleziona `Serve on Local Network`. Se vuoi utilizzarlo con un sito web o con chiamate estese all'interno di VS Code, seleziona `Enable CORS`.
3. Nell'angolo in alto a sinistra, assicurati che il server sia in esecuzione cliccando sul pulsante di attivazione/disattivazione davanti a `Status`.
4. Sarà ora attivo un endpoint compatibile con OpenAI. L'indirizzo è tipicamente http://127.0.0.1:1234
5. Se un modello non è già caricato, puoi caricarlo cliccando su `Load Model` e seguendo i passaggi precedentemente descritti.

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


Questo modello sarà ora accessibile tramite l'endpoint LM Studio Server e supporterà gli endpoint OpenAI, tra cui:

| Endpoint | Metodo | Documentazione |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Esempio: Ping del tuo Endpoint
Dopo aver appena creato l'endpoint compatibile con OpenAI, vediamo come integrarlo in un ambiente di sviluppo Python (come VSCode) e utilizzare il tuo sistema come provider API locale.

1. Crea un ambiente virtuale Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Su Linux, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Concedi all'utente l'accesso ai dispositivi GPU** (esci e rientra affinché le modifiche abbiano effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Su Linux, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
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
    Su Windows, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Suggerimento**: Gli utenti Windows potrebbero dover modificare la PowerShell Execution Policy (ad esempio
    > impostandola su RemoteSigned o Unrestricted) prima di eseguire alcuni comandi Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Su Windows, apri un terminale nella directory di tua scelta e segui i comandi per creare un venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Suggerimento**: Gli utenti Windows potrebbero dover modificare la PowerShell Execution Policy (ad esempio
    > impostandola su RemoteSigned o Unrestricted) prima di eseguire alcuni comandi Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Installa il pacchetto OpenAI
    ```bash
    pip install openai
    ```

3. Esegui il seguente script per eseguire il ping dell'endpoint appena creato.
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

#### (Facoltativo): Passaggio tra Runtime

1. Premi `Ctrl + Shift + R` sulla tastiera. In alternativa, clicca sulla scheda `Discover` (Lente di ingrandimento) sul lato sinistro, quindi clicca su `Runtime` nel popup.
2. Dovresti quindi vedere `Runtime Selections`, dove il menu a tendina può essere utilizzato per cambiare il runtime.


## Passi Successivi

- **Integrazione di App Personalizzate**: Integra i tuoi script o applicazioni Python utilizzando l'API locale compatibile con OpenAI.
- **Frontend Avanzati**: Connetti interfacce potenti come Open WebUI al tuo server per la gestione della cronologia delle chat e dei profili.

Per ulteriore documentazione, visita: https://lmstudio.ai/docs/developer