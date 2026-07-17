<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Bu playbook, GitHub'ın işleyemediği özel etiketler kullanmaktadır. Bu içeriği doğru şekilde önizlemek için lütfen [amd.com/playbooks](https://amd.com/playbooks) adresini ziyaret edin.
<!-- @github-only:end -->

# AMD Sync ile Uzak Geliştirme

## Genel Bakış

**AMD Sync**, dizüstü bilgisayarınızı AMD Ryzen™ AI Halo için uzak bir kontrol merkezine dönüştürür. Manuel SSH, anahtar ve IDE kurulumunu atlayın — AMD Sync'i yükleyin ve Ryzen AI Halo üzerinde uzak terminal, VS Code, JupyterLab ve canlı GPU/CPU/bellek panosuna tek tıklamayla erişin.

Yerel makineniz tanıdık kalmaya devam eder; her komut, not defteri ve model Ryzen AI Halo üzerinde çalışır.

> **İpucu**: Bu sayfa, AMDSync'e yönelik tüm yeni güncellemeleri içerecektir.

## Neler Öğreneceksiniz

- Ryzen AI Halo üzerinde SSH'ı etkinleştirme ve AMD Sync'ten bağlanma
- AMD Sync ile tek tıklamayla Ryzen AI Halo'ya karşı VS Code, Terminal, JupyterLab ve Canlı Metrikler başlatma
- AMD Sync'in yönetilen proje klasörlerini kullanarak uzak çalışmayı düzenleme

---

## Temel Kavramlar

AMD Sync'in iki tarafı vardır: bir **istemci** (AMD Sync uygulamasını çalıştıran dizüstü bilgisayarınız) ve bir **sunucu** (AMD Sync'in tünel açtığı bir SSH sunucusu çalıştıran Ryzen AI Halo). AMD Sync'ten başlattığınız her şey — VS Code, terminal, not defteri — yerel olarak açılır ancak Ryzen AI Halo üzerinde çalışır.

> **Desteklenen istemciler:** Windows 11 ve Linux. macOS desteklenmemektedir.

---

## Adım 1 — Ryzen AI Halo'da SSH'ı Etkinleştirme


> **Not:** Windows'ta Ryzen AI Halo, SSH sunucusu *varsayılan olarak kapalı* şekilde gelir. Linux'ta ise SSH sunucusu *varsayılan olarak açık* şekilde gelir.

1. Ryzen AI Halo'da **AMD Ryzen™ AI Developer Center**'ı açın.
2. **Remote** sekmesine gidin.
3. **SSH Server**'ı açık konuma getirin.
4. **Server Information** altında gösterilen **IP Address**, **Port** ve **Username** bilgilerini not edin — bunları AMD Sync'e yapıştıracaksınız.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Not:** Bu, Windows için AMD Developer Center'dır. Linux sürümünün kullanıcı arayüzü farklı olabilir, ancak benzer uzak işlevselliğe sahiptir.

> **İpucu:** AMD Sync, Developer Center'dan bir parola değil, o kullanıcının **işletim sistemi oturum açma parolasını** ister.

---

## Adım 2 — İstemcinize AMD Sync'i Yükleme

AMD Sync, Windows 11 ve Linux üzerinde çalışır. İşletim sisteminiz için yükleyiciyi indirin, ardından aşağıdaki adımları izleyin. Kurulumun ardından **Get Started** ekranında **Accept & Install** seçeneğine tıklayın — AMD Sync tamamlandığında otomatik olarak başlar.

### Windows

[AMDSyncInstaller.exe'yi İndirin](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe` dosyasına çift tıklayın.
2. **Accept & Install** seçeneğine tıklayın.

> Windows Güvenlik Duvarı sizi uyarırsa, AMD Sync'in SSH üzerinden Ryzen AI Halo'ya ulaşabilmesi için ağ erişimine izin verin.

### Linux

Tercih ettiğiniz formatı indirmek için bağlantıya tıklayın:

| Format | İndirme | Kurulum komutu |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Not:** Ubuntu App Center, yerel olarak açılan bir `.deb` dosyasını *"Potansiyel olarak güvensiz"* şeklinde işaretleyebilir. Bu, herhangi bir üçüncü taraf yerel yükleyici için standart bir uyarıdır. `.deb` dosyasına çift tıklamak başarısız olursa, yukarıdaki terminal komutunu kullanın.

---

## Adım 3 — Ryzen AI Halo'nuza Bağlanma

İlk başlatmada AMD Sync, **Add a Remote Device** formunu gösterir. Developer Center'ın **Remote** sekmesindeki değerleri kullanarak doldurun.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Alan | Notlar |
|-------|-------|
| **Device Name** *(isteğe bağlı)* | `Ryzen AI Halo` gibi kolay bir etiket. Varsayılan olarak `Device 1`, `Device 2`, … şeklindedir. |
| **Hostname or IP** | Remote sekmesinden |
| **SSH Port** | Remote sekmesinden (yalnızca sayılar) |
| **Username** | Ryzen AI Halo'daki işletim sistemi hesap adınız |
| **Password** | İşletim sistemi oturum açma parolanız — yazarken gizlenir |

**Add Device** seçeneğine tıklayın. Kısa bir yükleme ekranının ardından **"Connection Successful"** mesajını görecek ve sistem tepsisinde yaşayan ana görünüme geçeceksiniz. Pencereyi kapatmak için dışına tıklayın; AMD Sync çalışmaya devam eder ve tek tıklamayla erişilebilir.

> **Bağlantı başarısız olursa,** AMD Sync değerleriniz korunmuş şekilde forma geri döner. Olağan nedenler şunlardır: Ryzen AI Halo'da SSH'ın devre dışı olması, yanlış parola veya iki cihazın farklı ağlarda bulunması.

---

## Adım 4 — İlk Uzak Aracınızı Başlatma

Ana görünüm size beş tek tıklamalı bileşen sunar — istemci ve Ryzen AI Halo'nun hangi işletim sistemini çalıştırdığından bağımsız olarak hepsi kullanılabilir.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Bileşen | Ne yapar |
|-----------|--------------|
| **Directory** | Ryzen AI Halo'da VS Code, Terminal ve JupyterLab'ın açılacağı klasörü seçer. Varsayılan olarak yönetilen `Documents/AMD_Sync` çalışma alanına ayarlanır. |
| **VS Code** | VS Code'u yerel olarak, seçilen klasöre SSH tüneli ile açar. |
| **Terminal** | Seçilen klasörde Ryzen AI Halo'ya SSH ile bağlı yerel bir terminal açar. |
| **JupyterLab** | Seçilen klasörün kapsamında, Ryzen AI Halo'ya SSH ile bağlı bir not defteri projesi başlatır. |
| **Live Metrics** | Ryzen AI Halo'daki GPU, bellek ve CPU kullanımının gerçek zamanlı görünümü. |

### VS Code'u Deneyin

İlk başlatma için **VS Code**'u deneyin.

1. **Directory**'yi varsayılan `~/Documents/AMD_Sync` olarak bırakın.
2. **VS Code**'a tıklayın.
3. AMD Sync, Ryzen AI Halo'da `Documents/AMD_Sync/Project_1` oluşturur ve VS Code'u yerel olarak, bu klasöre tünel açarak açar.

Artık Ryzen AI Halo'da yaşayan dosyaları yerel VS Code kurulumunuzla düzenliyorsunuz. `helloworld.py` oluşturun, `print("hello world")` ekleyin, entegre terminali açın (`` Ctrl + ` ``) ve çalıştırın:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

Durum çubuğunda **SSH: Linux** yazar — bu, kodunuzun dizüstü bilgisayarınızda değil Ryzen AI Halo'da çalıştığının kanıtıdır.

### Terminali Deneyin

Klavyeden ayrılmadan aynı klasöre SSH üzerinden girmek için **Terminal**'e tıklayın.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows'ta varsayılan terminal **PowerShell**'dir — tercih ederseniz Ayarlar menüsünden **Windows Command Prompt**'a geçebilirsiniz. Linux'ta AMD Sync, varsayılan sistem terminalinizi kullanır.

---

## Directory Nasıl Çalışır

**Directory** açılır menüsü, AMD Sync'teki en önemli kontroldür — başlattığınız her aracın Ryzen AI Halo'da nereye yerleşeceğini belirler.

- **`~/Documents/AMD_Sync` (varsayılan)** — Buradan VS Code veya JupyterLab başlatmak otomatik olarak yeni bir proje klasörü oluşturur (VS Code için `Project_1`, `Project_2`, …; JupyterLab için `Notebook_Project_1`, `Notebook_Project_2`, …).
- **Mevcut proje klasörleri** — `AMD_Sync`'in doğrudan alt öğeleri (Ryzen AI Halo'da manuel olarak oluşturduğunuz klasörler dahil) açılır menüde görünür. En son kullandığınız klasör, bir sonraki seferde varsayılan olur.
- **Özel yollar** — Ryzen AI Halo'da başka bir yerdeki klasörü açmak için herhangi bir mutlak yol yazın. AMD Sync yalnızca onu *açar* — `AMD_Sync` dışında klasör oluşturmaz ve özel yollar oturumlar arasında kaydedilmez.

Özel bir yol çalışmazsa AMD Sync size nedenini söyler: geçersiz sözdizimi, klasör mevcut değil veya yol bir dosyaya işaret ediyor.

---

## Canlı Metrikler ve JupyterLab

- **Live Metrics** — GPU, bellek ve CPU kullanımının canlı panosu. Uzak bir eğitim çalışmasının gerçekten donanıma ulaştığını doğrulamanın en hızlı yolu.
- **JupyterLab** — Ryzen AI Halo'ya SSH ile bağlı, not defteri hücrelerini ve kabuk komutlarını kullanıcı arayüzünden ayrılmadan karıştırmak için kendi entegre terminaline sahip tam bir not defteri projesi.

---

## Ayarlar ve Birden Fazla Cihaz

**Settings** menüsünde üç sekme bulunur:

| Sekme | Kapsadığı alan |
|-----|----------------|
| **Devices** | Başarıyla bağlandığınız her Ryzen AI Halo'yu listeler. Yeniden bağlanın, kimlik bilgilerini düzenleyin veya yeni bir cihaz ekleyin. |
| **Information** | Belgelere ve forum desteğine bağlantılar. |
| **Customize** | Uygulamayı masaüstünüzde yeniden konumlandırın, terminal türünü değiştirin (yalnızca Windows) ve AMD Sync güncellemelerini kontrol edin. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Terminal türü (Windows)** — **PowerShell** (varsayılan) ve **Windows Command Prompt** arasında seçim yapın.
- **Terminal türü (Linux)** — Yalnızca varsayılan sistem terminali kullanılabilir.
- **Uygulama güncellemeleri** — Bu sekme, kullanıcı arayüzü içinden yeni AMD Sync sürümlerini kontrol etmek ve yüklemek için doğru yerdir; ayrı bir güncelleyiciye gerek yoktur.

> Bir cihaz, **Devices** altında yalnızca ilk başarılı bağlantının ardından görünür; bu nedenle başarısız girişimler listeyi karıştırmaz.

---

## Sorun Giderme

- **Bağlantı hemen başarısız oluyor** — Developer Center'daki Ryzen AI Halo'nun **Remote** sekmesinde SSH sunucusunun etkin olduğunu doğrulayın.
- **Yanlış parola hatası** — Developer Center'dan alınan parolaları değil, Ryzen AI Halo'daki **işletim sistemi oturum açma parolanızı** kullanın.
- **VS Code düğmesi hiçbir şey yapmıyor** — [code.visualstudio.com](https://code.visualstudio.com) adresinden istemci makinenize VS Code'u yükleyin.
- **AMD Sync tepsi simgesi eksik (Linux/GNOME)** — AppIndicator uzantısını yükleyin ve etkinleştirin.
- **`.deb` dosya yöneticisinden açılmıyor** — Terminalden `sudo apt install ./AMDSyncInstaller.deb` komutunu kullanın.

---