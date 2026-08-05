<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Pregled

vLLM je visoko zmogljiv izvedbeni pogon za sklepanje, zasnovan za velike jezikovne modele (LLM). Zagotavlja optimizirano strežbo z neprekinjenim paketnim procesiranjem za visoko prepustnost in API, združljiv z OpenAI, za nemoteno integracijo aplikacij. Zaradi tega je vLLM odličen za produkcijske namestitve, kjer sta hitrost in učinkovita raba virov ključnega pomena.

Ta vodnik vas nauči, kako strežete LLM-je z uporabo kontejneriziranega vLLM na vgrajenem GPU-ju in kako komunicirati z modeli prek OpenAI Python API-ja.

## Kaj se boste naučili

- Kako nastaviti in zagnati strežnik vLLM s podporo AMD ROCm™
- Kako komunicirati z modeli prek končnih točk API-ja, združljivega z OpenAI
- Kako pošiljati pozive lokalnemu strežniku z ukazom `vllm-prompt`

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev potrebne programske opreme

vLLM deluje v vnaprej pripravljenem kontejnerju z ROCm in njegovimi odvisnostmi, ki so že vnaprej usklajene. Dodatna namestitev ni potrebna.

Na strani gostitelja ni koraka za namestitev vLLM. Zaženite vLLM z:

```bash
vllm-launch
```

Zaganjalnik zažene kontejner, cilja na vgrajen GPU in izpostavi lokalni strežnik vLLM, združljiv z OpenAI. Druga možnost je klik na ikono vLLM v opravilni vrstici.

## Hitri začetek

### 1. Potrdite, da strežnik vLLM deluje

Ukaz `vllm-launch` lahko za inicializacijo vsega potrebuje nekaj minut. Ko se zažene, je strežnik na voljo na naslovu `http://localhost:8001`. Terminal za zagon pustite odprt, ker strežnik teče v ospredju, nato pa za preostale korake odprite ločen terminal. Spodnji primeri uporabljajo `Qwen/Qwen3-1.7B`; če je vaš zaganjalnik konfiguriran za drug model, v zahtevah zamenjajte ustrezni ID modela.

### 2. Pošljite poziv

Uporabite priloženi skript `vllm-prompt`, da pošljete zahtevo lokalnemu strežniku vLLM, združljivemu z OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Klepetajte z modelom z uporabo OpenAI Python API-ja

Ker vLLM izpostavlja API, združljiv z OpenAI, lahko za komunikacijo z njim uporabite Python paket `openai`.

Najprej ustvarite virtualno okolje Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Namestite paket OpenAI
```bash
pip install openai
```

Ustvarite odjemalca `OpenAI`, ki kaže na lokalni strežnik vLLM namesto na strežnike OpenAI. Odjemalec zahteva `api_key`, vendar ga vLLM ne preverja, zato deluje kateri koli niz:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Nato pošljite zahtevo za dokončanje klepeta. Uporablja se enak format sporočil kot pri API-ju OpenAI — seznam sporočil z vlogami, kot sta `"user"` in `"assistant"`. Nastavitev `stream=True` pomeni, da bo odgovor prispel postopoma in ne vse naenkrat:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Nazadnje ponovite prek pretočenih delov in izpišite vsak del besedila, ko prispe:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priloženi skript [chat_with_model.py](assets/chat_with_model.py) vsebuje celoten primer in ga je mogoče prenesti.


## Izbira in konfiguracija modela

Privzeto `vllm-launch` streže `Qwen/Qwen3-1.7B` kot testni model na vratih `8001`. Model, vrata in parametre strežbe vLLM lahko spremenite brez ponovne izgradnje ali urejanja kontejnerja.

### Modeli, ki jih je testiral AMD

Naslednji modeli so vnaprej konfigurirani in jih je potrdil AMD:

| Model | Opombe |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Privzeti model. Lahek in hiter za nalaganje. |
| `openai/gpt-oss-20b` | Večji model za odgovore višje kakovosti. |

### Zagon drugega modela

Podajte ID modela z `--model` (ali `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Sprememba vrat

Podajte vrata nad 1024 z `--port` (ali `-p`); privzeta vrednost je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Če spremenite vrata, usmerite `base_url` odjemalca na ista vrata (na primer `http://localhost:8080/v1`).

### Posredovanje dodatnih parametrov vLLM

Vsi dodatni argumenti se posredujejo neposredno vLLM, tako da lahko prilagodite vedenje strežbe, na primer dolžino konteksta ali podatkovni tip. Obstajata dva načina za njihovo podajanje.

**Vgrajeno**, za možnostmi zaganjalnika:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trajno**, v konfiguracijski datoteki na `~/.local/share/vLLM/vllm-launch.conf`. Ta datoteka privzeto ne obstaja — ustvarite jo in dodajte svoje argumente kot Bash tabelo:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Uporabite `+=`, da dodate k privzetim argumentom, namesto da jih zamenjate:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Za prikaz vseh možnosti zaganjalnika kadar koli zaženite:

```bash
vllm-launch --help
```

### Kje so shranjeni modeli

`vllm-launch` išče modele na dveh lokacijah:

| Lokacija | Pot |
|----------|------|
| Sistemski modeli | `/var/cache/models` |
| Uporabniški modeli | `~/.local/share/vLLM/models` |

Prenesen model lahko postavite v katero koli od teh map in ga zaženete tako, da podate njegovo pot ali ID v `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Opomba**: Pričakuje se, da bo zagon vašega lastnega prenesenega modela na ta način deloval, ko je model postavljen v eno od zgornjih map, vendar AMD tega poteka dela še ni uradno potrdil.

## Odpravljanje težav

### Povezava zavrnjena

Prepričajte se, da strežnik deluje:
```bash
curl http://localhost:8001/health
```

## Povzetek

V tem vodniku ste se naučili, kako:

- zagnati kontejnerizirani vLLM s podporo ROCm na vgrajenem GPU-ju,
- zagnati strežnik vLLM s končnimi točkami API-ja, združljivimi z OpenAI, na vratih 8001,
- pošiljati pozive z ukazom `vllm-prompt`,
- izvajati klice API-ja strežniku vLLM z uporabo pretočnih in nepretočnih zahtev,
- odpravljati pogoste težave pri zagonu strežnika, pomnilniku in povezavah odjemalcev.

Zdaj imate kontejnerizirano namestitev vLLM za strežbo velikih jezikovnih modelov z optimizirano zmogljivostjo na vgrajenem GPU-ju.

## Naslednji koraki

- **Preizkusite različne modele** — uporabite `vllm-launch --model <model>`, da eksperimentirate z različnimi LLM-ji in primerjate zmogljivost (glejte [Izbira in konfiguracija modela](#choosing-and-configuring-a-model)).
- **Zgradite aplikacijo** — uporabite API, združljiv z OpenAI, za integracijo vLLM v Python aplikacijo, klepetalnega robota ali avtomatizirani potek dela.
- **Fino prilagodite in strezite** — fino prilagodite model z uporabo LoRA ali QLoRA, nato pa ga uvedite z vLLM za optimizirano sklepanje.
## Dodatni viri

- **[Uradna dokumentacija za vLLM](https://docs.vllm.ai/)** — Obsežni vodniki in referenčne informacije za API
- **[Repozitorij vLLM na GitHubu](https://github.com/vllm-project/vllm)** — Izvorna koda, težave in razprave skupnosti