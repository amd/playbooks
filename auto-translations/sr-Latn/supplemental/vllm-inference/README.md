<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Pregled

vLLM je visokoperformansni mehanizam za zaključivanje (inference) namenjen velikim jezičkim modelima (LLM). Pruža optimizovano posluživanje sa kontinuiranim grupisanjem (batching) radi visoke propusnosti i API kompatibilan sa OpenAI za jednostavnu integraciju aplikacija. Zbog toga je vLLM odličan izbor za produkcione implementacije gde su brzina i efikasnost resursa ključni.

Ovaj vodič vas uči kako da poslužujete LLM modele koristeći kontejnerizovani vLLM na integrisanom GPU-u i kako da komunicirate sa modelima putem OpenAI Python API-ja.

## Šta ćete naučiti

- Kako da podesite i pokrenete vLLM server sa podrškom za AMD ROCm™
- Kako da komunicirate sa modelima putem endpointa kompatibilnih sa OpenAI API-jem
- Kako da šaljete upite lokalnom serveru pomoću `vllm-prompt`

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati pomoću AMD Ryzen™ AI Developer Center-a.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje potrebnog softvera

vLLM se pokreće u unapred izgrađenom kontejneru sa ROCm-om i njegovim zavisnostima koje su već uparene. Nije potrebna nikakva dodatna instalacija.

Ne postoji korak instalacije vLLM-a na host sistemu. Pokrenite vLLM sa:

```bash
vllm-launch
```

Pokretač (launcher) pokreće kontejner, cilja na integrisani GPU i izlaže lokalni vLLM server kompatibilan sa OpenAI API-jem. Alternativno, kliknite na vLLM ikonicu na traci zadataka.

## Brzi početak

### 1. Potvrdite da vLLM server radi

`vllm-launch` može da potraje nekoliko minuta da inicijalizuje sve. Kada se pokrene, server je dostupan na `http://localhost:8001`. Ostavite terminal za pokretanje otvoren jer server radi u prvom planu, a zatim otvorite poseban terminal za preostale korake. Primeri u nastavku koriste `Qwen/Qwen3-1.7B`; ako je vaš pokretač podešen za drugi model, zamenite ID tog modela u zahtevima.

### 2. Pošaljite upit

Koristite priloženu skriptu `vllm-prompt` da pošaljete zahtev lokalnom vLLM serveru kompatibilnom sa OpenAI API-jem:

```bash
vllm-prompt "Tell me a story"
```

### 3. Ćaskajte sa modelom koristeći OpenAI Python API

Pošto vLLM izlaže API kompatibilan sa OpenAI, možete koristiti Python paket `openai` da komunicirate sa njim.

Prvo, kreirajte Python virtuelno okruženje:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Instalirajte OpenAI paket
```bash
pip install openai
```

Kreirajte `OpenAI` klijent usmeren na lokalni vLLM server umesto na OpenAI-jeve servere. `api_key` je obavezan za klijenta, ali ga vLLM ne validira, tako da svaka niska znakova radi:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Zatim, pošaljite zahtev za dovršavanje ćaskanja (chat completion). Ovo koristi isti format poruka kao OpenAI API — listu poruka sa ulogama poput `"user"` i `"assistant"`. Postavljanje `stream=True` znači da će odgovor stizati postepeno, a ne odjednom:

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

Na kraju, prođite kroz strimovane delove i ispišite svaki deo teksta čim stigne:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložena skripta [chat_with_model.py](assets/chat_with_model.py) sadrži ceo primer i može se preuzeti.


## Izbor i konfigurisanje modela

Podrazumevano, `vllm-launch` poslužuje `Qwen/Qwen3-1.7B` kao testni model na portu `8001`. Model, port i parametre vLLM posluživanja možete promeniti bez ponovnog izgrađivanja ili izmene kontejnera.

### Modeli koje je AMD testirao

Sledeći modeli su unapred konfigurisani i validirani od strane AMD-a:

| Model | Napomene |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Podrazumevani model. Lagan i brz za učitavanje. |
| `openai/gpt-oss-20b` | Veći model za kvalitetnije odgovore. |

### Pokretanje drugog modela

Prosledite ID modela pomoću `--model` (ili `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Promena porta

Prosledite port veći od 1024 pomoću `--port` (ili `-p`); podrazumevani je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Ako promenite port, usmerite `base_url` vašeg klijenta na isti port (na primer `http://localhost:8080/v1`).

### Prosleđivanje dodatnih vLLM parametara

Svi dodatni argumenti se prosleđuju direktno vLLM-u, tako da možete podešavati ponašanje posluživanja, poput dužine konteksta ili tipa podataka. Postoje dva načina da ih navedete.

**Direktno u komandnoj liniji**, nakon opcija pokretača:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trajno**, u konfiguracionoj datoteci na `~/.local/share/vLLM/vllm-launch.conf`. Ova datoteka podrazumevano ne postoji — kreirajte je i dodajte svoje argumente kao Bash niz:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Koristite `+=` da dodate na podrazumevane argumente umesto da ih zamenite:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Da biste u bilo kom trenutku videli sve opcije pokretača, pokrenite:

```bash
vllm-launch --help
```

### Gde se modeli čuvaju

`vllm-launch` traži modele na dve lokacije:

| Lokacija | Putanja |
|----------|------|
| Sistemski modeli | `/var/cache/models` |
| Korisnički modeli | `~/.local/share/vLLM/models` |

Preuzeti model možete smestiti u bilo koji od ovih direktorijuma i pokrenuti ga prosleđivanjem njegove putanje ili ID-a parametru `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Napomena**: Očekuje se da će pokretanje sopstvenog preuzetog modela na ovaj način raditi kada se model smesti u jedan od gore navedenih direktorijuma, ali ovaj tok rada AMD još uvek nije zvanično validirao.

## Rešavanje problema

### Veza odbijena (Connection refused)

Proverite da li server radi:
```bash
curl http://localhost:8001/health
```

## Sažetak

U ovom vodiču ste naučili kako da:

- Pokrenete kontejnerizovani vLLM sa podrškom za ROCm na integrisanom GPU-u
- Pokrenete vLLM server sa endpointima kompatibilnim sa OpenAI API-jem na portu 8001
- Šaljete upite pomoću `vllm-prompt`
- Upućujete API pozive vLLM serveru koristeći i strimovane i nestrimovane zahteve
- Rešavate uobičajene probleme sa pokretanjem servera, memorijom i vezama klijenta

Sada imate kontejnerizovanu vLLM implementaciju za posluživanje velikih jezičkih modela sa optimizovanim performansama na integrisanom GPU-u.

## Sledeći koraci

- **Isprobajte različite modele** — Koristite `vllm-launch --model <model>` da eksperimentišete sa različitim LLM modelima i uporedite performanse (pogledajte [Izbor i konfigurisanje modela](#choosing-and-configuring-a-model)).
- **Izgradite aplikaciju** — Koristite API kompatibilan sa OpenAI da integrišete vLLM u Python aplikaciju, chatbot ili tok automatizacije.
- **Fino podesite i poslužujte** — Fino podesite model koristeći LoRA ili QLoRA, a zatim ga implementirajte pomoću vLLM-a za optimizovano zaključivanje.
## Dodatni resursi

- **[Zvanična dokumentacija za vLLM](https://docs.vllm.ai/)** — Sveobuhvatni vodiči i reference za API
- **[GitHub repozitorijum za vLLM](https://github.com/vllm-project/vllm)** — Izvorni kod, problemi i diskusije zajednice