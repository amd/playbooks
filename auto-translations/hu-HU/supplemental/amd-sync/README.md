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

# Távoli fejlesztés AMD Sync segítségével

## Áttekintés

Az **AMD Sync** távoli vezérlőpulttá alakítja a laptopodat az AMD Ryzen™ AI Halo számára. Kihagyhatod a manuális SSH-, kulcs- és IDE-beállítást – telepítsd az AMD Sync-et, és egy kattintással hozzáférhetsz egy távoli terminálhoz, a VS Code-hoz, a JupyterLab-hoz, valamint egy élő GPU/CPU/memória irányítópulthoz a Ryzen AI Halo-n.

A helyi géped ismerős marad; minden parancs, jegyzetfüzet és modell a Ryzen AI Halo-n fut.

> **Tipp**: Ez az oldal tartalmazza majd az AMDSync minden új frissítését. 

## Amit meg fogsz tanulni

- Az SSH engedélyezése a Ryzen AI Halo-n, és kapcsolódás hozzá az AMD Sync-ből
- A VS Code, Terminal, JupyterLab és Live Metrics indítása a Ryzen AI Halo-n egy kattintással
- A távoli munka szervezése az AMD Sync kezelt projektmappáinak segítségével

---

## Alapfogalmak

Az AMD Sync két oldalból áll: egy **kliensből** (a laptopod, amelyen az AMD Sync alkalmazás fut) és egy **szerverből** (a Ryzen AI Halo, amelyen egy SSH-szerver fut, amelybe az AMD Sync alagutat képez). Minden, amit az AMD Sync-ből indítasz – VS Code, terminál, jegyzetfüzet – helyileg nyílik meg, de a Ryzen AI Halo-n fut.

> **Támogatott kliensek:** Windows 11 és Linux. A macOS nem támogatott.

---

## 1. lépés – SSH engedélyezése a Ryzen AI Halo-n


> **Megjegyzés:** Windows rendszeren a Ryzen AI Halo alapértelmezetten *kikapcsolt* SSH-szerverrel érkezik. Linux rendszeren alapértelmezetten *bekapcsolt* SSH-szerverrel érkezik.

1. A Ryzen AI Halo-n nyisd meg az **AMD Ryzen™ AI Developer Center** alkalmazást.
2. Lépj a **Remote** fülre.
3. Kapcsold be az **SSH Server** opciót.
4. Jegyezd fel a **Server Information** alatt megjelenő **IP Address**, **Port** és **Username** adatokat – ezeket fogod beilleszteni az AMD Sync-be.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Megjegyzés:** Ez az AMD Developer Center Windows rendszerhez. A Linux verzió felülete eltérő lehet, de hasonló távoli funkciókkal rendelkezik.

> **Tipp:** Az AMD Sync az adott felhasználó **operációs rendszerbeli bejelentkezési jelszavát** kéri, nem a Developer Centerből származó jelszót.

---

## 2. lépés – Az AMD Sync telepítése a kliensgépen

Az AMD Sync Windows 11 és Linux rendszeren fut. Töltsd le a telepítőt az operációs rendszerednek megfelelően, majd kövesd az alábbi lépéseket. A telepítés után kattints az **Accept & Install** gombra a **Get Started** képernyőn – az AMD Sync automatikusan elindul, amint a folyamat befejeződött.

### Windows

[AMDSyncInstaller.exe letöltése](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kattints duplán az `AMDSyncInstaller.exe` fájlra.
2. Kattints az **Accept & Install** gombra.

> Ha a Windows Firewall megerősítést kér, engedélyezd az AMD Sync hálózati hozzáférését, hogy elérhesse a Ryzen AI Halo-t SSH-n keresztül.

### Linux

Kattints a linkre a kívánt formátum letöltéséhez:

| Formátum | Letöltés | Telepítési parancs |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Megjegyzés:** Az Ubuntu App Center figyelmeztethet, hogy egy helyileg megnyitott `.deb` fájl *„potenciálisan nem biztonságos.”* Ez a szokásos figyelmeztetés bármely harmadik féltől származó helyi telepítő esetén. Ha a `.deb` fájlra dupla kattintás nem működik, használd a fenti terminálparancsot.

---

## 3. lépés – Kapcsolódás a Ryzen AI Halo-hoz

Az első indításkor az AMD Sync megjeleníti az **Add a Remote Device** űrlapot. Töltsd ki a Developer Center **Remote** fülén található értékek alapján.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Mező | Megjegyzések |
|-------|-------|
| **Device Name** *(opcionális)* | Egy könnyen azonosítható megnevezés, például `Ryzen AI Halo`. Alapértelmezett érték: `Device 1`, `Device 2`, … |
| **Hostname or IP** | A Remote fülről |
| **SSH Port** | A Remote fülről (csak számok) |
| **Username** | Az operációs rendszerbeli fiókneved a Ryzen AI Halo-n |
| **Password** | Az operációs rendszerbeli bejelentkezési jelszavad – gépelés közben elrejtve |

Kattints az **Add Device** gombra. Egy rövid betöltési képernyő után megjelenik a **„Connection Successful”** üzenet, és a kezdő nézetbe kerülsz, amely a tálca értesítési területén található. Kattints a ablakon kívülre a bezárásához; az AMD Sync a háttérben futva marad, és egy kattintással elérhető.

> **Ha a kapcsolódás sikertelen,** az AMD Sync visszatér az űrlaphoz, a megadott értékek megmaradnak. A leggyakoribb okok: az SSH ki van kapcsolva a Ryzen AI Halo-n, hibás a jelszó, vagy a két eszköz eltérő hálózaton van.

---

## 4. lépés – Az első távoli eszköz elindítása

A kezdő nézet öt egykattintásos komponenst kínál – mindegyik elérhető, függetlenül attól, hogy a kliens és a Ryzen AI Halo melyik operációs rendszert futtatja.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponens | Mit csinál |
|-----------|--------------|
| **Directory** | Kiválasztja a Ryzen AI Halo-n azt a mappát, amelyben a VS Code, a Terminal és a JupyterLab megnyílik. Alapértelmezés szerint egy kezelt `Documents/AMD_Sync` munkaterület. |
| **VS Code** | Helyileg megnyitja a VS Code-ot egy SSH-alagúttal a kiválasztott mappába. |
| **Terminal** | Megnyit egy helyi terminált, amely SSH-kapcsolaton keresztül a Ryzen AI Halo-hoz csatlakozik, a kiválasztott mappában. |
| **JupyterLab** | Elindít egy jegyzetfüzet-projektet, amely SSH-kapcsolaton keresztül a Ryzen AI Halo-hoz csatlakozik, a kiválasztott mappára korlátozva. |
| **Live Metrics** | A GPU, a memória és a CPU kihasználtságának valós idejű megjelenítése a Ryzen AI Halo-n. |

### Próbáld ki a VS Code-ot

Az első indításhoz próbáld ki a **VS Code**-ot. A következő lépések Linuxra vonatkoznak, de a Windowson a folyamat hasonló.

1. Hagyd a **Directory** mezőt az alapértelmezett `~/Documents/AMD_Sync` értéken.
2. Kattints a **VS Code** gombra.
3. Az AMD Sync létrehozza a `Documents/AMD_Sync/Project_1` mappát a Ryzen AI Halo-n, és helyileg megnyitja a VS Code-ot, alagúton keresztül csatlakoztatva hozzá.

Most már olyan fájlokat szerkesztesz, amelyek a Ryzen AI Halo-n találhatók, a helyi VS Code beállításaiddal. Hozd létre a `helloworld.py` fájlt, add hozzá a `print("hello world")` sort, nyisd meg a beépített terminált (`` Ctrl + ` ``), és futtasd:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Az állapotsorban az **SSH: Linux** felirat jelenik meg – ez bizonyítja, hogy a kódod a Ryzen AI Halo-n fut, nem a laptopodon.
### Próbáld ki a Terminált

Kattints a **Terminal** elemre, hogy ugyanabba a mappába lépj be SSH-n keresztül anélkül, hogy el kellene hagynod a billentyűzetet.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows alatt az alapértelmezett terminál a **PowerShell** — válts a **Windows Command Prompt** opcióra a Beállítások menüben, ha azt preferálod. Linuxon az AMD Sync a rendszer alapértelmezett terminálját használja.

---

## Hogyan működik a Könyvtár

A **Directory** legördülő menü az AMD Sync legfontosabb vezérlőeleme — ez dönti el, hogy az általad elindított eszközök hova kerülnek a Ryzen AI Halo gépen.

- **`~/Documents/AMD_Sync` (alapértelmezett)** — Ha innen indítod el a VS Code-ot vagy a JupyterLab-ot, automatikusan létrejön egy új projektmappa (`Project_1`, `Project_2`, … a VS Code esetén; `Notebook_Project_1`, `Notebook_Project_2`, … a JupyterLab esetén).
- **Meglévő projektmappák** — Az `AMD_Sync` bármely közvetlen almappája (beleértve azokat is, amelyeket manuálisan hozol létre a Ryzen AI Halo gépen) megjelenik a legördülő menüben. A legutóbb használt mappa lesz az alapértelmezett a következő alkalommal.
- **Egyéni útvonalak** — Írj be bármilyen abszolút útvonalat, hogy megnyiss egy mappát a Ryzen AI Halo gép más helyén. Az AMD Sync csak *megnyitja* azt — nem hoz létre mappákat az `AMD_Sync` mappán kívül, és az egyéni útvonalak nem kerülnek mentésre a munkamenetek között.

Ha egy egyéni útvonal nem működik, az AMD Sync megmondja, miért: érvénytelen szintaxis, a mappa nem létezik, vagy az útvonal egy fájlra mutat.

---

## Élő metrikák és JupyterLab

- **Live Metrics** — A GPU, a memória és a CPU használatának élő irányítópultja. Ez a leggyorsabb módja annak, hogy megerősítsd, egy távoli tanítási folyamat valóban a hardvert terheli.
- **JupyterLab** — Egy teljes notebook projekt, amely SSH-n keresztül kapcsolódik a Ryzen AI Halo géphez, saját integrált terminállal, amellyel notebook cellákat és shell parancsokat kombinálhatsz anélkül, hogy elhagynád a felületet.

---

## Beállítások és több eszköz

A **Settings** menünek három fülje van:

| Fül | Mit tartalmaz |
|-----|----------------|
| **Devices** | Felsorolja az összes Ryzen AI Halo eszközt, amelyekhez sikeresen csatlakoztál. Újracsatlakozás, hitelesítő adatok szerkesztése, vagy új eszköz hozzáadása. |
| **Information** | Linkek a dokumentációhoz és a fórum támogatáshoz. |
| **Customize** | Az alkalmazás áthelyezése az asztalon, terminál típusának váltása (csak Windows), és az AMD Sync frissítések ellenőrzése. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminál típusa (Windows)** — Válassz a **PowerShell** (alapértelmezett) és a **Windows Command Prompt** között.
- **Terminál típusa (Linux)** — Csak a rendszer alapértelmezett terminálja érhető el.
- **Alkalmazás-frissítések** — Ez a fül megfelelő hely az új AMD Sync verziók ellenőrzésére és telepítésére a felületen belülről; nincs szükség külön frissítőeszközre.

> Egy eszköz csak az első sikeres csatlakozás után jelenik meg a **Devices** alatt, így a sikertelen próbálkozások nem zsúfolják tele a listát.

---

## Hibaelhárítás

- **A kapcsolódás azonnal sikertelen** — Ellenőrizd, hogy az SSH szerver engedélyezve van-e a Ryzen AI Halo gép **Remote** fülén a Developer Centerben.
- **Hibás jelszó hiba** — Használd az **OS bejelentkezési jelszavadat** a Ryzen AI Halo gépen, ne a Developer Centerből származó jelszavakat.
- **A VS Code gomb nem csinál semmit** — Telepítsd a VS Code-ot a kliens gépedre innen: [code.visualstudio.com](https://code.visualstudio.com).
- **Az AMD Sync tálca ikonja hiányzik (Linux/GNOME)** — Telepítsd és engedélyezd az AppIndicator bővítményt.
- **A `.deb` nem nyílik meg a fájlkezelőből** — Használd a `sudo apt install ./AMDSyncInstaller.deb` parancsot egy terminálból.
- **A beállítás minden indításkor újra megjelenik (Linux)**: oldd fel a bejelentkezési kulcstartódat, vagy indítsd el a `--password-store=gnome-libsecret` kapcsolóval, majd végezd el újra a beállítást egyszer.

---