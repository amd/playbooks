<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma

Questo documento descrive la configurazione della piattaforma prevista per l'esecuzione di questo playbook.

## App/Framework richiesti

### Windows/Linux
Lemonade dovrebbe essere preinstallato da [qui](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (app web frontend)
- **Lemonade Server** (server di modelli backend)

> Questo playbook esegue **Lemonade** (server/app Lemonade) in modo **nativo**. **Open WebUI** viene eseguito come **container** su Linux (tramite Podman) e come **pacchetto Python** su Windows. Il pacchetto PyPI `open-webui` supporta solo Python ≤ 3.12, quindi il container Linux evita di dover gestire versioni precedenti di Python.  

## Modelli (in Lemonade)

I modelli devono essere scaricati all'interno dell'**app Lemonade** (utilizzando il Model Manager integrato) oppure tramite i comandi di gestione dei modelli di Lemonade (`lemonade pull <model_name>`). Questo playbook presuppone che i modelli consigliati di seguito siano scaricati e compaiano nell'endpoint dell'elenco dei modelli.

Verifica la disponibilità dei modelli:
- Apri: `http://localhost:13305/api/v1/models`
- I modelli scaricati saranno elencati sotto `"data"`.

### Modelli consigliati

| Capacità | ID modello | Note |
|---|----|-----|
| LLM (Testo in ingresso → Testo in uscita) | `Qwen3-4B-Hybrid` (o simile) | Qualsiasi modello LLM di Lemonade per chat, completamento testo, coding o ragionamento |
| VLM (Immagine → Testo) | `Qwen3.5-4B-GGUF` (o qualsiasi modello della categoria **Vision**) | Qualsiasi modello multimodale/con capacità di visione in grado di accettare immagini come parte del proprio input |
| Generazione di immagini (Testo → Immagine) | `SDXL-Turbo` (o qualsiasi modello della categoria **Image**) | Qualsiasi modello Stable Diffusion che genera immagini per un prompt testuale |
| Audio (Voce → Testo) | `Whisper-Large-v3` (o qualsiasi modello della categoria **Audio**) | Qualsiasi modello ASR che converte l'audio in testo |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Porte utilizzate

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Se queste porte sono già in uso sul tuo sistema, modificale all'avvio del server/dei server.