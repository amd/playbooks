<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Configurarea platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Aplicații/Framework-uri necesare

### Windows/Linux

- **Lemonade Server** trebuie instalat urmând
  [ghidul de instalare Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 sau o versiune ulterioară** și `npm`, utilizate de CLI-ul `agent-canvas`.
- **uv**, managerul de pachete Python pe care Agent Canvas îl folosește pentru a gestiona
  mediul serverului agentului. Instalați-l din
  [ghidul de instalare uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modele necesare

### Windows/Linux

Următorul model trebuie să fie disponibil pentru Lemonade Server înainte de a începe
playbook-ul.

| Tip model | ID model | Note |
| --- | --- | --- |
| Model de chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servit de Lemonade Server la `http://127.0.0.1:13305/api/v1`. Utilizați un model GGUF mai mic pe dispozitivele cu mai puțin de 32 GB memorie. |

Porniți modelul cu:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
