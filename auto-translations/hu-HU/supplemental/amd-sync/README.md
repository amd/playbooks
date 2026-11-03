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

# Távoli fejlesztés az AMD Sync használatával

## Áttekintés

Az **AMD Sync** az AMD Ryzen™ AI Halo távvezérlő pultjává alakítja a laptopodat. Kihagyhatod a manuális SSH-, kulcs- és IDE-beállítást — telepítsd az AMD Sync-et, és máris egy kattintással hozzáférsz egy távoli terminálhoz, a VS Code-hoz, a JupyterLab-hoz, valamint egy élő GPU/CPU/memória irányítópulthoz a Ryzen AI Halo-n.

A helyi géped megszokott marad; minden parancs, jegyzetfüzet és modell a Ryzen AI Halo-n fut.

> **Tipp**: Ez az oldal tartalmazza majd az AMDSync összes új frissítését.

## Amit meg fogsz tanulni

- SSH engedélyezése a Ryzen AI Halo-n, és kapcsolódás hozzá az AMD Sync-ből
- A VS Code, a Terminal, a JupyterLab és a Live Metrics indítása a Ryzen AI Halo-n egy kattintással
- A távoli munka rendszerezése az AMD Sync kezelt projektmappáinak segítségével

---

## Alapfogalmak

Az AMD Sync-nek két oldala van: egy **kliens** (a laptopod, amelyen az AMD Sync alkalmazás fut) és egy **szerver** (a Ryzen AI Halo, amelyen egy SSH-szerver fut, amelybe az AMD Sync alagutat épít). Minden, amit az AMD Sync-ből indítasz — VS Code, terminál, jegyzetfüzet — helyben nyílik meg, de a Ryzen AI Halo-n fut.

> **Támogatott kliensek:** Windows 11 és Linux. A macOS nem támogatott.

---

## 1. lépés — SSH engedélyezése a Ryzen AI Halo-n

> **Megjegyzés:** Windows alatt a Ryzen AI Halo *alapértelmezés szerint kikapcsolt* SSH-szerverrel érkezik. Linux alatt *alapértelmezés szerint bekapcsolt* SSH-szerverrel.

1. A Ryzen AI Halo-n nyisd meg az **AMD Ryzen™ AI Developer Center**-t.
2. Lépj a **Remote** fülre.
3. Kapcsold be az **SSH Server** kapcsolót.
4. Jegyezd fel a **Server Information** alatt megjelenő **IP Address**, **Port** és **Username** értékeket — ezeket be kell majd illesztened az AMD Sync-be.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Megjegyzés:** Ez az AMD Developer Center Windows verziója. A Linux verzió felülete eltérhet, de hasonló távoli funkciókkal rendelkezik.

> **Tipp:** Az AMD Sync az adott felhasználó **operációs rendszer bejelentkezési jelszavát** kéri, nem a Developer Centerhez tartozó jelszót.

---

## 2. lépés — Az AMD Sync telepítése a kliensgépeden

Az AMD Sync Windows 11 és Linux rendszereken fut. Töltsd le az operációs rendszerednek megfelelő telepítőt, majd kövesd az alábbi lépéseket. A telepítés után kattints az **Accept & Install** gombra a **Get Started** képernyőn — az AMD Sync a folyamat végén automatikusan elindul.

### Windows

[AMDSyncInstaller.exe letöltése](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kattints duplán az `AMDSyncInstaller.exe` fájlra.
2. Kattints az **Accept & Install** gombra.

> Ha a Windows tűzfal figyelmeztetést jelenít meg, engedélyezd az AMD Sync hálózati hozzáférését, hogy elérhesse a Ryzen AI Halo-t SSH-n keresztül.

### Linux

Kattints a linkre a kívánt formátum letöltéséhez:

| Formátum | Letöltés | Telepítési parancs |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Megjegyzés:** Az Ubuntu App Center egy helyben megnyitott `.deb` fájlt *"Potenciálisan nem biztonságosnak"* jelölhet meg. Ez a szokásos figyelmeztetés bármely külső fejlesztőtől származó helyi telepítő esetén. Ha a `.deb` fájlra duplán kattintva nem sikerül a telepítés, használd a fenti terminálparancsot.

---

## 3. lépés — Kapcsolódás a Ryzen AI Halo-hoz

Első indításkor az AMD Sync megjeleníti az **Add a Remote Device** űrlapot. Töltsd ki a Developer Center **Remote** fülén található értékek alapján.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Mező | Megjegyzések |
|-------|-------|
| **Device Name** *(opcionális)* | Egy könnyen felismerhető címke, például `Ryzen AI Halo`. Alapértelmezett értéke `Device 1`, `Device 2`, … |
| **Hostname or IP** | A Remote fülről |
| **SSH Port** | A Remote fülről (csak számok) |
| **Username** | Az operációs rendszer felhasználói fiókod neve a Ryzen AI Halo-n |
| **Password** | Az operációs rendszer bejelentkezési jelszava — gépelés közben elrejtve |

Kattints az **Add Device** gombra. Egy rövid betöltő képernyő után megjelenik a **"Connection Successful"** üzenet, és a főnézetre kerülsz, amely a rendszertálcádban él. Kattints a mezőn kívülre az elrejtéséhez; az AMD Sync tovább fut a háttérben, és egy kattintással elérhető.

> **Ha a kapcsolódás sikertelen,** az AMD Sync visszatér az űrlaphoz a megadott értékekkel. A leggyakoribb okok: az SSH le van tiltva a Ryzen AI Halo-n, hibás a jelszó, vagy a két eszköz különböző hálózaton van.

---

## 4. lépés — Az első távoli eszköz indítása

A főnézet öt egykattintásos komponenst kínál — mindegyik elérhető, függetlenül attól, hogy melyik operációs rendszeren fut a kliens és a Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponens | Mit csinál |
|-----------|--------------|
| **Directory** | Kiválasztja azt a mappát a Ryzen AI Halo-n, amelyben a VS Code, a Terminal és a JupyterLab megnyílik. Alapértelmezés szerint egy kezelt `Documents/AMD_Sync` munkaterületet használ. |
| **VS Code** | Megnyitja a VS Code-ot helyben, egy SSH-alagúton keresztül a kiválasztott mappához kapcsolódva. |
| **Terminal** | Megnyit egy helyi terminált, amely SSH-n keresztül kapcsolódik a Ryzen AI Halo-hoz, a kiválasztott mappában. |
| **JupyterLab** | Elindít egy jegyzetfüzet-projektet, amely SSH-n keresztül kapcsolódik a Ryzen AI Halo-hoz, a kiválasztott mappára korlátozva. |
| **Live Metrics** | Valós idejű nézet a Ryzen AI Halo GPU-, memória- és CPU-kihasználtságáról. |

### Próbáld ki a VS Code-ot

Az első indításhoz próbáld ki a **VS Code**-ot.

1. Hagyd a **Directory** mezőt az alapértelmezett `~/Documents/AMD_Sync` értéken.
2. Kattints a **VS Code**-ra.
3. Az AMD Sync létrehozza a `Documents/AMD_Sync/Project_1` mappát a Ryzen AI Halo-n, és helyben megnyitja a VS Code-ot, ehhez alagutazva.

Most már olyan fájlokat szerkesztesz, amelyek a Ryzen AI Halo-n élnek, a saját, helyi VS Code beállításaiddal. Hozd létre a `helloworld.py` fájlt, add hozzá a `print("hello world")` sort, nyisd meg a beépített terminált (`` Ctrl + ` ``), és futtasd:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Az állapotsorban a **SSH: Linux** felirat olvasható — ez bizonyítja, hogy a kódod a Ryzen AI Halo-n fut, nem a laptopodon.
### Próbáld ki a Terminál funkciót

Kattints a **Terminál** gombra, hogy SSH kapcsolaton keresztül ugyanabba a mappába lépj be anélkül, hogy elhagynád a billentyűzetet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows rendszeren az alapértelmezett terminál a **PowerShell** — válts át **Windows Command Prompt**-ra a Beállítások menüben, ha inkább azt preferálod. Linux rendszeren az AMD Sync a rendszer alapértelmezett terminálját használja.

---

## Hogyan működik a Könyvtár

A **Könyvtár** legördülő menü az AMD Sync legfontosabb vezérlőeleme — ez határozza meg, hogy az elindított eszközök hova kerülnek a Ryzen AI Halo eszközön.

- **`~/Documents/AMD_Sync` (alapértelmezett)** — Ha innen indítod a VS Code-ot vagy a JupyterLab-ot, automatikusan létrejön egy új projektmappa (`Project_1`, `Project_2`, … a VS Code esetén; `Notebook_Project_1`, `Notebook_Project_2`, … a JupyterLab esetén).
- **Meglévő projektmappák** — Az `AMD_Sync` közvetlen almappái (beleértve a Ryzen AI Halo eszközön manuálisan létrehozott mappákat is) megjelennek a legördülő menüben. A legutóbb használt mappa lesz az alapértelmezett a következő alkalommal.
- **Egyéni útvonalak** — Írj be bármilyen abszolút elérési utat, hogy a Ryzen AI Halo eszközön máshol lévő mappát nyisd meg. Az AMD Sync csak *megnyitja* azt — nem hoz létre mappákat az `AMD_Sync`-en kívül, és az egyéni útvonalak nem kerülnek mentésre a munkamenetek között.

Ha egy egyéni útvonal nem működik, az AMD Sync megmondja, miért: érvénytelen szintaxis, a mappa nem létezik, vagy az útvonal egy fájlra mutat.

---

## Élő metrikák és JupyterLab

- **Élő metrikák** — A GPU, memória és CPU használatának élő irányítópultja. Ez a leggyorsabb módja annak, hogy megerősítsd, egy távoli tanítási folyamat valóban a hardvert terheli.
- **JupyterLab** — Egy teljes notebook-projekt, amely SSH-n keresztül csatlakozik a Ryzen AI Halo eszközhöz, saját integrált terminállal a notebook cellák és a shell parancsok keveréséhez anélkül, hogy elhagynád a felhasználói felületet.

---

## Beállítások és több eszköz

A **Beállítások** menünek három fülje van:

| Fül | Miről szól |
|-----|----------------|
| **Eszközök** | Felsorolja az összes Ryzen AI Halo eszközt, amelyhez sikeresen csatlakoztál. Csatlakozz újra, szerkeszd a hitelesítő adatokat, vagy adj hozzá új eszközt. |
| **Információk** | Linkek a dokumentációhoz és a fórumos támogatáshoz. |
| **Testreszabás** | Helyezd át az alkalmazást az asztalon, válts terminál típust (csak Windows esetén), és ellenőrizd az AMD Sync frissítéseket. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminál típusa (Windows)** — Válassz a **PowerShell** (alapértelmezett) és a **Windows Command Prompt** között.
- **Terminál típusa (Linux)** — Csak az alapértelmezett rendszer terminál érhető el.
- **Alkalmazásfrissítések** — Ez a fül a megfelelő hely az AMD Sync új verzióinak ellenőrzésére és telepítésére a felhasználói felületről; nincs szükség külön frissítőprogramra.

> Egy eszköz csak az első sikeres csatlakozás után jelenik meg az **Eszközök** alatt, így a sikertelen próbálkozások nem zsúfolják tele a listát.

---

## Hibaelhárítás

- **A kapcsolódás azonnal meghiúsul** — Ellenőrizd, hogy az SSH szerver engedélyezve van-e a Ryzen AI Halo eszköz **Remote** fülén a Developer Centerben.
- **Hibás jelszó hiba** — Használd az **OS bejelentkezési jelszavadat** a Ryzen AI Halo eszközön, ne a Developer Centerből származó jelszavakat.
- **A VS Code gomb nem csinál semmit** — Telepítsd a VS Code-ot a kliens gépedre a [code.visualstudio.com](https://code.visualstudio.com) oldalról.
- **Hiányzik az AMD Sync tálcaikon (Linux/GNOME)** — Telepítsd és engedélyezd az AppIndicator bővítményt.
- **A `.deb` fájl nem nyílik meg a fájlkezelőből** — Használd a `sudo apt install ./AMDSyncInstaller.deb` parancsot egy terminálból.
- **A beállítás minden indításkor újra megjelenik (Linux)**: oldd fel a bejelentkezési kulcstartót, vagy indítsd el a `--password-store=gnome-libsecret` opcióval, majd végezd el egyszer újra a beállítást.

---