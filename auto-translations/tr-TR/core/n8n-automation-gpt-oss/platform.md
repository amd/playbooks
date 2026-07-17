<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Yapılandırması

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Ön Koşullar

### Windows

| Bileşen | Sürüm | Notlar |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Geliştirici Platformu'nda önceden yüklenmiş ve PATH'te mevcut; diğer tüm cihazlarda manuel olarak yüklenmelidir |
| **Lemonade Server** | en son | `http://localhost:13305/api/v1` adresinde çalışıyor |

### Linux

| Bileşen | Sürüm | Notlar |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Geliştirici Platformu'nda önceden yüklenmiş ve PATH'te mevcut; diğer tüm cihazlarda manuel olarak yüklenmelidir |
| **Lemonade Server** | en son | `http://localhost:13305/api/v1` adresinde çalışıyor |


## Lemonade LLM

Lemonade sunucusu, cihaza uygun model yüklenmiş şekilde çalışıyor olmalıdır (cihazınız için `lemonade run` komutu hakkında README'ye bakın):

| Cihaz | Uç Nokta | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Geliştirici Platformu <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Serisi Grafik <br> AMD Radeon™ 9000 Serisi Grafik | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |