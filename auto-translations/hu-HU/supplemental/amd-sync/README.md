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

# Távoli fejlesztés az AMD Sync segítségével

## Áttekintés

Az **AMD Sync** a laptopodat távoli irányítóközponttá alakítja az AMD Ryzen™ AI Halo eléréséhez. Kerüld el a manuális SSH-, kulcs- és IDE-beállítást — telepítsd az AMD Sync alkalmazást, és egy kattintással hozzáférhetsz egy távoli terminálhoz, a VS Code-hoz, a JupyterLab-hoz, valamint egy élő GPU/CPU/memória irányítópulthoz a Ryzen AI Halo-n.

A helyi géped ugyanaz marad, mint eddig; minden parancs, notebook és modell a Ryzen AI Halo-n fut.

> **Tipp**: Ez az oldal tartalmazza majd az AMDSync-hez kapcsolódó frissítéseket. 

## Amit meg fogsz tanulni

- Az SSH engedélyezése a Ryzen AI Halo-n, és kapcsolódás hozzá az AMD Sync-ből
- A VS Code, a Terminal, a JupyterLab és az Élő metrikák indítása a Ryzen AI Halo felé egy kattintással
- A távoli munka rendszerezése az AMD Sync kezelt projektmappáival

---

## Alapfogalmak

Az AMD Syncnek két oldala van: egy **kliens** (a laptopod, amelyen az AMD Sync alkalmazás fut) és egy **szerver** (a Ryzen AI Halo, amelyen egy SSH-szerver fut, amelybe az AMD Sync alagutat épít). Bármit is indítasz az AMD Sync-ből — VS Code-ot, terminált, notebookot — az helyileg nyílik meg, de a Ryzen AI Halo-n fut le.

> **Támogatott kliensek:** Windows 11 és Linux. A macOS nem támogatott.

---

## 1. lépés — Az SSH engedélyezése a Ryzen AI Halo-n


> **Megjegyzés:** Windows rendszeren a Ryzen AI Halo *alapértelmezetten kikapcsolt* SSH-szerverrel érkezik. Linuxon *alapértelmezetten bekapcsolt* SSH-szerverrel érkezik.

1. A Ryzen AI Halo-n nyisd meg az **AMD Ryzen™ AI Developer Center**-t.
2. Menj a **Remote** fülre.
3. Kapcsold be az **SSH Server** opciót.
4. Jegyezd fel a **Server Information** alatt megjelenő **IP Address**, **Port** és **Username** értékeket — ezeket be fogod illeszteni az AMD Sync-be.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Megjegyzés:** Ez az AMD Developer Center Windows-verziója. A Linux-verzió felhasználói felülete eltérhet, de a távoli funkciók hasonlóak.

> **Tipp:** Az AMD Sync az adott felhasználó **operációs rendszerbeli bejelentkezési jelszavát** kéri, nem a Developer Centerhez tartozó jelszót.

---

## 2. lépés — Az AMD Sync telepítése a kliensgépeden

Az AMD Sync Windows 11-en és Linuxon fut. Töltsd le a saját operációs rendszeredhez tartozó telepítőt, majd kövesd az alábbi lépéseket. A telepítés után kattints az **Accept & Install** gombra a **Get Started** képernyőn — az AMD Sync a folyamat végén automatikusan elindul.

### Windows

[AMDSyncInstaller.exe letöltése](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kattints duplán az `AMDSyncInstaller.exe` fájlra.
2. Kattints az **Accept & Install** gombra.

> Ha a Windows Tűzfal engedélyt kér, engedélyezd az AMD Sync számára a hálózati hozzáférést, hogy elérhesse a Ryzen AI Halo-t SSH-n keresztül.

### Linux

Kattints a linkre a kívánt formátum letöltéséhez:

| Formátum | Letöltés | Telepítő parancs |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Megjegyzés:** Az Ubuntu App Center figyelmeztetést adhat egy helyileg megnyitott `.deb` fájlra, hogy *"Potenciálisan nem biztonságos."* Ez a szokásos figyelmeztetés bármely harmadik féltől származó helyi telepítő esetén. Ha a `.deb` fájlra való dupla kattintás nem működik, használd a fenti terminálparancsot.

---

## 3. lépés — Kapcsolódás a Ryzen AI Halo-hoz

Az első indításkor az AMD Sync megjeleníti az **Add a Remote Device** űrlapot. Töltsd ki a Developer Center **Remote** fülén található értékek alapján.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Mező | Megjegyzések |
|-------|-------|
| **Device Name** *(opcionális)* | Egy könnyen felismerhető címke, például `Ryzen AI Halo`. Alapértelmezés szerint `Device 1`, `Device 2`, … |
| **Hostname or IP** | A Remote fülről |
| **SSH Port** | A Remote fülről (csak számok) |
| **Username** | Az operációs rendszeres fiókod neve a Ryzen AI Halo-n |
| **Password** | Az operációs rendszeres bejelentkezési jelszavad — gépelés közben rejtve marad |

Kattints az **Add Device** gombra. Egy rövid betöltő képernyő után megjelenik a **"Connection Successful"** üzenet, és megérkezel a főképernyőre, amely a rendszertálcán él tovább. Kattints az ablakon kívülre a bezáráshoz; az AMD Sync tovább fut a háttérben, és egy kattintással elérhető.

> **Ha a kapcsolódás sikertelen,** az AMD Sync visszatér az űrlaphoz, a korábban megadott értékekkel. A leggyakoribb okok az, hogy az SSH ki van kapcsolva a Ryzen AI Halo-n, hibás a jelszó, vagy a két eszköz eltérő hálózaton van.

---

## 4. lépés — Az első távoli eszköz elindítása

A főképernyő öt, egy kattintással elérhető komponenst kínál — ezek mindegyike elérhető, függetlenül attól, hogy a kliens és a Ryzen AI Halo milyen operációs rendszert futtat.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponens | Mit csinál |
|-----------|--------------|
| **Directory** | Kiválasztja azt a mappát a Ryzen AI Halo-n, amelyben a VS Code, a Terminal és a JupyterLab megnyílik. Alapértelmezés szerint egy kezelt `Documents/AMD_Sync` munkaterület. |
| **VS Code** | Helyileg megnyitja a VS Code-ot egy SSH-alagúttal a kiválasztott mappához. |
| **Terminal** | Egy helyi terminált nyit meg, amely SSH-kapcsolaton keresztül csatlakozik a Ryzen AI Halo-hoz, a kiválasztott mappában. |
| **JupyterLab** | Elindít egy notebook projektet, amely SSH-kapcsolaton keresztül csatlakozik a Ryzen AI Halo-hoz, a kiválasztott mappára korlátozva. |
| **Live Metrics** | Valós idejű nézet a Ryzen AI Halo GPU-, memória- és CPU-kihasználtságáról. |

### Próbáld ki a VS Code-ot

Az első indításhoz próbáld ki a **VS Code**-ot.

1. Hagyd a **Directory** mezőt az alapértelmezett `~/Documents/AMD_Sync` értéken.
2. Kattints a **VS Code** gombra.
3. Az AMD Sync létrehozza a `Documents/AMD_Sync/Project_1` mappát a Ryzen AI Halo-n, és helyileg megnyitja a VS Code-ot, alagutazva ehhez a mappához.

Most már olyan fájlokat szerkesztesz, amelyek a Ryzen AI Halo-n élnek, a helyi VS Code beállításaiddal. Hozz létre egy `helloworld.py` fájlt, add hozzá a `print("hello world")` sort, nyisd meg az integrált terminált (`` Ctrl + ` ``), és futtasd:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Az állapotsáv **SSH: Linux** feliratot mutat — ez a bizonyíték arra, hogy a kódod a Ryzen AI Halo-n fut, nem a laptopodon.
### A Terminál kipróbálása

Kattintson a **Terminal** gombra, hogy SSH-n keresztül ugyanabba a mappába lépjen be anélkül, hogy elhagyná a billentyűzetet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows rendszeren az alapértelmezett terminál a **PowerShell** — ha inkább mást szeretne, válthat **Windows Command Prompt**-ra a Settings menüben. Linux rendszeren az AMD Sync a rendszer alapértelmezett terminálját használja.

---

## Hogyan működik a Directory

A **Directory** legördülő menü az AMD Sync legfontosabb vezérlőeleme — ez határozza meg, hogy az elindított eszközök hova kerülnek a Ryzen AI Halo eszközön.

- **`~/Documents/AMD_Sync` (alapértelmezett)** — Ha innen indítja a VS Code-ot vagy a JupyterLab-ot, automatikusan egy új projektmappa jön létre (`Project_1`, `Project_2`, … a VS Code esetén; `Notebook_Project_1`, `Notebook_Project_2`, … a JupyterLab esetén).
- **Meglévő projektmappák** — Az `AMD_Sync` bármely közvetlen almappája (beleértve a Ryzen AI Halo eszközön manuálisan létrehozott mappákat is) megjelenik a legördülő menüben. A legutóbb használt mappa lesz az alapértelmezett a következő alkalommal.
- **Egyéni elérési utak** — Írjon be bármilyen abszolút elérési utat, hogy a Ryzen AI Halo eszköz egy másik mappáját nyissa meg. Az AMD Sync csak *megnyitja* azt — nem hoz létre mappákat az `AMD_Sync` mappán kívül, és az egyéni elérési utak nem kerülnek mentésre a munkamenetek között.

Ha egy egyéni elérési út nem működik, az AMD Sync megmondja, miért: érvénytelen szintaxis, a mappa nem létezik, vagy az elérési út egy fájlra mutat.

---

## Live Metrics és JupyterLab

- **Live Metrics** — A GPU, a memória és a CPU használatának élő irányítópultja. Ez a leggyorsabb módja annak, hogy megerősítse: egy távoli tanítási folyamat valóban a hardvert terheli.
- **JupyterLab** — Egy teljes notebook projekt, amely SSH-n keresztül kapcsolódik a Ryzen AI Halo eszközhöz, saját integrált terminállal, így a notebook cellák és a shell parancsok keverhetők anélkül, hogy elhagyná a felületet.

---

## Settings és több eszköz

A **Settings** menünek három lapja van:

| Lap | Mit tartalmaz |
|-----|----------------|
| **Devices** | Felsorolja az összes Ryzen AI Halo eszközt, amelyhez sikeresen csatlakozott. Újracsatlakozhat, szerkesztheti a hitelesítő adatokat, vagy hozzáadhat egy új eszközt. |
| **Information** | Hivatkozások a dokumentációhoz és a fórum támogatásához. |
| **Customize** | Az alkalmazás áthelyezése az asztalon, a terminál típusának váltása (csak Windows), és az AMD Sync frissítéseinek ellenőrzése. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminál típusa (Windows)** — Válasszon a **PowerShell** (alapértelmezett) és a **Windows Command Prompt** között.
- **Terminál típusa (Linux)** — Csak a rendszer alapértelmezett terminálja érhető el.
- **Alkalmazásfrissítések** — Ez a lap a megfelelő hely az AMD Sync új verzióinak kereséséhez és telepítéséhez közvetlenül a felületről; nincs szükség külön frissítőprogramra.

> Egy eszköz csak az első sikeres csatlakozás után jelenik meg a **Devices** alatt, így a sikertelen próbálkozások nem zsúfolják tele a listát.

---

## Hibaelhárítás

- **A kapcsolódás azonnal sikertelen** — Ellenőrizze, hogy az SSH szerver engedélyezve van-e a Ryzen AI Halo eszköz Developer Center alkalmazásának **Remote** lapján.
- **Hibás jelszó hiba** — Használja az **OS bejelentkezési jelszavát** a Ryzen AI Halo eszközön, ne a Developer Centerből vett jelszavakat.
- **A VS Code gomb nem csinál semmit** — Telepítse a VS Code-ot a kliensgépén a [code.visualstudio.com](https://code.visualstudio.com) oldalról.
- **Az AMD Sync tálcaikonja hiányzik (Linux/GNOME)** — Telepítse és engedélyezze az AppIndicator kiterjesztést.
- **A `.deb` nem nyílik meg a fájlkezelőből** — Használja a `sudo apt install ./AMDSyncInstaller.deb` parancsot egy terminálból.
- **A telepítés minden indításkor újra megjelenik (Linux)**: oldja fel a bejelentkezési kulcstartót, vagy indítsa el a `--password-store=gnome-libsecret` kapcsolóval, majd végezze el újra a telepítést egyszer.

---