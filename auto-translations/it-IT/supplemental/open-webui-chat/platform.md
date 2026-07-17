<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive la configurazione della piattaforma prevista per l'esecuzione di questo playbook.

## App/Framework Richiesti

### Windows/Linux
Lemonade deve essere pre-installato da [qui](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (app web frontend)
- **Lemonade Server** (server backend per i modelli)

> Questo playbook esegue **Lemonade** (server/app Lemonade) **nativamente**. **Open WebUI** viene eseguito come **container** su Linux (tramite Podman) e come **pacchetto Python** su Windows. Il pacchetto PyPI `open-webui` supporta solo Python ≤ 3.12, quindi il container Linux evita la necessità di gestire versioni Python più vecchie.

## Modelli (in Lemonade)

I modelli devono essere scaricati all'interno dell'**app Lemonade** (utilizzando il Model Manager integrato) o tramite i comandi di gestione dei modelli di Lemonade (`lemonade pull <model_name>`). Questo playbook presuppone che i modelli consigliati di seguito siano stati scaricati e vengano visualizzati nell'endpoint dell'elenco dei modelli.

Verifica la disponibilità dei modelli:
- Apri: `http://localhost:13305/api/v1/models`
- I modelli scaricati saranno elencati sotto `"data"`.

### Modelli consigliati

| Capacità | ID Modello | Note |
|---|----|-----|
| LLM (Input testo → Output testo) | `Qwen3-4B-Hybrid` (o simile) | Qualsiasi modello LLM di Lemonade per chat, completamento testo, programmazione o ragionamento |
| VLM (Immagine → Testo) | `Qwen3.5-4B-GGUF` (o qualsiasi modello nella categoria **Vision**) | Qualsiasi modello multimodale/con capacità visiva in grado di accettare immagini come parte del proprio input |
| Generazione di Immagini (Testo → Immagine) | `SDXL-Turbo` (o qualsiasi modello nella categoria **Image**) | Qualsiasi modello Stable Diffusion che genera immagini da un prompt testuale |
| Audio (Parlato → Testo) | `Whisper-Large-v3` (o qualsiasi modello nella categoria **Audio**) | Qualsiasi modello ASR che converte l'audio in testo |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Porte utilizzate

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Se queste porte sono già in uso nel tuo sistema, modificale all'avvio del/dei server.