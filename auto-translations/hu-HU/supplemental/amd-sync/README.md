<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Távoli fejlesztés AMD Sync segítségével

## Áttekintés

Az **AMD Sync** laptopját egy AMD Ryzen™ AI Halo távoli vezérlőpultjává alakítja. Felejtse el a manuális SSH-, kulcs- és IDE-beállítást — telepítse az AMD Sync alkalmazást, és egyetlen kattintással érjen el egy távoli terminált, VS Code-ot, JupyterLabot, valamint egy élő GPU/CPU/memória-irányítópultot a Ryzen AI Halo eszközön.

A helyi gép megszokott marad; minden parancs, notebook és modell a Ryzen AI Halo eszközön fut.

> **Tipp**: Ez az oldal tartalmazza az AMDSync összes új frissítését.

## Mit fog megtanulni

- SSH engedélyezése a Ryzen AI Halo eszközön és csatlakozás hozzá az AMD Sync segítségével
- VS Code, Terminal, JupyterLab és élő metrikák indítása a Ryzen AI Halo eszközön egyetlen kattintással
- Távoli munka szervezése az AMD Sync kezelt projektmappáival

---

## Alapfogalmak

Az AMD Sync két részből áll: egy **kliens** (a laptopja, amelyen az AMD Sync alkalmazás fut) és egy **szerver** (a Ryzen AI Halo, amelyen egy SSH-szerver fut, amelybe az AMD Sync alagutat épít). Minden, amit az AMD Sync-ből indít el — VS Code, terminál, notebook — helyileg nyílik meg, de a Ryzen AI Halo eszközön hajtódik végre.

> **Támogatott kliensek:** Windows 11 és Linux. A macOS nem támogatott.

---

## 1. lépés — SSH engedélyezése a Ryzen AI Halo eszközön


> **Megjegyzés:** Windows rendszeren a Ryzen AI Halo alapértelmezés szerint *kikapcsolt* SSH-szerverrel érkezik. Linux rendszeren az SSH-szerver *alapértelmezés szerint be van kapcsolva*.

1. A Ryzen AI Halo eszközön nyissa meg az **AMD Ryzen™ AI Developer Center** alkalmazást.
2. Lépjen a **Remote** fülre.
3. Kapcsolja be az **SSH Server** kapcsolót.
4. Jegyezze fel a **Server Information** alatt megjelenő **IP Address**, **Port** és **Username** értékeket — ezeket fogja beilleszteni az AMD Sync-be.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Megjegyzés:** Ez a Windows rendszerhez készült AMD Developer Center. A Linux verziónak eltérő felhasználói felülete lehet, de hasonló távoli funkciókkal rendelkezik.

> **Tipp:** Az AMD Sync az adott felhasználó **operációs rendszerbeli bejelentkezési jelszavát** kéri, nem a Developer Centerből származó jelszót.

---

## 2. lépés — Az AMD Sync telepítése a kliensre

Az AMD Sync Windows 11 és Linux rendszeren fut. Töltse le az operációs rendszeréhez megfelelő telepítőt, majd kövesse az alábbi lépéseket. A telepítés után kattintson az **Accept & Install** gombra az **Get Started** képernyőn — az AMD Sync automatikusan elindul, amikor a telepítés befejeződik.

### Windows

[Töltse le az AMDSyncInstaller.exe fájlt](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kattintson duplán az `AMDSyncInstaller.exe` fájlra.
2. Kattintson az **Accept & Install** gombra.

> Ha a Windows tűzfal kérdést tesz fel, engedélyezze az AMD Sync hálózati hozzáférését, hogy SSH-n keresztül elérhesse a Ryzen AI Halo eszközt.

### Linux

Kattintson a hivatkozásra a kívánt formátum letöltéséhez:

| Formátum | Letöltés | Telepítési parancs |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Megjegyzés:** Az Ubuntu App Center egy helyileg megnyitott `.deb` fájlt *„Potenciálisan nem biztonságos"* figyelmeztetéssel jelölhet meg. Ez a szokásos figyelmeztetés minden harmadik féltől származó helyi telepítőre vonatkozik. Ha a `.deb` fájlra duplán kattintva nem sikerül a telepítés, használja a fenti terminálparancsot.

---

## 3. lépés — Csatlakozás a Ryzen AI Halo eszközhöz

Az első indításkor az AMD Sync megjeleníti az **Add a Remote Device** űrlapot. Töltse ki a Developer Center **Remote** füléről származó értékekkel.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Mező | Megjegyzések |
|-------|-------|
| **Device Name** *(nem kötelező)* | Egy barátságos elnevezés, például `Ryzen AI Halo`. Alapértelmezés szerint `Device 1`, `Device 2`, … |
| **Hostname or IP** | A Remote fülről |
| **SSH Port** | A Remote fülről (csak számok) |
| **Username** | Az operációs rendszerbeli fióknevét a Ryzen AI Halo eszközön |
| **Password** | Az operációs rendszerbeli bejelentkezési jelszava — gépelés közben elrejtve jelenik meg |

Kattintson az **Add Device** gombra. Egy rövid betöltési képernyő után megjelenik a **„Connection Successful"** üzenet, és a főnézetre kerül, amely a rendszertálcán él. Kattintson az ablakon kívülre az elrejtéséhez; az AMD Sync tovább fut, és egyetlen kattintással elérhető.

> **Ha a csatlakozás sikertelen,** az AMD Sync visszatér az űrlaphoz a megőrzött értékekkel. A szokásos okok: az SSH le van tiltva a Ryzen AI Halo eszközön, helytelen jelszó, vagy a két eszköz különböző hálózatokon van.

---

## 4. lépés — Az első távoli eszköz indítása

A főnézet öt egyetlen kattintással elérhető összetevőt kínál — mindegyik elérhető, függetlenül attól, hogy a kliens és a Ryzen AI Halo milyen operációs rendszert futtat.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Összetevő | Mit csinál |
|-----------|--------------|
| **Directory** | Kiválasztja a Ryzen AI Halo eszközön lévő mappát, amelybe a VS Code, a Terminal és a JupyterLab megnyílik. Alapértelmezés szerint egy kezelt `Documents/AMD_Sync` munkaterületre mutat. |
| **VS Code** | Helyileg megnyitja a VS Code-ot egy SSH-alagúttal a kiválasztott mappába. |
| **Terminal** | Megnyit egy helyi terminált, amely SSH-n keresztül csatlakozik a Ryzen AI Halo eszközhöz, a kiválasztott mappában. |
| **JupyterLab** | Elindít egy notebook-projektet SSH-n keresztül csatlakozva a Ryzen AI Halo eszközhöz, a kiválasztott mappára korlátozva. |
| **Live Metrics** | A Ryzen AI Halo eszközön lévő GPU, memória és CPU kihasználtságának valós idejű nézete. |

### Próbálja ki a VS Code-ot

Az első indításhoz próbálja ki a **VS Code**-ot.

1. Hagyja a **Directory** beállítást az alapértelmezett `~/Documents/AMD_Sync` értéken.
2. Kattintson a **VS Code** gombra.
3. Az AMD Sync létrehozza a `Documents/AMD_Sync/Project_1` mappát a Ryzen AI Halo eszközön, és helyileg megnyitja a VS Code-ot, alagutazva abba.

Most olyan fájlokat szerkeszt, amelyek a Ryzen AI Halo eszközön találhatók, a helyi VS Code beállításával. Hozzon létre egy `helloworld.py` fájlt, adja hozzá a `print("hello world")` sort, nyissa meg az integrált terminált (`` Ctrl + ` ``), és futtassa:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Az állapotsor **SSH: Linux** feliratot mutat — ez bizonyítja, hogy a kód a Ryzen AI Halo eszközön fut, nem a laptopján.

### Próbálja ki a Terminált

Kattintson a **Terminal** gombra, hogy billentyűzet elhagyása nélkül SSH-n keresztül ugyanabba a mappába ugorjon.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows rendszeren az alapértelmezett terminál a **PowerShell** — váltson **Windows Command Prompt** módra a Beállítások menüből, ha azt részesíti előnyben. Linux rendszeren az AMD Sync az alapértelmezett rendszerterminált használja.

---

## Hogyan működik a Directory

A **Directory** legördülő menü az AMD Sync legfontosabb vezérlője — ez határozza meg, hogy minden indított eszköz hol landol a Ryzen AI Halo eszközön.

- **`~/Documents/AMD_Sync` (alapértelmezett)** — A VS Code vagy a JupyterLab innen való indítása automatikusan létrehoz egy új projektmappát (`Project_1`, `Project_2`, … a VS Code esetén; `Notebook_Project_1`, `Notebook_Project_2`, … a JupyterLab esetén).
- **Meglévő projektmappák** — Az `AMD_Sync` közvetlen gyermekei (beleértve a Ryzen AI Halo eszközön manuálisan létrehozott mappákat is) megjelennek a legördülő menüben. Az utoljára használt mappa lesz az alapértelmezett a következő alkalommal.
- **Egyéni elérési utak** — Írjon be bármilyen abszolút elérési utat egy máshol lévő mappa megnyitásához a Ryzen AI Halo eszközön. Az AMD Sync csak *megnyitja* — nem hoz létre mappákat az `AMD_Sync`-en kívül, és az egyéni elérési utak nem kerülnek mentésre a munkamenetek között.

Ha egy egyéni elérési út nem működik, az AMD Sync megmondja az okát: érvénytelen szintaxis, a mappa nem létezik, vagy az elérési út egy fájlra mutat.

---

## Live Metrics és JupyterLab

- **Live Metrics** — A GPU, memória és CPU kihasználtságának élő irányítópultja. A leggyorsabb módja annak megerősítésére, hogy egy távoli tanítási folyamat valóban eléri a hardvert.
- **JupyterLab** — Egy teljes notebook-projekt SSH-n keresztül csatlakozva a Ryzen AI Halo eszközhöz, saját integrált terminállal a notebook-cellák és shell-parancsok keveréséhez anélkül, hogy elhagyná a felhasználói felületet.

---

## Beállítások és több eszköz

A **Settings** menünek három füle van:

| Fül | Mit fed le |
|-----|----------------|
| **Devices** | Felsorolja az összes Ryzen AI Halo eszközt, amelyhez sikeresen csatlakozott. Újracsatlakozás, hitelesítő adatok szerkesztése vagy új eszköz hozzáadása. |
| **Information** | Hivatkozások a dokumentációhoz és a fórum-támogatáshoz. |
| **Customize** | Az alkalmazás átpozicionálása az asztalon, termináltípus váltása (csak Windows), és az AMD Sync frissítéseinek ellenőrzése. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Termináltípus (Windows)** — Válasszon a **PowerShell** (alapértelmezett) és a **Windows Command Prompt** között.
- **Termináltípus (Linux)** — Csak az alapértelmezett rendszerterminál érhető el.
- **Alkalmazásfrissítések** — Ez a fül a megfelelő hely az új AMD Sync verziók ellenőrzéséhez és telepítéséhez a felhasználói felületen belül; nincs szükség külön frissítőre.

> Egy eszköz csak az első sikeres csatlakozás után jelenik meg az **Devices** alatt, így a sikertelen kísérletek nem zsúfolják tele a listát.

---

## Hibaelhárítás

- **A csatlakozás azonnal meghiúsul** — Ellenőrizze, hogy az SSH-szerver engedélyezve van-e a Ryzen AI Halo eszközön a Developer Center **Remote** fülén.
- **Helytelen jelszó hiba** — Használja a Ryzen AI Halo eszközön lévő **operációs rendszerbeli bejelentkezési jelszavát**, ne a Developer Centerből származó jelszavakat.
- **A VS Code gomb nem csinál semmit** — Telepítse a VS Code-ot a kliensgépre a [code.visualstudio.com](https://code.visualstudio.com) oldalról.
- **Az AMD Sync tálcaikon hiányzik (Linux/GNOME)** — Telepítse és engedélyezze az AppIndicator bővítményt.
- **A `.deb` fájl nem nyílik meg a fájlkezelőből** — Használja a `sudo apt install ./AMDSyncInstaller.deb` parancsot egy terminálból.

---