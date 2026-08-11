<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Az LM Studio egy erőteljes, GUI-alapú wrapper a [llama.cpp](https://github.com/ggml-org/llama.cpp) számára, és emellett [OpenAI-kompatibilis végpontot](https://lmstudio.ai/docs/developer/openai-compat) is biztosít a helyi modellkiszolgáláshoz. Az LM Studio egyszerű, mégis nagy teljesítményű felületet nyújt a modellek egyszerű letöltéséhez és üzembe helyezéséhez. Az LM Studio mind Vulkan, mind AMD ROCm™ szoftveres backendet (úgynevezett runtime-ot) kínál AMD felhasználók számára.


## Amit tanulni fog
- Hogyan konfigurálja és használja az LM Studiót a helyi hardver kihasználásához
- LLM-ek tesztelése és kezelése teljesen offline környezetben
- Modellek kiszolgálása OpenAI-kompatibilis API-n keresztül egyedi munkafolyamatok és alkalmazások meghajtásához


## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @os:linux -->
> **Megjegyzés**: A VS Code-ot telepítheti az AMD Ryzen™ AI Developer Centeren keresztül. Az LM Studio esetében kövesse az alábbi telepítési utasításokat.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés**: Ha a VS Code vagy az LM Studio nincs telepítve, telepítheti azokat az AMD Ryzen™ AI Developer Centerről. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftverelőfeltételek telepítése

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
Ismerje meg, hogyan kezdhet el csevegni egy ChatGPT-szintű LLM-mel teljesen helyi módon.  

1. Nyissa meg az LMStudio-t. 
2. Nyomja meg a `Ctrl + L` billentyűkombinációt a Model Loader megnyitásához, válassza a `Manually choose model load parameters` opciót, majd kattintson a(z) `${model_name}` elemre
3. Győződjön meg róla, hogy a „show advanced settings” be van jelölve.  
4. Módosítsa a `Context Length` értékét igény szerint. A nagyobb kontextushossz több modellmemóriát jelent, de több rendszermemóriát is felhasznál. Ehhez a playbookhoz a 4096 érték ajánlott.
5. Győződjön meg róla, hogy a `GPU Offload` a maximumra van állítva, és a `Flash Attention` be van kapcsolva (a Cache Quantizations maradhat kikapcsolva)
6. Jelölje be a `Remember settings` opciót, majd kattintson a `Load Model` gombra.
7. Ha nem a csevegőablakban van, nyomja meg a `Ctrl + 1` billentyűkombinációt, vagy kattintson a 👾 gombra a képernyő bal felső sarkában.
8. Küldjön egy üzenetet, és kezdjen el interakcióba lépni a modellel!

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

> **Tipp**: A kontextushossz a modell memóriájára utal. A flash attention javítja a feldolgozási sebességet, miközben csökkenti a memóriahasználatot. A GPU Offload a számítást a videokártyára helyezi át a gyorsabb válaszok érdekében.

## LLM-ek kiszolgálása OpenAI-kompatibilis végponton keresztül

Az LM Studio emellett OpenAI-kompatibilis végpontot is kínál az LM Studio Server formájában. Ezt már bemutattuk egy ügynökalapú kódolási munkafolyamatban a Cline-nal [itt](../playbooks/vscode-qwen3-coder). Egy másik gyakori felhasználási eset az LM Studio Server csatlakoztatása bármely webalkalmazáshoz (React, Node.js, Python) szabványos HTTP-kérések küldésével a következtetési végpontra.

Az LM Studio Server beállításához kövesse az alábbi utasításokat:

1. A bal oldalon kattintson a `Developer` fülre (parancssor ikon) vagy nyomja meg a `Ctrl + 2` billentyűkombinációt, majd kattintson a `Server Settings` elemre.  
2. (Opcionális): Ha a modellt a LAN hálózaton keresztül szeretné kiszolgálni, jelölje be a `Serve on Local Network` opciót. Ha egy weboldallal vagy kiterjedt hívásokkal szeretné használni a VS Code-on belül, jelölje be az `Enable CORS` opciót. 
3. A bal felső sarokban győződjön meg róla, hogy a szerver fut, a `Status` előtti kapcsológombra kattintva.
4. Ezzel egy OpenAI-kompatibilis végpont fog futni. A cím jellemzően a http://127.0.0.1:1234 címen érhető el  
5. Ha még nincs betöltve modell, betöltheti a `Load Model` gombra kattintva, és a korábban ismertetett lépéseket követve. 

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


Ez a modell mostantól elérhető lesz az LM Studio Server végponton keresztül, és támogatni fogja az OpenAI végpontokat, beleértve az alábbiakat:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Példa: Az Endpoint pingelése
Miután létrehoztuk az OpenAI-kompatibilis végpontot, nézzük meg, hogyan integrálhatjuk ezt egy Python fejlesztői környezetbe (mint például a VSCode), és hogyan használhatjuk a rendszerünket helyi API-szolgáltatóként.

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
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (a változtatás érvénybe lépéséhez jelentkezzen ki, majd vissza):

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
    Windows rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat a venv létrehozásához.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: A Windows-felhasználóknak esetleg módosítaniuk kell a PowerShell végrehajtási szabályzatát (Execution Policy) (pl.
    > RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell-parancs futtatása előtt.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windows rendszeren nyisson meg egy terminált a kívánt könyvtárban, és kövesse az alábbi parancsokat a venv létrehozásához.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tipp**: A Windows-felhasználóknak esetleg módosítaniuk kell a PowerShell végrehajtási szabályzatát (Execution Policy) (pl.
    > RemoteSigned vagy Unrestricted értékre állítva) néhány PowerShell-parancs futtatása előtt.

<!-- @device:end -->
<!-- @os:end -->

2. Telepítse az OpenAI csomagot
    ```bash
    pip install openai
    ```

3. Futtassa a következő szkriptet az imént létrehozott végpont pingeléséhez.
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

#### (Opcionális): Váltás a futtatókörnyezetek (Runtimes) között

1. Nyomja meg a `Ctrl + Shift + R` billentyűkombinációt a billentyűzeten. Alternatív megoldásként kattintson a bal oldalon található `Discover` (Felfedezés) fülre (nagyítóüveg ikon), majd a felugró ablakban kattintson a `Runtime` opcióra.
2. Ezután meg kell jelennie a `Runtime Selections` (Futtatókörnyezet-választás) résznek, ahol a legördülő menü segítségével módosíthatja a futtatókörnyezetet.


## Következő lépések

- **Egyéni alkalmazásintegráció**: Integrálja saját Python szkriptjeit vagy alkalmazásait a helyi, OpenAI-kompatibilis API használatával.
- **Fejlett felhasználói felületek**: Csatlakoztasson erőteljes felületeket, mint például az Open WebUI-t, a szerveréhez a csevegési előzmények és a persona-kezelés érdekében.

További dokumentációért látogasson el ide: https://lmstudio.ai/docs/developer