<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

LM Studio je zmogljiv grafični vmesnik za [llama.cpp](https://github.com/ggml-org/llama.cpp) in ponuja tudi [končno točko, skladno z OpenAI](https://lmstudio.ai/docs/developer/openai-compat) za lokalno strežbo modelov. LM Studio ponuja preprost, a zmogljiv vmesnik za enostavno prenašanje in uvajanje modelov. LM Studio za uporabnike AMD ponuja tako Vulkan kot AMD ROCm™ programske zaledne sisteme (imenovane runtime).


## Kaj se boste naučili
- Kako konfigurirati in uporabljati LM Studio za izkoriščanje lokalne strojne opreme
- Testiranje in upravljanje jezikovnih modelov (LLM) v popolnoma brezpovezavnem okolju
- Strežba modelov prek API-ja, združljivega z OpenAI, za pogon prilagojenih delovnih tokov in aplikacij


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

## Namestitev potrebne programske opreme

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Prenos modelov

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

## Klepetanje z jezikovnim modelom
Naučite se, kako začeti klepetati z jezikovnim modelom (LLM) kakovosti ChatGPT popolnoma lokalno.  

1. Odprite LMStudio. 
2. Pritisnite `Ctrl + L`, da odprete nalagalnik modela, izberite `Manually choose model load parameters` in kliknite na `${model_name}`
3. Prepričajte se, da je označeno "show advanced settings".  
4. Po želji spremenite `Context Length`. Večja dolžina konteksta pomeni več pomnilnika modela, vendar tudi večjo porabo sistemskega pomnilnika. Priporočena vrednost za ta priročnik je 4096.
5. Prepričajte se, da je `GPU Offload` nastavljen na maksimum in da je `Flash Attention` vklopljen (kvantizacije predpomnilnika lahko ostanejo izklopljene)
6. Označite `Remember settings` in kliknite `Load Model`.
7. Če niste v oknu za klepet, pritisnite `Ctrl + 1` ali kliknite na gumb 👾 v zgornjem levem kotu zaslona.
8. Pošljite sporočilo in začnite komunicirati z modelom!

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

> **Nasvet**: Dolžina konteksta se nanaša na pomnilnik modela. Flash attention izboljša hitrost obdelave in hkrati zmanjša porabo pomnilnika. GPU Offload prenese izračune na grafično kartico za hitrejše odzive.

## Strežba jezikovnih modelov prek končne točke, združljive z OpenAI

LM Studio ponuja tudi končno točko, skladno z OpenAI, v obliki strežnika LM Studio Server. To je bilo že prikazano v agentnem delovnem toku kodiranja s Cline [tukaj](../playbooks/vscode-qwen3-coder). Drug pogost primer uporabe je povezovanje strežnika LM Studio Server s katero koli spletno aplikacijo (React, Node.js, Python) s pošiljanjem standardnih zahtev HTTP na sklepalno končno točko.

Za nastavitev strežnika LM Studio Server uporabite naslednja navodila:

1. Na levi strani kliknite na zavihek `Developer` (ikona ukazne vrstice) ali pritisnite `Ctrl + 2` in nato kliknite na `Server Settings`.  
2. (Neobvezno): Če želite streči model prek svojega lokalnega omrežja (LAN), označite `Serve on Local Network`. Če ga želite uporabljati s spletno stranjo ali za obsežno klicanje znotraj VS Code, označite `Enable CORS`. 
3. V zgornjem levem kotu se prepričajte, da strežnik teče, tako da kliknete na preklopni gumb pred `Status`.
4. Zdaj bo tekla končna točka, skladna z OpenAI. Naslov je običajno http://127.0.0.1:1234  
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


Ta model bo zdaj dostopen prek končne točke strežnika LM Studio Server in bo podpiral končne točke OpenAI, vključno z:

| Končna točka | Metoda | Dokumentacija |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Primer: Preverjanje povezave z vašo končno točko
Ko smo pravkar ustvarili končno točko, združljivo z OpenAI, si poglejmo, kako to integrirati v razvojno okolje za Python (na primer VSCode) in uporabiti vaš sistem kot lokalnega ponudnika API.

1. Ustvarite virtualno okolje za Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    V Linuxu odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv).
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Dodelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev se morate odjaviti in ponovno prijaviti):

```bash
sudo usermod -aG render,video $LOGNAME
```

    V Linuxu odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv).
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
    V Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv).
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti svoj izvedbeni pravilnik PowerShell (Execution Policy) (npr.
    > nastaviti ga na RemoteSigned ali Unrestricted), preden zaženejo nekatere ukaze PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    V Windows odprite terminal v mapi po vaši izbiri in sledite ukazom za ustvarjanje virtualnega okolja (venv).
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Nasvet**: Uporabniki sistema Windows bodo morda morali spremeniti svoj izvedbeni pravilnik PowerShell (Execution Policy) (npr.
    > nastaviti ga na RemoteSigned ali Unrestricted), preden zaženejo nekatere ukaze PowerShell.

<!-- @device:end -->
<!-- @os:end -->

2. Namestite paket OpenAI
    ```bash
    pip install openai
    ```

3. Zaženite naslednji skript, da preverite povezavo s končno točko, ki smo jo pravkar ustvarili.
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

#### (Neobvezno): Preklapljanje med izvajalnimi okolji (Runtimes)

1. Na tipkovnici pritisnite `Ctrl + Shift + R`. Lahko pa tudi kliknete na zavihek `Discover` (ikona povečevalnega stekla) na levi strani in nato v pojavnem oknu kliknete `Runtime`.
2. Nato bi morali videti `Runtime Selections`, kjer lahko z spustnim menijem spremenite izvajalno okolje.


## Naslednji koraki

- **Integracija po meri**: Integrirajte lastne skripte ali aplikacije Python z uporabo lokalnega API-ja, združljivega z OpenAI.
- **Napredni vmesniki**: Povežite zmogljive vmesnike, kot je Open WebUI, s svojim strežnikom za zgodovino klepetov in upravljanje osebnosti.

Za več dokumentacije obiščite: https://lmstudio.ai/docs/developer