<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Genel Bakış

LM Studio, [llama.cpp](https://github.com/ggml-org/llama.cpp) için güçlü, GUI tabanlı bir sarmalayıcıdır ve ayrıca yerel model sunumu için [OpenAI uyumlu bir uç nokta](https://lmstudio.ai/docs/developer/openai-compat) sağlar. LM Studio, modelleri kolayca indirmek ve dağıtmak için basit ama güçlü bir arayüz sunar. LM Studio, AMD kullanıcıları için hem Vulkan hem de AMD ROCm™ yazılım arka uçlarını (runtime olarak adlandırılır) sunar.


## Neler Öğreneceksiniz
- LM Studio'yu yerel donanımınızdan yararlanacak şekilde nasıl yapılandıracağınızı ve kullanacağınızı
- LLM'leri tamamen çevrimdışı bir ortamda nasıl test edip yöneteceğinizi
- Özel iş akışlarını ve uygulamaları desteklemek için modelleri OpenAI Uyumlu API üzerinden nasıl sunacağınızı


## Bellek Yapılandırmasını Ayarlama

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Yazılım Güncellemelerini Kontrol Etme

<!-- @os:linux -->
> **Not**: VS Code'u AMD Ryzen™ AI Developer Center üzerinden yükleyebilirsiniz. LM Studio için aşağıdaki yükleme talimatlarını izleyin.
<!-- @os:end -->

<!-- @os:windows -->
> **Not**: VS Code veya LM Studio yüklü değilse, bunları AMD Ryzen™ AI Developer Center üzerinden yükleyebilirsiniz. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Yazılım Ön Koşullarının Yüklenmesi

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Modellerin İndirilmesi

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

## LLM ile Sohbet Etme
Tamamen yerel olarak ChatGPT düzeyinde bir LLM ile sohbet etmeye nasıl başlayacağınızı öğrenin.  

1. LMStudio'yu açın. 
2. Model Yükleyiciyi açmak için `Ctrl + L` tuşlarına basın, `Manually choose model load parameters` seçeneğini seçin ve `${model_name}` üzerine tıklayın
3. "show advanced settings" seçeneğinin işaretli olduğundan emin olun.  
4. `Context Length` değerini istediğiniz gibi değiştirin. Daha yüksek bağlam uzunluğu, daha fazla model belleği anlamına gelir, ancak daha fazla sistem belleği kullanılır. Bu kılavuz için önerilen değer 4096'dır.
5. `GPU Offload` değerinin maksimum olarak ayarlandığından ve `Flash Attention` seçeneğinin açık olduğundan emin olun (Cache Quantizations kapalı kalabilir)
6. `Remember settings` seçeneğini işaretleyin ve `Load Model` üzerine tıklayın.
7. Sohbet penceresinde değilseniz, `Ctrl + 1` tuşlarına basın veya ekranın sol üst köşesindeki 👾 düğmesine tıklayın.
8. Bir mesaj gönderin ve modelle etkileşime başlayın!

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

> **İpucu**: Bağlam uzunluğu, modelin belleğini ifade eder. Flash attention, bellek kullanımını azaltırken işlem hızını artırır. GPU Offload, daha hızlı yanıtlar için işlemi grafik kartına aktarır.

## LLM'leri OpenAI Uyumlu Bir Uç Nokta Üzerinden Sunma

LM Studio ayrıca LM Studio Server şeklinde OpenAI uyumlu bir uç nokta sunar. Bu, Cline ile birlikte bir ajan tabanlı kodlama iş akışında [burada](../playbooks/vscode-qwen3-coder) zaten gösterilmiştir. Bir başka yaygın kullanım örneği, çıkarım uç noktasına standart HTTP istekleri göndererek LM Studio Server'ı herhangi bir web uygulamasına (React, Node.js, Python) bağlamaktır.

LM Studio Server'ı ayarlamak için aşağıdaki talimatları kullanın:

1. Sol tarafta, `Developer` sekmesine (komut satırı simgesi) tıklayın veya `Ctrl + 2` tuşlarına basın, ardından `Server Settings` üzerine tıklayın.  
2. (İsteğe bağlı): Modeli LAN'ınız üzerinden sunmak istiyorsanız, `Serve on Local Network` seçeneğini işaretleyin. Bir web sitesiyle veya VS Code içinde kapsamlı çağrılarla kullanmak istiyorsanız, `Enable CORS` seçeneğini işaretleyin. 
3. Sol üst köşede, `Status` önündeki geçiş düğmesine tıklayarak sunucunun çalıştığından emin olun.
4. Artık OpenAI uyumlu bir uç nokta çalışıyor olacak. Adres genellikle http://127.0.0.1:1234 şeklindedir  
5. Bir model zaten yüklenmemişse, `Load Model` üzerine tıklayıp daha önce bahsedilen adımları izleyerek yükleyebilirsiniz. 

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


Bu model artık LM Studio Server uç noktası üzerinden erişilebilir olacak ve aşağıdakiler dahil OpenAI uç noktalarını destekleyecektir:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Örnek: Uç Noktanızı Ping Etme
OpenAI Uyumlu uç noktayı oluşturduktan sonra, bunu bir Python geliştirici ortamına (VSCode gibi) nasıl entegre edeceğinizi ve sisteminizi yerel bir API Sağlayıcı olarak nasıl kullanacağınızı inceleyelim.

1. Bir Python sanal ortamı oluşturun:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Linux'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutları izleyin.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Kullanıcınıza GPU cihazlarına erişim izni verin** (bunun etkili olması için oturumu kapatıp tekrar açın):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Linux'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutları izleyin.
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
    Windows'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutları izleyin.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **İpucu**: Windows kullanıcılarının, bazı Powershell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini değiştirmesi gerekebilir (örneğin,
    > RemoteSigned veya Unrestricted olarak ayarlamak gibi).

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windows'ta, seçtiğiniz dizinde bir terminal açın ve bir venv oluşturmak için aşağıdaki komutları izleyin.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **İpucu**: Windows kullanıcılarının, bazı Powershell komutlarını çalıştırmadan önce PowerShell Yürütme İlkesini değiştirmesi gerekebilir (örneğin,
    > RemoteSigned veya Unrestricted olarak ayarlamak gibi).

<!-- @device:end -->
<!-- @os:end -->

2. OpenAI paketini kurun
    ```bash
    pip install openai
    ```

3. Az önce oluşturduğumuz uç noktayı ping etmek için aşağıdaki betiği çalıştırın.
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

#### (İsteğe Bağlı): Çalışma Zamanları Arasında Geçiş Yapma

1. Klavyenizde `Ctrl + Shift + R` tuşlarına basın. Alternatif olarak sol taraftaki `Discover` sekmesine (Büyüteç) tıklayın ve ardından açılan pencerede `Runtime` seçeneğine tıklayın.
2. Ardından, açılır menü kullanılarak çalışma zamanının değiştirilebileceği `Runtime Selections` bölümünü görmelisiniz.


## Sonraki Adımlar

- **Özel Uygulama Entegrasyonu**: Yerel OpenAI uyumlu API'yi kullanarak kendi Python betiklerinizi veya uygulamalarınızı entegre edin.
- **Gelişmiş Ön Yüzler**: Sohbet geçmişi ve persona yönetimi için sunucunuza Open WebUI gibi güçlü arayüzler bağlayın.

Daha fazla belge için lütfen şu adresi ziyaret edin: https://lmstudio.ai/docs/developer