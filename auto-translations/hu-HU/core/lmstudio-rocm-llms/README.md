<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Az LM Studio egy hatékony GUI-alapú keretrendszer a [llama.cpp](https://github.com/ggml-org/llama.cpp) számára, és [OpenAI-kompatibilis végpontot](https://lmstudio.ai/docs/developer/openai-compat) is biztosít helyi modellkiszolgáláshoz. Az LM Studio egyszerű, de hatékony felületet kínál a modellek egyszerű letöltéséhez és telepítéséhez. Az LM Studio AMD felhasználók számára Vulkan és AMD ROCm™ szoftver háttérrendszereket (más néven futtatókörnyezeteket) is kínál.


## Mit fog megtanulni
- Hogyan konfigurálja és használja az LM Studio-t a helyi hardver kihasználásához
- LLM-ek tesztelése és kezelése teljesen offline környezetben
- Modellek kiszolgálása OpenAI-kompatibilis API-n keresztül egyéni munkafolyamatok és alkalmazások működtetéséhez


## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @os:linux -->
> **Megjegyzés**: A VS Code-ot az AMD Ryzen™ AI Developer Center-en keresztül telepítheti. Az LM Studio esetében kövesse az alábbi telepítési utasításokat.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ha a VS Code vagy az LM Studio nincs telepítve, az AMD Ryzen™ AI Developer Center-ből telepítheti őket.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Modellek letöltése

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

## Csevegés egy LLM-mel
Ismerje meg, hogyan kezdhet el csevegni egy ChatGPT-szintű LLM-mel teljesen helyi környezetben.

1. Nyissa meg az LMStudio-t.
2. Nyomja meg a `Ctrl + L` billentyűkombinációt a Model Loader megnyitásához, válassza a `Manually choose model load parameters` lehetőséget, majd kattintson a `${model_name}` elemre.
3. Győződjön meg arról, hogy a „show advanced settings" jelölőnégyzet be van jelölve.
4. Módosítsa a `Context Length` értékét igény szerint. A nagyobb kontexthossz több modellmemóriát jelent, de több rendszermemóriát is használ. Ehhez a playbook-hoz az ajánlott érték 4096.
5. Győződjön meg arról, hogy a `GPU Offload` maximumra van állítva, és a `Flash Attention` be van kapcsolva (a Cache Quantizations kikapcsolva maradhat).
6. Jelölje be a `Remember settings` opciót, majd kattintson a `Load Model` gombra.
7. Ha nem a csevegőablakban van, nyomja meg a `Ctrl + 1` billentyűkombinációt, vagy kattintson a 👾 gombra a képernyő bal felső sarkában.
8. Küldjön egy üzenetet, és kezdjen el interakcióba lépni a modellel!

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

> **Tipp**: A kontexthossz a modell memóriájára utal. A Flash Attention javítja a feldolgozási sebességet, miközben csökkenti a memóriahasználatot. A GPU Offload a számítást a grafikus kártyára helyezi át a gyorsabb válaszok érdekében.

## LLM-ek kiszolgálása OpenAI-kompatibilis végponton keresztül

Az LM Studio egy OpenAI-kompatibilis végpontot is kínál LM Studio Server formájában. Ezt már bemutatták egy agentic kódolási munkafolyamatban a Cline-nal [itt](../playbooks/vscode-qwen3-coder). Egy másik gyakori felhasználási eset az LM Studio Server csatlakoztatása bármely webalkalmazáshoz (React, Node.js, Python) szabványos HTTP-kérések küldésével az inferencia végponthoz.

Az LM Studio Server beállításához kövesse az alábbi utasításokat:

1. A bal oldalon kattintson a `Developer` fülre (parancssori ikon) vagy nyomja meg a `Ctrl + 2` billentyűkombinációt, majd kattintson a `Server Settings` elemre.
2. (Opcionális): Ha a modellt a helyi hálózaton szeretné kiszolgálni, jelölje be a `Serve on Local Network` opciót. Ha weboldallal vagy kiterjedt VS Code-on belüli hívásokkal szeretné használni, jelölje be az `Enable CORS` opciót.
3. A bal felső sarokban győződjön meg arról, hogy a szerver fut, a `Status` előtti kapcsológombra kattintva.
4. Egy OpenAI-kompatibilis végpont fog futni. A cím általában: http://127.0.0.1:1234
5. Ha még nincs modell betöltve, betöltheti a `Load Model` gombra kattintva, majd a korábban említett lépéseket követve.

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


Ez a modell mostantól elérhető lesz az LM Studio Server végponton keresztül, és az alábbi OpenAI végpontokat fogja támogatni:

| Végpont | Metódus | Dokumentáció |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Példa: A végpont pingelése
Most, hogy létrehoztuk az OpenAI-kompatibilis végpontot, nézzük meg, hogyan integrálható ez egy Python fejlesztői környezetbe (például VSCode-ba), és hogyan használható a rendszer helyi API-szolgáltatóként.

1. Hozzon létre egy Python virtuális környezetet:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Linuxon nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat a venv létrehozásához.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (a hatályba lépéshez jelentkezzen ki, majd be):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Linuxon nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat a venv létrehozásához.
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
    Windowson nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat a venv létrehozásához.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: Előfordulhat, hogy a Windows-felhasználóknak módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
    > RemoteSigned vagy Unrestricted értékre kell állítani) egyes PowerShell-parancsok futtatása előtt.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windowson nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat a venv létrehozásához.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: Előfordulhat, hogy a Windows-felhasználóknak módosítaniuk kell a PowerShell végrehajtási házirendjét (pl.
    > RemoteSigned vagy Unrestricted értékre kell állítani) egyes PowerShell-parancsok futtatása előtt.

<!-- @device:end -->
<!-- @os:end -->

2. Telepítse az OpenAI csomagot
    ```bash
    pip install openai
    ```

3. Futtassa az alábbi szkriptet az imént létrehozott végpont pingeléséhez.
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

#### (Opcionális): Váltás a futtatókörnyezetek között

1. Nyomja meg a `Ctrl + Shift + R` billentyűkombinációt a billentyűzeten. Alternatívaként kattintson a `Discover` fülre (Nagyító ikon) a bal oldalon, majd kattintson a `Runtime` elemre a felugró ablakban.
2. Ekkor megjelenik a `Runtime Selections` panel, ahol a legördülő menü segítségével módosítható a futtatókörnyezet.


## Következő lépések

- **Egyéni alkalmazásintegráció**: Integrálja saját Python-szkriptjeit vagy alkalmazásait a helyi OpenAI-kompatibilis API segítségével.
- **Fejlett felületek**: Csatlakoztasson hatékony felületeket, például az Open WebUI-t a szerveréhez a csevegési előzmények és személyiségkezelés érdekében.

További dokumentációért látogasson el ide: https://lmstudio.ai/docs/developer