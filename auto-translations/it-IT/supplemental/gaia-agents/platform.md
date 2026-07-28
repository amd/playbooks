<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da un traduttore umano. Potrebbe contenere errori e alcuni passaggi, comandi, download o la disponibilità dei prodotti potrebbero variare in base alla lingua o alla regione. Se qualcosa non sembra corretto, fare riferimento al playbook originale in inglese come fonte autorevole.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## App/Framework richiesti

### Windows/Linux

GAIA dovrebbe essere pre-installato seguendo le istruzioni fornite nella [Guida all'installazione di GAIA](../../dependencies/gaia.md).

Lemonade Server dovrebbe essere pre-installato seguendo le istruzioni fornite nella [Guida all'installazione di Lemonade](../../dependencies/lemonade.md).

## Modelli richiesti

### Windows/Linux

L'Hardware Advisor Agent utilizza **Qwen3-Coder-30B** per il ragionamento dell'agente. Questo modello viene scaricato automaticamente durante `gaia init`. Non è richiesto alcun download manuale dei modelli.