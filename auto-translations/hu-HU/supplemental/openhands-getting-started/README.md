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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Áttekintés

Az [OpenHands](https://github.com/All-Hands-AI/OpenHands) egy AI szoftverügynök,
amely kódot ír, parancsokat futtat, böngészi a webet, és fájlokat szerkeszt egy
valós munkaterületen. Ahelyett, hogy javaslatokat másolnál ki egy csevegőablakból,
rámutatsz az ügynökre egy projektmappára, és hagyod, hogy elvégezze a munkát:
implementáljon egy funkciót, javítson egy hibát, írjon teszteket, vagy
magyarázzon el egy kódbázist.

Az [Agent Canvas](https://github.com/OpenHands/agent-canvas) az ajánlott
böngészőalapú felhasználói felület az OpenHands futtatásához. Egyetlen
`agent-canvas` parancs elindítja az ügynökszervert, az automatizálási
háttérrendszert és a webes frontendet együtt, így a böngésződből folytathatsz
beszélgetést az ügynökkel.

Ahhoz, hogy minden az AMD rendszereden maradjon, az ügynök egy helyi modellel
kommunikál, amelyet a Lemonade Server szolgál ki. A Lemonade ezt a modellt egy
OpenAI-kompatibilis API-n keresztül teszi elérhetővé, így az Agent Canvas
ugyanúgy be tudja konfigurálni, mint bármely más OpenAI-stílusú végpontot,
miközben a modell, a kódod és a beszélgetés kontextusa mind a gépeden marad.

Ebben a leírásban elindítasz egy helyi modellt, elindítod az Agent Canvast,
ráirányítod arra a modellre, és futtatod az első kódolási feladatodat egy
valós projektmappán.

## Amit meg fogsz tanulni

- Hogyan indítsd el a Lemonade Servert, és győződj meg róla, hogy egy helyi
  modell válaszol a csevegési kérésekre
- Hogyan telepítsd és indítsd el az Agent Canvast az npm csomagból
- Hogyan konfiguráld az Agent Canvast, hogy egy helyi Lemonade modellt
  használjon LLM-ként
- Hogyan indíts egy OpenHands beszélgetést, és figyeld meg, ahogy az ügynök
  fájlokat szerkeszt és parancsokat futtat egy munkaterületen
- Hogyan tekintsd át, mit változtatott az ügynök, és irányítsd tovább
  utólagos üzenetekkel

## Alapfogalmak

| Fogalom | Mi ez | Hol illeszkedik ebbe a leírásba |
| --- | --- | --- |
| Lemonade Server | Egy AMD hardverre épített helyi LLM-kiszolgáló platform, amely OpenAI-kompatibilis API-t biztosít. Az adataid soha nem hagyják el a gépedet. | Futtatja azt a modellt, amely az ügynököt működteti. |
| OpenHands | Egy AI szoftverügynök, amely fájlokat olvas és szerkeszt, shell parancsokat futtat, és böngészi a webet egy munkaterületen belül. | Az ügynök, amelyet a csevegésből irányítasz. |
| Agent Canvas | A böngészőalapú felhasználói felület és háttérrendszer, amely futtatja az OpenHands beszélgetéseket, és megjeleníti az eszközhívásokat és fájlváltozásokat. | Elindítja a rendszert, és otthont ad a beszélgetésednek. |
| Munkaterület | A projektmappa, amelyet az ügynök olvashat és módosíthat. | Az ügynök szerkesztéseinek és parancsainak célpontja. |

<!-- @device:stx,krk -->

> [!NOTE]
> A kódoló ügynök munkafolyamatok nagyobb modellből és kontextusablakból
> profitálnak. Használj legalább 32 GB rendszermemóriát, és nagyobb GGUF
> modellekhez inkább 64 GB-ot vagy többet válassz.
<!-- @device:end -->

## Előfeltételek

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Szükséged lesz a következőkre:

- Telepített Lemonade Server, amely képes kiszolgálni az alábbi modellt.
- Node.js 22.12 vagy újabb verzió, valamint `npm` (az `agent-canvas` CLI
  használja).
- `uv`, a Python csomagkezelő, amelyet az Agent Canvas az ügynökszerver
  környezetének kezelésére használ. Ha a rendszereden még nincs telepítve,
  telepítsd az [uv telepítési útmutatóból](https://docs.astral.sh/uv/getting-started/installation/)
  az Agent Canvas indítása előtt.
- Egy projektmappa, amelyben dolgozni fogsz. Ez lehet bármilyen helyi git
  tárolóra vagy kódmappa, amelyen szeretnéd, hogy az ügynök dolgozzon.

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. Indítsd el a Lemonade Servert

Indítsd el a modellt a Lemonade CLI-ből:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

A Lemonade egy OpenAI-kompatibilis API-t tesz elérhetővé itt:

```text
http://127.0.0.1:13305/api/v1
```



## 2. Ellenőrizd a helyi modellt

Győződj meg róla, hogy a Lemonade ki tudja szolgálni a kiválasztott modellt:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Majd küldj egy kis csevegési kérést:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Ha ez egy `choices` tömböt ad vissza, a Lemonade készen áll az Agent Canvas
számára.

## 3. Az Agent Canvas telepítése és indítása

Telepítsd globálisan a közzétett Agent Canvas csomagot:

```bash
npm install -g @openhands/agent-canvas
```

Ezután indítsd el a teljes rendszert egy terminálból:

```bash
agent-canvas
```

Alapértelmezés szerint az Agent Canvas a `http://localhost:8000` címen indul.
Nyisd meg ezt az URL-t a böngésződben. Ha a 8000-es port már foglalt, add meg a
`--port` (vagy `-p`) kapcsolót az Agent Canvas indításakor:

```bash
agent-canvas --port 3000
```

Ugyanez a parancs Windows rendszeren PowerShellben is működik. Ekkor nyisd meg
a `http://localhost:3000` címet helyette. Az alapértelmezett helyi
háttérrendszernek egészségesként kell megjelennie a kezdőképernyőn.

Az `agent-canvas` parancs elindítja az ügynökszervert, az automatizálási
háttérrendszert és a webes frontendet együtt. Csak erre az egyetlen parancsra
van szükséged az OpenHands helyi futtatásához.

## 4. A helyi LLM konfigurálása

Első indításkor az Agent Canvas egy bevezető folyamatot indít. Ebben a
folyamatban:

1. Hagyd kiválasztva az **OpenHands** ügynököt, majd kattints a **Next**
   gombra.
2. A **Set up your LLM** részben válaszd az **Advanced** lehetőséget.
3. Hagyd az **Authentication** beállítást **API key** értéken.
4. Állítsd a **Custom Model** mezőt erre: `openai/Qwen3.6-35B-A3B-GGUF`.
5. Állítsd a **Base URL** mezőt erre: `http://127.0.0.1:13305/api/v1`.
6. Az **API Key** mezőbe írj be bármilyen nem üres helyőrző értéket, például
   `lemonade-local`. A Lemonade nem igényel valódi kulcsot, de az OpenHands
   kliensnek szüksége van egy értékre a küldéshez.
7. Kattints a **Next** gombra.

A kitöltött Advanced beállításoknak így kell kinézniük. Az API kulcs mezőt a
felhasználói felület elrejti.

![Az Agent Canvas első használatkor megjelenő LLM Advanced beállításai a Lemonade modellel és a helyi Base URL-lel](assets/01-llm-advanced-settings.png)

Az Agent Canvas ezeket az értékeket LLM-profilként menti el. Ha a verziód
kéri, hogy nevezd el ezt a profilt, használj szóköz nélküli nevet, például
`lemonade-local`. Ha később modellt váltasz, nyisd meg a **Settings > LLM**
menüt, és frissítsd ugyanazokat az Advanced mezőket. A mentett profilok között
a csevegési beviteli mezőből válthatsz a `/model` paranccsal.

## 5. Munkaterület megnyitása

Az ügynök csak a te által kiválasztott munkaterületen belüli fájlokat
olvashatja és módosíthatja. Egy feladat elindítása előtt irányítsd az Agent
Canvast a projektmappádra:

1. A kezdőképernyőről válaszd az **Open Workspace** lehetőséget.
2. Válaszd ki azt a mappát, amely a projektedet tartalmazza (például egy git
   tárolót, amelyen szeretnéd, hogy az ügynök dolgozzon).
3. Indíts egy új beszélgetést abban a munkaterületben.

Mindent, amit az ügynök végez – fájlok olvasása, parancsok futtatása, kód
szerkesztése –, arra a munkaterületre korlátozódik.

![Agent Canvas kezdőképernyő a bevezető folyamat után](assets/02-agent-canvas-home.png)
## 6. Az első kódolási feladat futtatása

A munkaterület megnyitása és a helyi LLM kiválasztása után írjon be egy konkrét feladatot a csevegésbe. Egy jó első feladat kicsi és ellenőrizhető, például:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Figyelje a beszélgetés idővonalát. Az OpenHands a következőket fogja tenni:

- Beolvassa a munkaterületet, hogy megértse a felépítést.
- Létrehozza a `hello.py` fájlt a kért függvénnyel és tesztblokkal.
- Opcionálisan lefuttatja a `python3 hello.py` parancsot az eredmény ellenőrzéséhez.
- Beszámol a csevegésben arról, hogy mit tett, és bármilyen parancs kimenetéről.

Az új fájlnak meg kell jelennie a munkaterületen, és az ügynök utolsó üzenetének le kell írnia az általa végrehajtott módosítást. Ez a kifizetődő pillanat: az ügynök valódi kódot írt és futtatott a projektmappájában.

## 7. Az ügynök munkájának áttekintése és irányítása

Miután az ügynök befejezett egy lépést, tekintse át a munkáját, mielőtt elfogadná a következőt:

- **Fájlváltozások**: használja a munkaterület fájlböngészőjét vagy az ügynök diff-nézetét, hogy pontosan lássa, mi került hozzáadásra, módosításra vagy törlésre.
- **Parancskimenet**: bontsa ki bármelyik parancsot, amelyet az ügynök futtatott, hogy megnézze a szabványos kimenetet, a hibakimenetet és a kilépési kódot.
- **Utókövetés**: ha az eredmény nem az, amit szeretett volna, válaszoljon ugyanabban a beszélgetésben egy javítással. Az ügynök megtartja az előző kontextust, és ugyanazokon a fájlokon dolgozik tovább.

Ha például a teszt nem a várt üdvözlést írta ki, válaszoljon így:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Az ügynök újra beolvassa a fájlt, lefuttatja a parancsot, diagnosztizálja a problémát, és ismét szerkeszti a fájlt — mindezt ugyanabban a beszélgetésben.

## Hibaelhárítás

- **Az `agent-canvas` nincs a PATH-on:** telepítse újra a `npm install -g @openhands/agent-canvas` paranccsal, és győződjön meg róla, hogy az npm globális bináris könyvtára szerepel a PATH-on. Windows rendszeren futtassa a `npm config get prefix` parancsot; a visszaadott könyvtárnak (gyakran `%APPDATA%\npm` vagy `%USERPROFILE%\.npm-global`) szerepelnie kell a felhasználói PATH-on, mielőtt az `agent-canvas` elindítható lenne egy új terminálból.
- **Az `npm install -g` engedélyezési hibával hiúsul meg:** állítson be egy felhasználó tulajdonában lévő globális npm könyvtárat, majd nyissa meg újra a terminált, és telepítse ismét az Agent Canvas-t.

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  Ahhoz, hogy a Windows PATH-módosítás tartós legyen, adja hozzá a `%USERPROFILE%\.npm-global` bejegyzést a felhasználói PATH-hoz a **Beállítások > Rendszer > Névjegy > Speciális rendszerbeállítások > Környezeti változók** menüpontban, majd nyisson meg egy új terminált.
  <!-- @os:end -->
- **A felhasználói felület betöltődik, de a háttérszolgáltatás nem egészséges állapotot mutat:** várjon néhány másodpercet, amíg az ügynökkiszolgáló elindul, majd frissítse az oldalt. Ha továbbra sem egészséges, indítsa újra az `agent-canvas`-t, és ellenőrizze a terminál kimenetét hibák szempontjából.
- **A Lemonade csevegési kérések kapcsolódási hibával hiúsulnak meg:** ellenőrizze, hogy a `curl -fsS "http://127.0.0.1:13305/api/v1/health"` sikeresen lefut-e, és hogy a Lemonade még mindig kiszolgálja-e a modellt a `lemonade status` paranccsal.
- **Az ügynök kontextushossz- vagy tokenkorlát-hibával hibázik:** indítsa újra a Lemonade-et egy nagyobb `ctx_size` értékkel (például `ctx_size=65536`), és kezdjen új beszélgetést, hogy az ügynök ne cipeljen túl nagy előzményt.
- **Az ügynök gyenge minőségű vagy hiányos szerkesztéseket készít:** váltson egy nagyobb modellre a Lemonade-ben, vagy adjon az ügynöknek egy kisebb, konkrétabb feladatot, és hagyja, hogy befejezze, mielőtt a következő módosítást kéri.
- **Az `uv` hiányzik:** telepítse innen:
  [uv telepítési útmutató](https://docs.astral.sh/uv/getting-started/installation/). Az Agent Canvas az `uv`-t használja az ügynökkiszolgáló Python-környezetének kezelésére.

## Következő lépések

- Próbáljon ki egy nagyobb feladatot ugyanabban a munkaterületben, például egy egységteszt-fájl hozzáadását vagy egy ismert hiba kijavítását, és tekintse át az ügynök diff-jét, mielőtt megtartaná a módosítást.
- Csatlakoztasson egy MCP-kiszolgálót, például GitHub-ot vagy Slack-et a **Testreszabás** alatt, hogy az ügynök munka közben olvashassa a hibajegyeket vagy közzétehessen frissítéseket.
- Mentsen el több LLM-profilt (egy gyors, kisebb modellt és egy erősebb, nagyobb modellt), és váltson közöttük a `/model` paranccsal a beszélgetés közben.
- Térjen át az [OpenHands automatizálásokra](https://docs.openhands.dev/openhands/usage/automations/overview), hogy az ismétlődő fejlesztési ciklusokat ütemezett vagy eseményvezérelt ügynökfuttatásokká alakítsa.

## Erőforrások

- [OpenHands dokumentáció](https://docs.openhands.dev/)
- [Agent Canvas áttekintés](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas beállítása](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-profilok és modellkonfiguráció](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server dokumentáció](https://lemonade-server.ai/docs)