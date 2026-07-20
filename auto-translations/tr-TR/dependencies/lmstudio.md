<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
LM Studio, **AMD Ryzen™ AI Developer Center** üzerinden yüklenebilir. **Updates** sekmesine gidin ve LM Studio yüklü değilse yükleyin.

LM Studio'nun önceden yüklenmiş modelleri görebilmesi için Settings > General > Models Directory kısmına gidin. Ardından yolu `C:\Users\Public\models` olarak değiştirin

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. Yükleyiciyi buradan indirin: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. Yükleyin. 
<!-- @device:end -->

> İpucu: Yükledikten sonra, CLI'yi (`lms`) başlatmak için LM Studio'yu bir kez çalıştırın.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> Not: .deb veya AppImage'den birini yüklemeyi seçebilirsiniz. 
1. AppImage'i buradan indirin: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. `sudo apt install libfuse2` komutunu çalıştırın  
3. `cd ~/Downloads` komutunu çalıştırın  
4. `chmod +x LM-Studio-*.AppImage` komutunu çalıştırın  
5. `./LM-Studio-*.AppImage` komutunu çalıştırın  
> İpucu: Yükledikten sonra, CLI'yi (`lms`) başlatmak için LM Studio'yu bir kez çalıştırın.

<!-- @device:halo_box -->
LM Studio'nun önceden yüklenmiş modelleri görebilmesi için Settings > General > Models Directory kısmına gidin. Ardından yolu `/var/cache/models` olarak değiştirin.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->