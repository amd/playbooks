<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

LM Studio to zaawansowana aplikacja z interfejsem graficznym stanowiąca nakładkę na [llama.cpp](https://github.com/ggml-org/llama.cpp), zapewniająca również [zgodny z OpenAI punkt końcowy](https://lmstudio.ai/docs/developer/openai-compat) do lokalnego serwowania modeli. LM Studio oferuje prosty, ale zaawansowany interfejs umożliwiający łatwe pobieranie i wdrażanie modeli. LM Studio udostępnia dla użytkowników AMD zarówno backendy Vulkan, jak i AMD ROCm™ (nazywane runtime'ami).


## Czego się nauczysz
- Jak skonfigurować i używać LM Studio, aby wykorzystać lokalny sprzęt
- Testowania i zarządzania modelami LLM w całkowicie offline'owym środowisku
- Serwowania modeli za pośrednictwem interfejsu API zgodnego z OpenAI, aby zasilać niestandardowe przepływy pracy i aplikacje


<!-- @device:halo_box,halo,stx,krk -->
## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @os:linux -->
> **Uwaga**: VS Code można zainstalować za pośrednictwem AMD Ryzen™ AI Developer Center. W przypadku LM Studio postępuj zgodnie z poniższymi instrukcjami instalacji.
<!-- @os:end -->

<!-- @os:windows -->
> **Uwaga**: Jeśli VS Code lub LM Studio nie są zainstalowane, można je zainstalować z poziomu AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Pobieranie modeli

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

## Rozmowa z LLM
Dowiedz się, jak rozpocząć rozmowę z modelem LLM na poziomie ChatGPT całkowicie lokalnie.  

1. Otwórz LMStudio. 
2. Naciśnij `Ctrl + L`, aby otworzyć narzędzie do wczytywania modeli, wybierz `Manually choose model load parameters`, a następnie kliknij `${model_name}`
3. Upewnij się, że opcja „show advanced settings” jest zaznaczona.  
4. Zmień `Context Length` według potrzeb. Wyższa długość kontekstu oznacza większe zużycie pamięci modelu, ale też więcej zużytej pamięci systemowej. Zalecana wartość w tym poradniku to 4096.
5. Upewnij się, że `GPU Offload` jest ustawione na maksimum, a `Flash Attention` jest włączone (Cache Quantizations mogą pozostać wyłączone)
6. Zaznacz `Remember settings` i kliknij `Load Model`.
7. Jeśli nie znajdujesz się w oknie czatu, naciśnij `Ctrl + 1` lub kliknij przycisk 👾 w lewym górnym rogu ekranu.
8. Wyślij wiadomość i zacznij interakcję z modelem!

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

> **Wskazówka**: Długość kontekstu odnosi się do pamięci modelu. Flash attention przyspiesza przetwarzanie, jednocześnie zmniejszając zużycie pamięci. GPU Offload przenosi obliczenia na kartę graficzną, co przyspiesza odpowiedzi.

## Serwowanie modeli LLM za pośrednictwem punktu końcowego zgodnego z OpenAI

LM Studio oferuje również zgodny z OpenAI punkt końcowy w postaci LM Studio Server. Zostało to już zaprezentowane w agentowym przepływie pracy związanym z kodowaniem przy użyciu Cline [tutaj](../playbooks/vscode-qwen3-coder). Innym popularnym zastosowaniem jest połączenie LM Studio Server z dowolną aplikacją webową (React, Node.js, Python) poprzez wysyłanie standardowych żądań HTTP do punktu końcowego wnioskowania.

Aby skonfigurować LM Studio Server, postępuj zgodnie z poniższymi instrukcjami:

1. Po lewej stronie kliknij zakładkę `Developer` (ikona wiersza poleceń) lub naciśnij `Ctrl + 2`, a następnie kliknij `Server Settings`.  
2. (Opcjonalnie): Jeśli chcesz udostępniać model w sieci LAN, zaznacz `Serve on Local Network`. Jeśli chcesz korzystać z niego na stronie internetowej lub przy rozbudowanym wywoływaniu w VS Code, zaznacz `Enable CORS`. 
3. W lewym górnym rogu upewnij się, że serwer działa, klikając przełącznik obok `Status`.
4. Punkt końcowy zgodny z OpenAI będzie teraz aktywny. Adres to zazwyczaj http://127.0.0.1:1234  
5. Jeśli model nie jest jeszcze wczytany, możesz go wczytać, klikając `Load Model` i postępując zgodnie z wcześniej opisanymi krokami. 

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


Ten model będzie teraz dostępny za pośrednictwem punktu końcowego LM Studio Server i będzie obsługiwał punkty końcowe zgodne z OpenAI, w tym:

| Punkt końcowy | Metoda | Dokumentacja |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Przykład: Testowanie punktu końcowego

Po utworzeniu punktu końcowego zgodnego z OpenAI, przyjrzyjmy się, jak zintegrować go ze środowiskiem programistycznym Python (takim jak VSCode) i wykorzystać swój system jako lokalnego dostawcę API.

1. Utwórz środowisko wirtualne Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (aby zmiana zaczęła obowiązywać, wyloguj się i zaloguj ponownie):

```bash
sudo usermod -aG render,video $LOGNAME
```

    W systemie Linux otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
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
    W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania programu PowerShell (Execution Policy) (np.
    > ustawiając ją na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    W systemie Windows otwórz terminal w wybranym katalogu i wykonaj poniższe polecenia, aby utworzyć środowisko venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Wskazówka**: Użytkownicy systemu Windows mogą potrzebować zmodyfikować zasady wykonywania programu PowerShell (Execution Policy) (np.
    > ustawiając ją na RemoteSigned lub Unrestricted) przed uruchomieniem niektórych poleceń PowerShell.

<!-- @device:end -->
<!-- @os:end -->

2. Zainstaluj pakiet OpenAI
    ```bash
    pip install openai
    ```

3. Uruchom poniższy skrypt, aby przetestować utworzony wcześniej punkt końcowy.
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

#### (Opcjonalnie): Przełączanie się między środowiskami uruchomieniowymi

1. Naciśnij `Ctrl + Shift + R` na klawiaturze. Alternatywnie kliknij zakładkę `Discover` (ikona lupy) po lewej stronie, a następnie kliknij `Runtime` w wyskakującym okienku.
2. Powinieneś wtedy zobaczyć `Runtime Selections`, gdzie za pomocą menu rozwijanego można zmienić środowisko uruchomieniowe.


## Kolejne kroki

- **Integracja własnych aplikacji**: Zintegruj własne skrypty lub aplikacje Python, korzystając z lokalnego API zgodnego z OpenAI.
- **Zaawansowane interfejsy**: Połącz zaawansowane interfejsy, takie jak Open WebUI, ze swoim serwerem, aby zarządzać historią czatu i profilami.

Więcej dokumentacji znajdziesz na stronie: https://lmstudio.ai/docs/developer