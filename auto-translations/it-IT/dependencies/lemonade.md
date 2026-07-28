<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installazione di Lemonade

<!-- @os:windows -->
Scarica il programma di installazione più recente da [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) ed esegui il file `.msi`.

Dopo l'installazione:
- La CLI `lemonade` viene aggiunta automaticamente al PATH di sistema
- Il server Lemonade è previsto in esecuzione automatica in background

Puoi anche installare in modalità silenziosa dalla riga di comando:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

Per altre distribuzioni o per installare dal sorgente, consulta le [opzioni di installazione complete](https://lemonade-server.ai/docs/guide/install/).
<!-- @os:end -->


#### Verifica dell'installazione di Lemonade

Apri un terminale ed esegui:
```bash
lemonade --version
```

Dovresti vedere un output simile a:
```
lemonade version x.y.z
```

Se viene visualizzato un numero di versione, Lemonade è installato correttamente ed è pronto all'uso.

Per riferimento rapido, ecco i comandi CLI di Lemonade più comuni:

| Comando | Cosa fa |
| --- | --- |
| `lemonade --help` | Mostra tutti i comandi e i flag disponibili. |
| `lemonade --version` | Stampa la versione di Lemonade installata. |
| `lemonade status` | Conferma se il server Lemonade è in esecuzione e raggiungibile. L'URL base predefinito dell'API compatibile con OpenAI è `http://localhost:13305/api/v1`. |
| `lemonade list` | Elenca i modelli disponibili per la tua configurazione di Lemonade. |
| `lemonade pull <MODEL_NAME>` | Scarica un modello senza avviarlo. |
| `lemonade run <MODEL_NAME>` | Scarica il modello se necessario, quindi lo avvia per l'inferenza/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Avvia un modello llama.cpp con il backend ROCm. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Avvia un modello llama.cpp con il backend Vulkan. |
| `lemonade config` | Mostra i valori di configurazione attuali di Lemonade. |
| `lemonade config set llamacpp.backend=rocm` | Imposta il backend llama.cpp predefinito su ROCm. |

Per le opzioni più recenti del server Lemonade o per la risoluzione dei problemi, consulta la [documentazione ufficiale di Lemonade](https://lemonade-server.ai/docs/lemonade-cli/).