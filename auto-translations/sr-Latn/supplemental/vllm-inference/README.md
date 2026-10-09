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

vLLM je visokoperformansni inferencijski mehanizam dizajniran za velike jezičke modele (LLM-ove). Pruža optimizovano posluživanje sa kontinuiranim grupisanjem (continuous batching) radi visoke propusnosti, kao i API kompatibilan sa OpenAI za jednostavnu integraciju aplikacija. Ovo čini vLLM odličnim izborom za produkciona okruženja gde su brzina i efikasnost resursa od ključnog značaja.

Ovaj vodič vas uči kako da poslužujete LLM-ove koristeći kontejnerizovani vLLM na integrisanom GPU-u i kako da komunicirate sa modelima putem OpenAI Python API-ja.

## Šta ćete naučiti

- Kako da podesite i pokrenete vLLM server sa podrškom za AMD ROCm™
- Kako da komunicirate sa modelima putem OpenAI-kompatibilnih API krajnjih tačaka
- Kako da šaljete upite lokalnom serveru pomoću `vllm-prompt`

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite ima li ažuriranja softvera

> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje softverskih preduslova

vLLM se izvršava u unapred izgrađenom kontejneru sa ROCm-om i njegovim zavisnostima već usklađenim. Nije potrebna nikakva dodatna instalacija.

Ne postoji korak instalacije vLLM-a na host strani. Pokrenite vLLM sa:

```bash
vllm-launch
```

Pokretač pokreće kontejner, ciljajući integrisani GPU, i izlaže lokalni OpenAI-kompatibilni vLLM server. Alternativno, kliknite na ikonu vLLM-a na traci zadataka.

## Brzi start

### 1. Potvrdite da vLLM server radi

`vllm-launch`-u može trebati nekoliko minuta da inicijalizuje sve. Kada se pokrene, server je dostupan na `http://localhost:8001`. Ostavite terminal za pokretanje otvorenim jer server radi u prvom planu, a zatim otvorite poseban terminal za preostale korake. Primeri ispod koriste `Qwen/Qwen3-1.7B`; ako je vaš pokretač podešen za drugi model, zamenite tim ID-jem modela u zahtevima.

### 2. Pošaljite upit

Koristite priloženu skriptu `vllm-prompt` da pošaljete zahtev lokalnom OpenAI-kompatibilnom vLLM serveru:

```bash
vllm-prompt "Tell me a story"
```

### 3. Ćaskajte sa modelom koristeći OpenAI Python API

Pošto vLLM izlaže OpenAI-kompatibilan API, možete koristiti Python paket `openai` da komunicirate sa njim.

Prvo, napravite Python virtuelno okruženje:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Instalirajte OpenAI paket
```bash
pip install openai
```

Napravite `OpenAI` klijenta usmerenog na lokalni vLLM server umesto na OpenAI-jeve servere. `api_key` je obavezan za klijenta, ali ga vLLM ne validira, tako da bilo koji niz radi:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Zatim pošaljite zahtev za dovršavanje ćaskanja (chat completion). Ovo koristi isti format poruka kao OpenAI API — listu poruka sa ulogama kao što su `"user"` i `"assistant"`. Postavljanje `stream=True` znači da će odgovor stizati postepeno umesto odjednom:

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

Na kraju, iterirajte kroz strimovane delove i ispišite svaki deo teksta čim stigne:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložena skripta [chat_with_model.py](assets/chat_with_model.py) sadrži ceo primer i može se preuzeti.


## Izbor i konfiguracija modela

Podrazumevano, `vllm-launch` poslužuje `Qwen/Qwen3-1.7B` kao testni model na portu `8001`. Možete promeniti model, port i parametre vLLM posluživanja bez ponovnog izgrađivanja ili izmene kontejnera.

### Modeli testirani od strane AMD-a

Sledeći modeli su unapred podešeni i validirani od strane AMD-a:

| Model | Napomene |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Podrazumevani model. Lagan i brz za učitavanje. |
| `openai/gpt-oss-20b` | Veći model za odgovore više kvaliteta. |

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

Svi dodatni argumenti se direktno prosleđuju vLLM-u, tako da možete podešavati ponašanje posluživanja, kao što su dužina konteksta ili tip podataka. Postoje dva načina za njihovo zadavanje.

**Unutar komandne linije**, nakon opcija pokretača:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trajno**, u konfiguracionom fajlu na `~/.local/share/vLLM/vllm-launch.conf`. Ovaj fajl ne postoji podrazumevano — napravite ga i dodajte svoje argumente kao Bash niz:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Koristite `+=` da dodate argumente na podrazumevane umesto da ih zamenite:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Da biste u bilo kom trenutku videli sve opcije pokretača, pokrenite:

```bash
vllm-launch --help
```

### Gde se čuvaju modeli

`vllm-launch` traži modele na dve lokacije:

| Lokacija | Putanja |
|----------|------|
| Sistemski modeli | `/var/cache/models` |
| Korisnički modeli | `~/.local/share/vLLM/models` |

Možete smestiti preuzeti model u bilo koji od ovih direktorijuma i pokrenuti ga prosleđivanjem njegove putanje ili ID-ja pomoću `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Napomena**: Pokretanje sopstvenog preuzetog modela na ovaj način se očekuje da radi čim se model smesti u jedan od navedenih direktorijuma, ali ovaj tok rada još uvek nije zvanično validiran od strane AMD-a.

## Rešavanje problema

### Veza odbijena (connection refused)

Proverite da li server radi:
```bash
curl http://localhost:8001/health
```

## Rezime

U ovom vodiču naučili ste kako da:

- Pokrenete kontejnerizovani vLLM sa podrškom za ROCm na integrisanom GPU-u
- Pokrenete vLLM server sa OpenAI-kompatibilnim API krajnjim tačkama na portu 8001
- Šaljete upite pomoću `vllm-prompt`
- Pravite API pozive ka vLLM serveru koristeći i strimovane i nestrimovane zahteve
- Rešavate uobičajene probleme sa pokretanjem servera, memorijom i vezama klijenta

Sada imate kontejnerizovano vLLM okruženje za posluživanje velikih jezičkih modela sa optimizovanim performansama na integrisanom GPU-u.

## Sledeći koraci

- **Isprobajte različite modele** — Koristite `vllm-launch --model <model>` da eksperimentišete sa različitim LLM-ovima i uporedite performanse (pogledajte [Izbor i konfiguracija modela](#choosing-and-configuring-a-model)).
- **Napravite aplikaciju** — Koristite OpenAI-kompatibilan API da integrišete vLLM u Python aplikaciju, chatbot ili automatizovani tok rada.
- **Fino podesite i poslužujte** — Fino podesite model koristeći LoRA ili QLoRA, zatim ga raspodelite pomoću vLLM-a za optimizovanu inferenciju.
## Dodatni resursi

- **[Zvanična dokumentacija za vLLM](https://docs.vllm.ai/)** — Sveobuhvatni vodiči i reference za API
- **[vLLM GitHub repozitorijum](https://github.com/vllm-project/vllm)** — Izvorni kod, prijave problema i diskusije zajednice