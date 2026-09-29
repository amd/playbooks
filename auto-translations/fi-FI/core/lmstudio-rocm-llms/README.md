<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

LM Studio on tehokas graafiseen käyttöliittymään perustuva kääre [llama.cpp](https://github.com/ggml-org/llama.cpp) -kirjastolle, ja se tarjoaa myös [OpenAI-yhteensopivan päätepisteen](https://lmstudio.ai/docs/developer/openai-compat) mallien paikalliseen palvelemiseen. LM Studio tarjoaa yksinkertaisen mutta tehokkaan käyttöliittymän mallien lataamiseen ja käyttöönottoon. LM Studio tarjoaa AMD-käyttäjille sekä Vulkan- että AMD ROCm™ -ohjelmistotaustaosia (kutsutaan ajoympäristöiksi, engl. runtimes).


## Mitä opit
- Kuinka LM Studio konfiguroidaan ja miten sitä käytetään paikallisen laitteistosi hyödyntämiseen
- LLM-mallien testaaminen ja hallinta täysin offline-ympäristössä
- Mallien tarjoaminen OpenAI-yhteensopivan API:n kautta räätälöityjen työnkulkujen ja sovellusten tehostamiseksi


<!-- @device:halo_box,halo,stx,krk -->
## Muistin konfigurointi

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @os:linux -->
> **Huomautus**: Voit asentaa VS Coden AMD Ryzen™ AI Developer Centerin kautta. Asenna LM Studio noudattamalla alla olevia asennusohjeita.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus**: Jos VS Code tai LM Studio ei ole asennettuna, voit asentaa ne AMD Ryzen™ AI Developer Centeristä. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Mallien lataaminen

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

## Keskusteleminen LLM:n kanssa
Opi aloittamaan keskustelu ChatGPT-tasoisen LLM:n kanssa täysin paikallisesti.  

1. Avaa LMStudio. 
2. Paina `Ctrl + L` avataksesi mallinlataajan, valitse `Manually choose model load parameters` ja napsauta kohtaa `${model_name}`
3. Varmista, että "show advanced settings" on valittuna.  
4. Muuta `Context Length` -arvoa haluamallasi tavalla. Suurempi kontekstipituus tarkoittaa enemmän mallin muistin käyttöä, mutta myös enemmän järjestelmämuistin käyttöä. Tähän ohjeeseen suositellaan arvoa 4096.
5. Varmista, että `GPU Offload` on asetettu maksimiin ja `Flash Attention` on päällä (Cache Quantizations -asetukset voivat pysyä pois päältä)
6. Rastita `Remember settings` ja napsauta `Load Model`.
7. Jos et ole keskusteluikkunassa, paina `Ctrl + 1` tai napsauta 👾-painiketta näytön vasemmassa yläkulmassa.
8. Lähetä viesti ja aloita vuorovaikutus mallin kanssa!

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

> **Vinkki**: Kontekstipituus viittaa mallin muistiin. Flash attention parantaa käsittelynopeutta ja vähentää samalla muistinkäyttöä. GPU Offload siirtää laskennan näytönohjaimelle nopeampien vastausten saamiseksi.

## LLM-mallien tarjoaminen OpenAI-yhteensopivan päätepisteen kautta

LM Studio tarjoaa myös OpenAI-yhteensopivan päätepisteen LM Studio Serverin muodossa. Tätä on jo esitelty agenttipohjaisessa koodaustyönkulussa Clinen kanssa [täällä](../playbooks/vscode-qwen3-coder). Toinen yleinen käyttötapaus on LM Studio Serverin yhdistäminen mihin tahansa verkkosovellukseen (React, Node.js, Python) lähettämällä tavallisia HTTP-pyyntöjä päättelypäätepisteeseen.

Ota LM Studio Server käyttöön seuraavien ohjeiden mukaisesti:

1. Napsauta vasemmalla puolella olevaa `Developer`-välilehteä (komentorivikuvake) tai paina `Ctrl + 2` ja napsauta sitten `Server Settings`.  
2. (Valinnainen): Jos haluat tarjota mallia lähiverkon (LAN) kautta, valitse `Serve on Local Network`. Jos haluat käyttää sitä verkkosivuston kanssa tai laajaa kutsumista VS Codesta, valitse `Enable CORS`. 
3. Varmista vasemmasta yläkulmasta, että palvelin on käynnissä napsauttamalla `Status`-kohdan edessä olevaa vaihtopainiketta.
4. OpenAI-yhteensopiva päätepiste on nyt käynnissä. Osoite on tyypillisesti http://127.0.0.1:1234  
5. Jos malli ei ole vielä ladattuna, voit ladata sen napsauttamalla `Load Model` ja seuraamalla aiemmin mainittuja vaiheita. 

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


Tämä malli on nyt käytettävissä LM Studio Serverin päätepisteen kautta ja tukee OpenAI-päätepisteitä, mukaan lukien:

| Päätepiste | Menetelmä | Dokumentaatio |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Esimerkki: Pingaa päätepistettäsi
Nyt kun olemme juuri luoneet OpenAI-yhteensopivan päätepisteen, katsotaan, miten tämä integroidaan Python-kehitysympäristöön (kuten VSCode) ja käytetään järjestelmääsi paikallisena API-tarjoajana.

1. Luo Python-virtuaaliympäristö:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Avaa Linuxissa pääte haluamaasi hakemistoon ja luo venv seuraavilla komennoilla.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Avaa Linuxissa pääte haluamaasi hakemistoon ja luo venv seuraavilla komennoilla.
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
    Avaa Windowsissa pääte haluamaasi hakemistoon ja luo venv seuraavilla komennoilla.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Vinkki**: Windows-käyttäjien tulee ehkä muokata PowerShellin suorituskäytäntöä (esim.
    > asettaa se arvoon RemoteSigned tai Unrestricted) ennen kuin he voivat suorittaa joitakin PowerShell-komentoja.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Avaa Windowsissa pääte haluamaasi hakemistoon ja luo venv seuraavilla komennoilla.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Vinkki**: Windows-käyttäjien tulee ehkä muokata PowerShellin suorituskäytäntöä (esim.
    > asettaa se arvoon RemoteSigned tai Unrestricted) ennen kuin he voivat suorittaa joitakin PowerShell-komentoja.

<!-- @device:end -->
<!-- @os:end -->

2. Asenna OpenAI-paketti
    ```bash
    pip install openai
    ```

3. Suorita seuraava skripti pingataksesi juuri luomaamme päätepistettä.
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

#### (Valinnainen): Ajoympäristöjen vaihtaminen

1. Paina näppäimistöltä `Ctrl + Shift + R`. Vaihtoehtoisesti napsauta `Discover`-välilehteä (suurennuslasi) vasemmalla puolella ja napsauta sitten ponnahdusikkunassa `Runtime`.
2. Näet tämän jälkeen kohdan `Runtime Selections`, jossa avattavaa valikkoa voi käyttää ajoympäristön vaihtamiseen.


## Seuraavat vaiheet

- **Mukautettu sovellusintegraatio**: Integroi omat Python-skriptisi tai sovelluksesi käyttäen paikallista OpenAI-yhteensopivaa API:a.
- **Kehittyneet käyttöliittymät**: Yhdistä tehokkaita käyttöliittymiä, kuten Open WebUI, palvelimeesi keskusteluhistorian ja persoonien hallintaa varten.

Lisää dokumentaatiota löydät osoitteesta: https://lmstudio.ai/docs/developer