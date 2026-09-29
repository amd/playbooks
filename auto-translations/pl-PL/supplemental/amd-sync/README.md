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

# Zdalne programowanie z AMD Sync

## Przegląd

**AMD Sync** zamienia Twój laptop w zdalny pulpit sterowania dla AMD Ryzen™ AI Halo. Pomiń ręczną konfigurację SSH, kluczy i IDE — zainstaluj AMD Sync i uzyskaj dostęp jednym kliknięciem do zdalnego terminala, VS Code, JupyterLab oraz na żywo aktualizowanego panelu GPU/CPU/pamięci na Ryzen AI Halo.

Twoja lokalna maszyna pozostaje znajoma; każde polecenie, notatnik i model działa na Ryzen AI Halo.

> **Wskazówka**: Ta strona będzie zawierać wszelkie nowe aktualizacje dotyczące AMDSync. 

## Czego się nauczysz

- Włączanie SSH na Ryzen AI Halo i łączenie się z nim z poziomu AMD Sync
- Uruchamianie VS Code, terminala, JupyterLab i Live Metrics dla Ryzen AI Halo jednym kliknięciem
- Organizowanie zdalnej pracy przy użyciu zarządzanych folderów projektów AMD Sync

---

## Kluczowe pojęcia

AMD Sync ma dwie strony: **klienta** (Twój laptop, na którym działa aplikacja AMD Sync) oraz **serwer** (Ryzen AI Halo, na którym działa serwer SSH, do którego AMD Sync tworzy tunel). Wszystko, co uruchamiasz z poziomu AMD Sync — VS Code, terminal, notatnik — otwiera się lokalnie, ale wykonuje się na Ryzen AI Halo.

> **Obsługiwani klienci:** Windows 11 i Linux. macOS nie jest obsługiwany.

---

## Krok 1 — Włącz SSH na Ryzen AI Halo


> **Uwaga:** W systemie Windows Ryzen AI Halo jest dostarczany z serwerem SSH *domyślnie wyłączonym*. W systemie Linux serwer SSH jest *domyślnie włączony*.

1. Na Ryzen AI Halo otwórz **AMD Ryzen™ AI Developer Center**.
2. Przejdź do zakładki **Remote**.
3. Włącz przełącznik **SSH Server**.
4. Zanotuj **IP Address**, **Port** oraz **Username** wyświetlane w sekcji **Server Information** — wkleisz je później do AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Uwaga:** To jest AMD Developer Center dla systemu Windows. Wersja dla Linuksa może mieć inny interfejs, ale podobną funkcjonalność zdalną.

> **Wskazówka:** AMD Sync pyta o **hasło logowania do systemu operacyjnego** danego użytkownika, a nie o hasło z Developer Center.

---

## Krok 2 — Zainstaluj AMD Sync na swoim kliencie

AMD Sync działa na systemach Windows 11 i Linux. Pobierz instalator dla swojego systemu operacyjnego, a następnie wykonaj poniższe kroki. Po instalacji kliknij **Accept & Install** na ekranie **Get Started** — AMD Sync uruchomi się automatycznie po zakończeniu.

### Windows

[Pobierz AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Kliknij dwukrotnie plik `AMDSyncInstaller.exe`.
2. Kliknij **Accept & Install**.

> Jeśli zapora systemu Windows wyświetli monit, zezwól AMD Sync na dostęp do sieci, aby mógł łączyć się z Ryzen AI Halo przez SSH.

### Linux

Kliknij łącze, aby pobrać preferowany format:

| Format | Pobieranie | Polecenie instalacji |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Uwaga:** Ubuntu App Center może oznaczyć lokalnie otwarty plik `.deb` jako *„Potencjalnie niebezpieczny”*. To standardowe ostrzeżenie dla każdego lokalnego instalatora firm trzecich. Jeśli dwukrotne kliknięcie pliku `.deb` się nie powiedzie, użyj powyższego polecenia w terminalu.

---

## Krok 3 — Połącz się ze swoim Ryzen AI Halo

Przy pierwszym uruchomieniu AMD Sync wyświetla formularz **Add a Remote Device**. Wypełnij go, korzystając z wartości z zakładki **Remote** w Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Pole | Uwagi |
|-------|-------|
| **Device Name** *(opcjonalnie)* | Przyjazna nazwa, np. `Ryzen AI Halo`. Domyślnie `Device 1`, `Device 2`, … |
| **Hostname or IP** | Z zakładki Remote |
| **SSH Port** | Z zakładki Remote (tylko cyfry) |
| **Username** | Nazwa Twojego konta systemowego na Ryzen AI Halo |
| **Password** | Twoje hasło logowania do systemu — maskowane podczas wpisywania |

Kliknij **Add Device**. Po krótkim ekranie ładowania zobaczysz komunikat **„Connection Successful”** i trafisz do widoku głównego, dostępnego w zasobniku systemowym. Kliknij poza oknem, aby je zamknąć — AMD Sync pozostaje uruchomiony i jest o jedno kliknięcie od Ciebie.

> **Jeśli połączenie się nie powiedzie,** AMD Sync wraca do formularza z zachowanymi wprowadzonymi wartościami. Zwykłymi przyczynami są wyłączone SSH na Ryzen AI Halo, nieprawidłowe hasło lub sytuacja, w której oba urządzenia znajdują się w różnych sieciach.

---

## Krok 4 — Uruchom swoje pierwsze zdalne narzędzie

Widok główny udostępnia pięć komponentów uruchamianych jednym kliknięciem — wszystkie dostępne niezależnie od systemu operacyjnego klienta i Ryzen AI Halo.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Komponent | Co robi |
|-----------|--------------|
| **Directory** | Wybiera folder na Ryzen AI Halo, w którym otworzą się VS Code, Terminal i JupyterLab. Domyślnie jest to zarządzany obszar roboczy `Documents/AMD_Sync`. |
| **VS Code** | Otwiera VS Code lokalnie z tunelem SSH do wybranego folderu. |
| **Terminal** | Otwiera lokalny terminal połączony przez SSH z Ryzen AI Halo, w wybranym folderze. |
| **JupyterLab** | Uruchamia projekt notatnika połączony przez SSH z Ryzen AI Halo, ograniczony do wybranego folderu. |
| **Live Metrics** | Widok wykorzystania GPU, pamięci i CPU na Ryzen AI Halo w czasie rzeczywistym. |

### Wypróbuj VS Code

Przy pierwszym uruchomieniu wypróbuj **VS Code**.

1. Pozostaw **Directory** na domyślnym `~/Documents/AMD_Sync`.
2. Kliknij **VS Code**.
3. AMD Sync utworzy folder `Documents/AMD_Sync/Project_1` na Ryzen AI Halo i otworzy VS Code lokalnie, z tunelem do niego.

Teraz edytujesz pliki znajdujące się na Ryzen AI Halo, korzystając z lokalnej konfiguracji VS Code. Utwórz plik `helloworld.py`, dodaj `print("hello world")`, otwórz zintegrowany terminal (`` Ctrl + ` ``) i uruchom go:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Pasek stanu wyświetla **SSH: Linux** — dowód, że Twój kod działa na Ryzen AI Halo, a nie na Twoim laptopie.
### Wypróbuj terminal

Kliknij **Terminal**, aby przejść do tego samego folderu przez SSH, nie odrywając rąk od klawiatury.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

W systemie Windows domyślnym terminalem jest **PowerShell** — jeśli wolisz, przełącz się na **Wiersz polecenia systemu Windows** w menu Ustawienia. W systemie Linux AMD Sync korzysta z domyślnego terminala systemowego.

---

## Jak działa katalog

Rozwijana lista **Katalog** to najważniejszy element sterujący w AMD Sync — decyduje o tym, gdzie na Ryzen AI Halo trafia każde uruchamiane narzędzie.

- **`~/Documents/AMD_Sync` (domyślnie)** — Uruchomienie VS Code lub JupyterLab z tego miejsca automatycznie tworzy nowy folder projektu (`Project_1`, `Project_2`, … dla VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … dla JupyterLab).
- **Istniejące foldery projektów** — Każdy bezpośredni podfolder `AMD_Sync` (w tym foldery utworzone ręcznie na Ryzen AI Halo) pojawia się na rozwijanej liście. Ostatnio używany folder staje się domyślnym przy następnym uruchomieniu.
- **Niestandardowe ścieżki** — Wpisz dowolną ścieżkę bezwzględną, aby otworzyć folder znajdujący się gdzie indziej na Ryzen AI Halo. AMD Sync jedynie *otwiera* taki folder — nie tworzy folderów poza `AMD_Sync`, a niestandardowe ścieżki nie są zapisywane między sesjami.

Jeśli niestandardowa ścieżka nie działa, AMD Sync informuje dlaczego: nieprawidłowa składnia, folder nie istnieje lub ścieżka wskazuje na plik.

---

## Metryki na żywo i JupyterLab

- **Metryki na żywo** — Panel z bieżącymi danymi o wykorzystaniu GPU, pamięci i CPU. Najszybszy sposób na potwierdzenie, że zdalny trening rzeczywiście obciąża sprzęt.
- **JupyterLab** — Pełny projekt notebooka połączony przez SSH z Ryzen AI Halo, z własnym zintegrowanym terminalem umożliwiającym łączenie komórek notebooka i poleceń powłoki bez opuszczania interfejsu.

---

## Ustawienia i wiele urządzeń

Menu **Ustawienia** zawiera trzy karty:

| Karta | Co obejmuje |
|-----|----------------|
| **Urządzenia** | Zawiera listę wszystkich Ryzen AI Halo, z którymi udało się nawiązać połączenie. Umożliwia ponowne połączenie, edycję danych logowania lub dodanie nowego urządzenia. |
| **Informacje** | Odnośniki do dokumentacji i wsparcia na forum. |
| **Personalizacja** | Zmiana położenia aplikacji na pulpicie, przełączanie typu terminala (tylko Windows) oraz sprawdzanie aktualizacji AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Typ terminala (Windows)** — Wybór między **PowerShell** (domyślnie) a **Wierszem polecenia systemu Windows**.
- **Typ terminala (Linux)** — Dostępny jest tylko domyślny terminal systemowy.
- **Aktualizacje aplikacji** — Ta karta to właściwe miejsce, aby sprawdzić i zainstalować nowe wersje AMD Sync bezpośrednio z poziomu interfejsu; oddzielny program aktualizujący nie jest potrzebny.

> Urządzenie pojawia się w zakładce **Urządzenia** dopiero po pomyślnym pierwszym połączeniu, dzięki czemu nieudane próby nie zaśmiecają listy.

---

## Rozwiązywanie problemów

- **Połączenie od razu się nie udaje** — Sprawdź, czy serwer SSH jest włączony na karcie **Remote** w Developer Center na Ryzen AI Halo.
- **Błąd nieprawidłowego hasła** — Użyj **hasła logowania do systemu operacyjnego** na Ryzen AI Halo, a nie haseł pobranych z Developer Center.
- **Przycisk VS Code nic nie robi** — Zainstaluj VS Code na swoim komputerze klienckim ze strony [code.visualstudio.com](https://code.visualstudio.com).
- **Brak ikony AMD Sync w zasobniku systemowym (Linux/GNOME)** — Zainstaluj i włącz rozszerzenie AppIndicator.
- **Plik `.deb` nie otwiera się z poziomu menedżera plików** — Użyj polecenia `sudo apt install ./AMDSyncInstaller.deb` w terminalu.
- **Konfiguracja pojawia się przy każdym uruchomieniu (Linux)**: odblokuj pęk kluczy logowania lub uruchom z parametrem `--password-store=gnome-libsecret`, a następnie jeszcze raz przeprowadź konfigurację.

---