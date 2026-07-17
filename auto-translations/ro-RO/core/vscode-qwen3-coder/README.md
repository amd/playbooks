<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Acest ghid folosește etichete speciale pe care GitHub nu le poate reda. Vă rugăm să vizitați [amd.com/playbooks](https://amd.com/playbooks) pentru a previzualiza corect acest conținut.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Acest ghid necesită minimum **32 GB** de memorie de sistem.
<!-- @device:end -->

## Prezentare generală

Agenții de codare sunt instrumente puternice care îi ajută pe dezvoltatori prin colaborarea cu agenți AI susținuți de Modele de Limbaj de Mari Dimensiuni (LLM-uri). Aceștia pot fi integrați în mediul de dezvoltare, cum ar fi terminalul sau VS Code, permițând o integrare perfectă în fluxul de lucru al unui dezvoltator.

Acest tutorial demonstrează cum să utilizați Cline, VS Code și LM Studio pentru a rula un agent de codare în întregime pe mașina locală.

## Ce veți învăța

* Cum să rulați VS Code cu agentul de codare Cline pentru a sprijini sarcinile de inginerie software.
* Cum să configurați Cline pentru a comunica cu LM Studio în vederea inferenței locale a agenților de codare.
* Cum să utilizați agenți de codare locali pentru a rezolva sarcini reale de inginerie software.

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificarea actualizărilor de software
> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor software preliminare

<!-- @require:lmstudio,vscode -->

## Lansarea și configurarea LM Studio

Vom folosi LM Studio pentru a servi LLM-ul care alimentează agentul de codare.

- În bara de căutare, căutați `LM Studio` și lansați aplicația. Veți fi întâmpinat de următoarea pagină.

![Ecranul inițial LM Studio](assets/initial-lm-studio.png)

În continuare, trebuie să încărcăm LLM-ul pe sistem. Vom folosi modelul `Qwen3-Coder-30B-A3B` cu o lungime mare a contextului. (Utilizați fila Model pentru a-l instala dacă nu ați făcut-o deja).
- Faceți clic pe bara de căutare din partea de sus a ferestrei LM Studio sau apăsați `CTRL+L`. Faceți clic pe comutatorul `Manually choose model load parameters` și apoi faceți clic pe modelul Qwen3-Coder-30B-A3B.
- Schimbați lungimea contextului de la `4096` la `32768` și asigurați-vă că `GPU Offload` este la maxim. Apoi, faceți clic pe `Load Model`.

![Selectarea modelului](assets/model-list-zoomed.png)

Folosim o lungime mare a contextului pentru ca agentul să poată procesa baze de cod extinse și să rețină modificările efectuate.

![Configurarea modelului](assets/selecting-model-zoomed.png)

În continuare, trebuie să activăm serverul LM Studio.
- Faceți clic pe fila Developer sau apăsați `CTRL+2` în LM Studio, în panoul din stânga.
- Verificați comutatorul de stare și asigurați-vă că este setat pe `Running`.

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

![Starea serverului](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Lansarea și configurarea VS Code

Vom instala extensia Cline în VS Code și o vom conecta la serverul LM Studio pe care tocmai l-am creat.
- În bara de căutare, căutați `VS Code` și lansați aplicația.
- Faceți clic pe pictograma `Extensions` din coloana din stânga a VS Code și căutați `Cline`. Apoi, faceți clic pe butonul `Install`.

![Instalarea extensiei Cline](assets/installing-cline-vscode-extension.png)

- O pictogramă Cline ar trebui să fie prezentă în stânga. Faceți clic pe aceasta pentru a deschide Cline. Va apărea o fereastră care întreabă `How will you use Cline?` Deoarece vom folosi un LLM local rulat prin LM Studio, selectați `Bring my own API Key` și apăsați `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Crearea contului](assets/cline-how-will-you-use-cline-zoomed.png)

În continuare, trebuie să configurăm Cline pentru a comunica cu serverul LM Studio pe care l-am configurat.
- Setați furnizorul API la `LM Studio` și modelul la `Qwen3-Coder-30B-A3B-GGUF`.

>**Sfat**: Este posibil ca modele mai noi să fie disponibile. Luați în considerare descărcarea și trecerea la modele Qwen3.6 dacă doriți.


![Configurarea modelului](assets/cline-model-configuration-zoomed.png)

## Crearea primului proiect

Să folosim agentul local pentru a crea un site web! Deschideți VSCode într-un director la alegere, unde Cline va crea fișierele.
- Pentru a face acest lucru, mergeți la `File -> Open Folder` în partea stângă sus a VS Code și alegeți un folder, cum ar fi `Documents`.

![Folder gol în VS Code](assets/open-cline-test.png)

Acum suntem pregătiți să trimitem un prompt agentului de codare local.
- Faceți clic pe extensia Cline din coloana din stânga și introduceți un prompt pentru a porni agentul. Ca exemplu, să folosim următorul prompt:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Agentul va începe apoi să creeze fișiere conform promptului. Ca utilizator, puteți urmări generarea codului în VS Code, așa cum se arată mai jos. Este posibil să trebuiască să faceți clic pe `Save` de fiecare dată când Cline dorește să creeze un fișier.

![Generarea codului cu Cline](assets/cline-code-generation.png)

După generarea software-ului, agentul și-a finalizat sarcina și puteți rula aplicația. În acest caz, agentul a scris în trei fișiere: `index.html`, `script.js` și `styles.css`. Prin simpla dublă apăsare pe fișierul HTML, putem încărca și interacționa cu site-ul web generat.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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

## Pași următori

După generarea site-ului web, puteți continua să lucrați cu Cline pentru a-l îmbunătăți. Două posibile îmbunătățiri sunt:

- **Documentație**: Trimiterea promptului `Add a README` agentului este tot ce este necesar pentru ca acesta să genereze un fișier `README.md` care documentează site-ul web.
- **Animație**: Trimiteți modelului promptul `Add an animation that visually represents a large language model running on a laptop.` pentru a genera o animație pe site-ul web.

Îi încurajăm pe cititori să încerce să genereze alte aplicații folosind această configurare. Mai jos sunt câteva exemple amuzante pe care le-am încercat:

- **Jocuri arcade retro**: Încercați alte prompturi. Poate fi, de asemenea, distractiv ca agentul să creeze jocuri în stil retro în Python folosind pachetul `PyGame` cu următorul prompt:

```code
Create a simple pong game using the PyGame python package.
```

- **Analiza datelor**: Un domeniu în care agenții de codare sunt deosebit de utili este cel al scriptingului și al analizei datelor. Acesta este un prompt pentru a demonstra capacitatea modelului local de a genera software de analiză a datelor pentru vizualizarea prețurilor acțiunilor:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Resurse

Mai jos sunt câteva resurse suplimentare pentru a afla mai multe despre agenții de codare, Cline și rularea sarcinilor de lucru pe

* Mai multe informații despre parteneriatul și integrarea AMD cu LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Blogul AMD care prezintă rularea Cline pe AMD Ryzen™ AI și plăcile grafice Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Blogul Cline despre rularea agenților de codare local pe PC-uri AI: https://cline.bot/blog/local-models-amd