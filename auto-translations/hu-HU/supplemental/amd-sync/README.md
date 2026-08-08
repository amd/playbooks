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

Az **AMD Sync** a laptopját egy távoli irányítópulttá alakítja az AMD Ryzen™ AI Halo számára. Hagyja ki a manuális SSH-, kulcs- és IDE-beállítást — telepítse az AMD Sync-et, és egy kattintással hozzáférhet a távoli terminálhoz, a VS Code-hoz, a JupyterLab-hoz, valamint egy élő GPU/CPU/memória irányítópulthoz a Ryzen AI Halo-n.

A helyi gépe ismerős marad; minden parancs, notebook és modell a Ryzen AI Halo-n fut.

> **Tipp**: Ez az oldal tartalmazza majd az AMDSync összes új frissítését.

## Amit meg fog tanulni

- SSH engedélyezése a Ryzen AI Halo-n, és kapcsolódás hozzá az AMD Sync-ből
- A VS Code, a Terminal, a JupyterLab és a Live Metrics indítása egy kattintással a Ryzen AI Halo-hoz kapcsolódva
- A távoli munka rendszerezése az AMD Sync kezelt projektmappáival

---

## Alapfogalmak

Az AMD Syncnek két oldala van: egy **kliens** (a laptopja, amelyen az AMD Sync alkalmazás fut) és egy **szerver** (a Ryzen AI Halo, amelyen egy SSH-szerver fut, amelybe az AMD Sync alagutat épít). Minden, amit az AMD Sync-ből indít — VS Code, terminál, notebook — helyileg nyílik meg, de a Ryzen AI Halo-n fut.

> **Támogatott kliensek:** Windows 11 és Linux. A macOS nem támogatott.

---

## 1. lépés — Az SSH engedélyezése a Ryzen AI Halo-n


> **Megjegyzés:** Windows rendszeren a Ryzen AI Halo *alapértelmezés szerint kikapcsolt* SSH-szerverrel érkezik. Linuxon *alapértelmezés szerint bekapcsolva* jön.

1. A Ryzen AI Halo-n nyissa meg az **AMD Ryzen™ AI Developer Center** alkalmazást.
2. Lépjen a **Remote** fülre.
3. Kapcsolja be az **SSH Server** opciót.
4. Jegyezze fel a **Server Information** alatt megjelenő **IP Address**, **Port** és **Username** értékeket — ezeket be kell majd illesztenie az AMD Sync-be.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Megjegyzés:** Ez az AMD Developer Center Windows rendszerhez. A Linux verzió felülete eltérhet, de hasonló távoli funkciókat kínál.

> **Tipp:** Az AMD Sync az adott felhasználó **operációs rendszer bejelentkezési jelszavát** kéri, nem a Developer Centerből származó jelszót.

---

## 2. lépés — Az AMD Sync telepítése a kliensre

Az AMD Sync Windows 11 és Linux rendszeren fut. Töltse le az Ön operációs rendszerének megfelelő telepítőt, majd kövesse az alábbi lépéseket. A telepítés után kattintson az **Accept & Install** gombra a **Get Started** képernyőn — az AMD Sync a befejezéskor automatikusan elindul.

### Windows

[AMDSyncInstaller.exe letöltése](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kattintson duplán az `AMDSyncInstaller.exe` fájlra.
2. Kattintson az **Accept & Install** gombra.

> Ha a Windows tűzfal jelzést küld, engedélyezze az AMD Sync hálózati hozzáférését, hogy elérhesse a Ryzen AI Halo-t SSH-n keresztül.

### Linux

Kattintson a linkre a kívánt formátum letöltéséhez:

| Formátum | Letöltés | Telepítő parancs |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Megjegyzés:** Az Ubuntu App Center a helyben megnyitott `.deb` fájlt *„Potenciálisan nem biztonságos”*-ként jelölheti meg. Ez a szokásos figyelmeztetés bármely helyi harmadik féltől származó telepítő esetén. Ha a `.deb` fájlra való dupla kattintás nem működik, használja a fenti terminálparancsot.

---

## 3. lépés — Kapcsolódás a Ryzen AI Halo-hoz

Az első indításkor az AMD Sync megjeleníti az **Add a Remote Device** űrlapot. Töltse ki a Developer Center **Remote** füléről származó értékekkel.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Mező | Megjegyzések |
|-------|-------|
| **Device Name** *(opcionális)* | Egy könnyen felismerhető címke, például `Ryzen AI Halo`. Alapértelmezés: `Device 1`, `Device 2`, … |
| **Hostname or IP** | A Remote fülről |
| **SSH Port** | A Remote fülről (csak számok) |
| **Username** | Az operációs rendszer felhasználói fiókjának neve a Ryzen AI Halo-n |
| **Password** | Az operációs rendszer bejelentkezési jelszava — gépelés közben elrejtve |

Kattintson az **Add Device** gombra. Egy rövid betöltési képernyő után megjelenik a **„Connection Successful”** üzenet, majd a kezdőnézet, amely a rendszertálcáján érhető el. Kattintson az ablakon kívülre az elrejtéséhez; az AMD Sync tovább fut, és egy kattintásra van.

> **Ha a kapcsolódás sikertelen,** az AMD Sync visszatér az űrlaphoz, megőrizve a megadott értékeket. A leggyakoribb okok: az SSH le van tiltva a Ryzen AI Halo-n, hibás jelszó, vagy a két eszköz eltérő hálózaton van.

---

## 4. lépés — Az első távoli eszköz elindítása

A kezdőnézet öt, egy kattintással elérhető komponenst kínál — ezek mindegyike elérhető, függetlenül attól, hogy a kliens és a Ryzen AI Halo milyen operációs rendszert futtat.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponens | Mit csinál |
|-----------|--------------|
| **Directory** | Kiválasztja azt a mappát a Ryzen AI Halo-n, amelyben a VS Code, a Terminal és a JupyterLab megnyílik. Alapértelmezés szerint egy kezelt `Documents/AMD_Sync` munkaterület. |
| **VS Code** | Helyileg megnyitja a VS Code-ot egy SSH-alagúttal a kiválasztott mappához. |
| **Terminal** | Helyi terminált nyit, amely SSH-kapcsolaton keresztül csatlakozik a Ryzen AI Halo-hoz, a kiválasztott mappában. |
| **JupyterLab** | Egy notebook projektet indít, amely SSH-kapcsolaton keresztül csatlakozik a Ryzen AI Halo-hoz, a kiválasztott mappára korlátozva. |
| **Live Metrics** | A GPU, a memória és a CPU kihasználtságának valós idejű nézete a Ryzen AI Halo-n. |

### Próbálja ki a VS Code-ot

Az első indításhoz próbálja ki a **VS Code**-ot.

1. Hagyja a **Directory** mezőt az alapértelmezett `~/Documents/AMD_Sync` értéken.
2. Kattintson a **VS Code** gombra.
3. Az AMD Sync létrehozza a `Documents/AMD_Sync/Project_1` mappát a Ryzen AI Halo-n, és helyileg megnyitja a VS Code-ot, alagúton keresztül csatlakoztatva hozzá.

Ezzel olyan fájlokat szerkeszt, amelyek a Ryzen AI Halo-n élnek, a helyi VS Code beállításaival. Hozzon létre egy `helloworld.py` fájlt, adja hozzá a `print("hello world")` sort, nyissa meg az integrált terminált (`` Ctrl + ` ``), és futtassa:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Az állapotsor a **SSH: Linux** szöveget mutatja — ez bizonyítja, hogy a kódja a Ryzen AI Halo-n fut, nem a laptopján.
### Próbálja ki a Terminált

Kattintson a **Terminal** gombra, hogy ugyanabba a mappába lépjen be SSH-n keresztül, anélkül, hogy el kellene hagynia a billentyűzetet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows rendszeren az alapértelmezett terminál a **PowerShell** — ha inkább mást szeretne, váltson **Windows Command Prompt**-ra a Settings menüben. Linux rendszeren az AMD Sync a rendszer alapértelmezett terminálját használja.

---

## Hogyan működik a Directory

A **Directory** legördülő menü a legfontosabb vezérlőelem az AMD Sync-ben — ez dönti el, hogy az elindított eszközök hova kerülnek a Ryzen AI Halo eszközön.

- **`~/Documents/AMD_Sync` (alapértelmezett)** — Ha innen indítja a VS Code-ot vagy a JupyterLab-ot, automatikusan új projektmappa jön létre (`Project_1`, `Project_2`, … a VS Code esetén; `Notebook_Project_1`, `Notebook_Project_2`, … a JupyterLab esetén).
- **Meglévő projektmappák** — Az `AMD_Sync` bármely közvetlen almappája (beleértve a Ryzen AI Halo eszközön manuálisan létrehozott mappákat is) megjelenik a legördülő menüben. A legutóbb használt mappa lesz az alapértelmezett a következő alkalommal.
- **Egyedi elérési utak** — Írjon be bármilyen abszolút elérési utat, hogy a Ryzen AI Halo eszköz egy másik mappáját nyissa meg. Az AMD Sync csak *megnyitja* a mappát — nem hoz létre mappákat az `AMD_Sync`-en kívül, és az egyedi elérési utak nem kerülnek mentésre a munkamenetek között.

Ha egy egyedi elérési út nem működik, az AMD Sync közli az okát: érvénytelen szintaxis, a mappa nem létezik, vagy az elérési út egy fájlra mutat.

---

## Live Metrics és JupyterLab

- **Live Metrics** — A GPU, a memória és a CPU használatának élő irányítópultja. A leggyorsabb módja annak, hogy megerősítse, egy távoli betanítási folyamat valóban terheli a hardvert.
- **JupyterLab** — Egy teljes notebook projekt, amely SSH-kapcsolaton keresztül csatlakozik a Ryzen AI Halo eszközhöz, saját integrált terminállal, amellyel a notebook cellák és a shell parancsok keverhetők anélkül, hogy el kellene hagyni a felületet.

---

## Settings és több eszköz

A **Settings** menünek három lapja van:

| Lap | Mit tartalmaz |
|-----|----------------|
| **Devices** | Felsorolja az összes Ryzen AI Halo eszközt, amelyhez sikeresen csatlakozott. Újracsatlakozás, hitelesítő adatok szerkesztése, vagy új eszköz hozzáadása. |
| **Information** | Hivatkozások a dokumentációhoz és a fórumos támogatáshoz. |
| **Customize** | Az alkalmazás áthelyezése az asztalon, terminál típusának váltása (csak Windows), és az AMD Sync frissítéseinek ellenőrzése. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminál típusa (Windows)** — Válasszon a **PowerShell** (alapértelmezett) és a **Windows Command Prompt** között.
- **Terminál típusa (Linux)** — Csak a rendszer alapértelmezett terminálja érhető el.
- **Alkalmazásfrissítések** — Ez a lap a megfelelő hely az AMD Sync új verzióinak ellenőrzésére és telepítésére közvetlenül a felületről; nincs szükség külön frissítőprogramra.

> Egy eszköz csak az első sikeres csatlakozás után jelenik meg a **Devices** alatt, így a sikertelen próbálkozások nem zsúfolják tele a listát.

---

## Hibaelhárítás

- **A csatlakozás azonnal meghiúsul** — Ellenőrizze, hogy az SSH szerver engedélyezve van-e a Ryzen AI Halo eszköz Developer Center alkalmazásának **Remote** lapján.
- **Hibás jelszó hiba** — Használja az **OS bejelentkezési jelszavát** a Ryzen AI Halo eszközön, ne a Developer Centerből vett jelszavakat.
- **A VS Code gomb nem csinál semmit** — Telepítse a VS Code-ot a kliens gépére a [code.visualstudio.com](https://code.visualstudio.com) oldalról.
- **Az AMD Sync tálcaikonja hiányzik (Linux/GNOME)** — Telepítse és engedélyezze az AppIndicator kiterjesztést.
- **A `.deb` fájl nem nyílik meg a fájlkezelőből** — Használja a `sudo apt install ./AMDSyncInstaller.deb` parancsot egy terminálból.

---