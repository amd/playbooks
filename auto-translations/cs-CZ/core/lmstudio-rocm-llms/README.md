<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

LM Studio je výkonný grafický wrapper pro [llama.cpp](https://github.com/ggml-org/llama.cpp) a také poskytuje [endpoint kompatibilní s OpenAI](https://lmstudio.ai/docs/developer/openai-compat) pro lokální obsluhu modelů. LM Studio nabízí jednoduché, ale výkonné rozhraní pro snadné stahování a nasazování modelů. LM Studio nabízí uživatelům AMD backendy (nazývané runtime) Vulkan i AMD ROCm™.


## Co se naučíte
- Jak nakonfigurovat a používat LM Studio k využití místního hardwaru
- Testovat a spravovat LLM v zcela offline prostředí
- Obsluhovat modely prostřednictvím API kompatibilního s OpenAI pro vlastní pracovní postupy a aplikace


## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @os:linux -->
> **Poznámka**: VS Code můžete nainstalovat prostřednictvím AMD Ryzen™ AI Developer Center. Pro LM Studio postupujte podle níže uvedených pokynů k instalaci.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka**: Pokud VS Code nebo LM Studio není nainstalováno, můžete je nainstalovat z AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Stahování modelů

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

## Chatování s LLM
Naučte se, jak začít chatovat s LLM na úrovni ChatGPT zcela lokálně.

1. Otevřete LMStudio.
2. Stiskněte `Ctrl + L` pro otevření Model Loaderu, vyberte `Manually choose model load parameters` a klikněte na `${model_name}`
3. Ujistěte se, že je zaškrtnuto „show advanced settings".
4. Změňte `Context Length` podle potřeby. Větší délka kontextu znamená více paměti modelu, ale větší využití systémové paměti. Pro tento playbook je doporučena hodnota 4096.
5. Ujistěte se, že `GPU Offload` je nastaven na maximum a `Flash Attention` je zapnuto (Cache Quantizations může zůstat vypnuto).
6. Zaškrtněte `Remember settings` a klikněte na `Load Model`.
7. Pokud nejste v okně chatu, stiskněte `Ctrl + 1` nebo klikněte na tlačítko 👾 v levém horním rohu obrazovky.
8. Odešlete zprávu a začněte interagovat s modelem!

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

> **Tip**: Délka kontextu označuje paměť modelu. Flash attention zlepšuje rychlost zpracování při snížení využití paměti. GPU Offload přesouvá výpočty na grafickou kartu pro rychlejší odezvy.

## Obsluha LLM prostřednictvím endpointu kompatibilního s OpenAI

LM Studio také nabízí endpoint kompatibilní s OpenAI v podobě LM Studio Server. To již bylo demonstrováno v agentním pracovním postupu kódování s Cline [zde](../playbooks/vscode-qwen3-coder). Dalším běžným případem použití je připojení LM Studio Server k libovolné webové aplikaci (React, Node.js, Python) odesíláním standardních HTTP požadavků na inference endpoint.

Pro nastavení LM Studio Server postupujte podle následujících pokynů:

1. Na levé straně klikněte na záložku `Developer` (ikona příkazového řádku) nebo `Ctrl + 2` a poté klikněte na `Server Settings`.
2. (Volitelné): Pokud chcete model obsluhovat přes vaši LAN, zaškrtněte `Serve on Local Network`. Pokud chcete používat s webovou stránkou nebo rozsáhlým voláním v rámci VS Code, zaškrtněte `Enable CORS`.
3. V levém horním rohu se ujistěte, že server běží, kliknutím na přepínací tlačítko před `Status`.
4. Endpoint kompatibilní s OpenAI nyní bude spuštěn. Adresa je obvykle http://127.0.0.1:1234
5. Pokud model ještě není načten, můžete ho načíst kliknutím na `Load Model` a postupováním podle dříve zmíněných kroků.

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


Tento model bude nyní přístupný prostřednictvím endpointu LM Studio Server a bude podporovat endpointy OpenAI včetně:

| Endpoint | Metoda | Dokumentace |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Příklad: Ping vašeho endpointu
Po vytvoření endpointu kompatibilního s OpenAI se podívejme, jak ho integrovat do vývojového prostředí Python (například VSCode) a použít váš systém jako lokálního poskytovatele API.

1. Vytvořte virtuální prostředí Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udělte svému uživateli přístup k GPU zařízením** (pro aktivaci se odhlaste a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
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
    Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Uživatelé Windows možná budou muset upravit zásady spouštění PowerShellu (např.
    > nastavit je na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Tip**: Uživatelé Windows možná budou muset upravit zásady spouštění PowerShellu (např.
    > nastavit je na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.

<!-- @device:end -->
<!-- @os:end -->

2. Nainstalujte balíček OpenAI
    ```bash
    pip install openai
    ```

3. Spusťte následující skript pro ping endpointu, který jsme právě vytvořili.
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

#### (Volitelné): Přepínání mezi runtime prostředími

1. Stiskněte `Ctrl + Shift + R` na klávesnici. Případně klikněte na záložku `Discover` (lupa) na levé straně a poté klikněte na `Runtime` ve vyskakovacím okně.
2. Měli byste pak vidět `Runtime Selections`, kde lze pomocí rozbalovací nabídky změnit runtime.


## Další kroky

- **Integrace vlastní aplikace**: Integrujte vlastní Python skripty nebo aplikace pomocí lokálního API kompatibilního s OpenAI.
- **Pokročilá rozhraní**: Připojte výkonná rozhraní jako Open WebUI k vašemu serveru pro správu historie chatu a person.

Další dokumentaci naleznete na: https://lmstudio.ai/docs/developer