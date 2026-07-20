<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more prikazati. Za pravilen predogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Pregled

LM Studio je zmogljiv grafični vmesnik za [llama.cpp](https://github.com/ggml-org/llama.cpp), ki prav tako omogoča [končno točko, skladno z OpenAI](https://lmstudio.ai/docs/developer/openai-compat) za lokalno strežbo modelov. LM Studio ponuja enostaven, a zmogljiv vmesnik za preprosto prenašanje in uvajanje modelov. LM Studio za uporabnike AMD ponuja tako Vulkan kot tudi AMD ROCm™ programski zaledji (imenovani izvajalno okolje oziroma runtime).


## Kaj se boste naučili
- Kako konfigurirati in uporabljati LM Studio za izkoriščanje lokalne strojne opreme
- Testiranje in upravljanje LLM-jev v popolnoma nepovezanem (offline) okolju
- Strežba modelov prek OpenAI Compatible API za podporo prilagojenim delovnim tokovom in aplikacijam


## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @os:linux -->
> **Opomba**: VS Code lahko namestite prek AMD Ryzen™ AI Developer Center. Za LM Studio sledite spodnjim navodilom za namestitev.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba**: Če VS Code ali LM Studio nista nameščena, ju lahko namestite prek AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Nameščanje predpogojev programske opreme

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Prenašanje modelov

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

## Pogovarjanje z LLM
Naučite se, kako začeti pogovor z LLM-jem kakovosti ChatGPT popolnoma lokalno.  

1. Odprite LMStudio. 
2. Pritisnite `Ctrl + L`, da odprete nalagalnik modelov (Model Loader), izberite `Manually choose model load parameters` in kliknite na `${model_name}`
3. Prepričajte se, da je označeno »show advanced settings«.  
4. Spremenite `Context Length`, kot želite. Večja dolžina konteksta pomeni več pomnilnika modela, vendar tudi večjo porabo sistemskega pomnilnika. Za ta priročnik je priporočena vrednost 4096.
5. Prepričajte se, da je `GPU Offload` nastavljen na najvišjo vrednost in da je `Flash Attention` vklopljen (kvantizacije predpomnilnika lahko ostanejo izklopljene)
6. Označite `Remember settings` in kliknite `Load Model`.
7. Če niste v pogovornem oknu, pritisnite `Ctrl + 1` ali kliknite na gumb 👾 v zgornjem levem kotu zaslona.
8. Pošljite sporočilo in začnite komunicirati z modelom!

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

> **Nasvet**: Dolžina konteksta se nanaša na pomnilnik modela. Flash attention izboljša hitrost obdelave in obenem zmanjša porabo pomnilnika. GPU Offload prenese računske operacije na grafično kartico za hitrejše odzive.

## Strežba LLM-jev prek končne točke, skladne z OpenAI

LM Studio prav tako ponuja končno točko, skladno z OpenAI, v obliki LM Studio Server. To je bilo že prikazano v agentnem delovnem toku za kodiranje s Cline [tukaj](../playbooks/vscode-qwen3-coder). Drug pogost primer uporabe je povezovanje LM Studio Server s katero koli spletno aplikacijo (React, Node.js, Python) s pošiljanjem standardnih zahtevkov HTTP na sklepalno končno točko.

Za nastavitev LM Studio Server sledite naslednjim navodilom:

1. Na levi strani kliknite na zavihek `Developer` (ikona ukazne vrstice) ali pritisnite `Ctrl + 2` in nato kliknite `Server Settings`.  
2. (Neobvezno): Če želite model streči po vašem lokalnem omrežju (LAN), označite `Serve on Local Network`. Če ga želite uporabljati s spletnim mestom ali za obsežno klicanje znotraj VS Code, označite `Enable CORS`. 
3. V zgornjem levem kotu se prepričajte, da strežnik teče, tako da kliknete preklopni gumb pred `Status`.
4. Zdaj bo delovala končna točka, skladna z OpenAI. Naslov je običajno http://127.0.0.1:1234  
5. Če model še ni naložen, ga lahko naložite s klikom na `Load Model` in sledenjem prej omenjenim korakom. 

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


Ta model bo zdaj dostopen prek končne točke LM Studio Server in bo podpiral končne točke OpenAI, vključno z:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Primer: preverjanje delovanja vaše končne točke (Endpoint)
Ko smo pravkar ustvarili končno točko, združljivo z OpenAI, si oglejmo, kako to integrirati v razvojno okolje za Python (kot je VSCode) in uporabiti vaš sistem kot lokalnega ponudnika API-ja.

1. Ustvarite virtualno okolje Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    V sistemu Linux odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Vašemu uporabniku omogočite dostop do naprav GPU** (za uveljavitev se odjavite in ponovno prijavite):

```bash
sudo usermod -aG render,video $LOGNAME
```

    V sistemu Linux odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje venv.
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
    V sistemu Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Nasvet**: uporabniki sistema Windows bodo morda morali spremeniti svoj izvedbeni pravilnik PowerShell (Execution Policy) (npr.
    > ga nastaviti na RemoteSigned ali Unrestricted), preden bodo lahko zagnali nekatere ukaze Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    V sistemu Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Nasvet**: uporabniki sistema Windows bodo morda morali spremeniti svoj izvedbeni pravilnik PowerShell (Execution Policy) (npr.
    > ga nastaviti na RemoteSigned ali Unrestricted), preden bodo lahko zagnali nekatere ukaze Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Namestite paket OpenAI
    ```bash
    pip install openai
    ```

3. Zaženite naslednji skript za preverjanje delovanja končne točke, ki smo jo pravkar ustvarili.
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

#### (Neobvezno): preklapljanje med izvajalnimi okolji (Runtimes)

1. Pritisnite `Ctrl + Shift + R` na tipkovnici. Druga možnost je, da kliknete zavihek `Discover` (povečevalno steklo) na levi strani in nato v pojavnem oknu kliknete `Runtime`.
2. Prikazale se vam bodo `Runtime Selections`, kjer lahko z spustnim menijem spremenite izvajalno okolje.


## Naslednji koraki

- **Integracija lastnih aplikacij**: integrirajte svoje lastne Python skripte ali aplikacije z uporabo lokalnega API-ja, združljivega z OpenAI.
- **Napredni vmesniki**: povežite zmogljive vmesnike, kot je Open WebUI, s svojim strežnikom za zgodovino klepetov in upravljanje profilov.

Za dodatno dokumentacijo obiščite: https://lmstudio.ai/docs/developer