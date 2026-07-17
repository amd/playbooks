<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more prikazati. Za pravilen ogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Pregled

vLLM je visokozmogljiv sklepalni stroj, zasnovan za velike jezikovne modele (LLM). Zagotavlja optimizirano streženje z neprekinjenim paketnim obdelovalanjem za visoko prepustnost ter API, združljiv z OpenAI, za brezhibno integracijo aplikacij. Zaradi tega je vLLM odličen za produkcijske namestitve, kjer sta hitrost in učinkovita raba virov ključnega pomena.

Ta priročnik vas uči, kako strežete LLM z uporabo vsebniško nameščenega vLLM na integriranem GPU ter kako komunicirate z modeli prek OpenAI Python API.

## Kaj se boste naučili

- Kako nastaviti in zagnati strežnik vLLM s podporo AMD ROCm™
- Kako komunicirati z modeli prek končnih točk API, združljivih z OpenAI
- Kako pošiljati pozive lokalnemu strežniku z `vllm-prompt`

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev programske opreme

Ta priročnik uporablja vnaprej zgrajeno sliko vsebnika, ki vključuje vLLM, podporo ROCm in pomožne skripte, potrebne za zagon strežnika. PyTorch, vLLM ali lokalnih skript priročnika vam ni treba ročno nameščati.

Na strani gostitelja ni koraka za namestitev vLLM. Zaženite vLLM z:

```bash
vllm-launch
```

Zaganjalnik zažene vsebnik, cilja na integrirani GPU in izpostavi lokalni strežnik vLLM, združljiv z OpenAI. Lahko pa kliknete ikono vLLM v opravilni vrstici.

## Hiter začetek

### 1. Potrdite, da strežnik vLLM deluje

Inicializacija `vllm-launch` lahko traja nekaj minut. Ko se zažene, je strežnik na voljo na `http://localhost:8001`. Pustite zagonski terminal odprt, ker strežnik deluje v ospredju, nato pa odprite ločen terminal za preostale korake. Spodnji primeri uporabljajo `Qwen/Qwen3-1.7B`; če je vaš zaganjalnik konfiguriran za drug model, v zahtevah nadomestite tisti ID modela.

### 2. Pošljite poziv

Uporabite priloženo skripto `vllm-prompt` za pošiljanje zahteve lokalnemu strežniku vLLM, združljivemu z OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Klepetajte z modelom z uporabo OpenAI Python API

Ker vLLM izpostavlja API, združljiv z OpenAI, lahko za interakcijo z njim uporabite paket Python `openai`.

Najprej ustvarite navidezno okolje Python:

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

Ustvarite odjemalca `OpenAI`, ki kaže na lokalni strežnik vLLM namesto na strežnike OpenAI. `api_key` zahteva odjemalec, vendar ga vLLM ne preverja, zato deluje kateri koli niz:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Nato pošljite zahtevo za dokončanje klepeta. Ta uporablja enako obliko sporočil kot OpenAI API — seznam sporočil z vlogami, kot sta `"user"` in `"assistant"`. Nastavitev `stream=True` pomeni, da bo odgovor prihajal postopoma in ne naenkrat:

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

Na koncu iterirajte po pretočnih delčkih in izpišite vsak kos besedila, ko prispe:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložena skripta [chat_with_model.py](assets/chat_with_model.py) vsebuje celoten primer in jo je mogoče prenesti.


## Odpravljanje težav

### Zavrnjena povezava

Prepričajte se, da strežnik deluje:
```bash
curl http://localhost:8001/health
```

## Povzetek

V tem priročniku ste se naučili, kako:

- Zagnati vsebniški vLLM s podporo ROCm na integriranem GPU
- Zagnati strežnik vLLM s končnimi točkami API, združljivimi z OpenAI, na vratih 8001
- Pošiljati pozive z `vllm-prompt`
- Izvajati klice API na strežnik vLLM z uporabo pretočnih in nepretočnih zahtev
- Odpravljati pogoste težave z zagonom strežnika, pomnilnikom in odjemalskimi povezavami

Zdaj imate vsebniško namestitev vLLM za streženje velikih jezikovnih modelov z optimizirano zmogljivostjo na integriranem GPU.

## Naslednji koraki

- **Preizkusite različne modele** — Zamenjajte model v konfiguraciji `vllm-launch`, da eksperimentirate z različnimi LLM in primerjate zmogljivost.
- **Zgradite aplikacijo** — Uporabite API, združljiv z OpenAI, za integracijo vLLM v aplikacijo Python, klepetalnega robota ali avtomatizacijski potek dela.
- **Fino nastavite in strežite** — Fino nastavite model z uporabo LoRA ali QLoRA, nato ga namestite z vLLM za optimizirano sklepanje.

## Dodatni viri

- **[Uradna dokumentacija vLLM](https://docs.vllm.ai/)** — Obsežni vodniki in reference API
- **[Repozitorij vLLM na GitHub](https://github.com/vllm-project/vllm)** — Izvorna koda, težave in razprave skupnosti