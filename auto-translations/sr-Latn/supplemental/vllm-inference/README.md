<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može prikazati. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->


## Pregled

vLLM je visokoučinski engine za inferencu dizajniran za velike jezičke modele (LLM). Pruža optimizovano posluživanje sa kontinuiranim grupiranjem za visok propusni opseg i OpenAI-kompatibilan API za besprekorno integrisanje aplikacija. Zbog toga je vLLM odličan za produkcijska okruženja gde su brzina i efikasnost resursa od ključnog značaja.

Ovaj priručnik vas uči kako da poslužujete LLM-ove koristeći kontejnerizovani vLLM na integrisanom GPU-u i kako da komunicirate sa modelima putem OpenAI Python API-ja.

## Šta ćete naučiti

- Kako da podesite i pokrenete vLLM server sa AMD ROCm™ podrškom
- Kako da komunicirate sa modelima putem OpenAI-kompatibilnih API krajnjih tačaka
- Kako da šaljete upite lokalnom serveru pomoću `vllm-prompt`

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite da li postoje ažuriranja softvera

> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem AMD Ryzen™ AI Developer Center-a.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

Ovaj priručnik koristi unapred izgrađenu sliku kontejnera koja uključuje vLLM, ROCm podršku i pomoćne skripte potrebne za pokretanje servera. Ne morate ručno instalirati PyTorch, vLLM niti lokalne skripte priručnika.

Ne postoji korak instalacije vLLM-a na strani hosta. Pokrenite vLLM sa:

```bash
vllm-launch
```

Pokretač pokreće kontejner, cilja integrisani GPU i izlaže lokalni OpenAI-kompatibilan vLLM server. Alternativno, kliknite na ikonu vLLM u traci zadataka.

## Brzi početak

### 1. Potvrdite da vLLM server radi

`vllm-launch` može potrajati nekoliko minuta da inicijalizuje sve. Kada se pokrene, server je dostupan na `http://localhost:8001`. Ostavite terminal za pokretanje otvoren jer server radi u prvom planu, a zatim otvorite poseban terminal za preostale korake. Primeri ispod koriste `Qwen/Qwen3-1.7B`; ako je vaš pokretač konfigurisan za drugi model, zamenite taj ID modela u zahtevima.

### 2. Pošaljite upit

Koristite priloženu skriptu `vllm-prompt` da pošaljete zahtev lokalnom vLLM OpenAI-kompatibilnom serveru:

```bash
vllm-prompt "Tell me a story"
```

### 3. Razgovarajte sa modelom koristeći OpenAI Python API

Pošto vLLM izlaže OpenAI-kompatibilan API, možete koristiti Python paket `openai` za komunikaciju sa njim.

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

Kreirajte `OpenAI` klijent koji pokazuje na lokalni vLLM server umesto na OpenAI-jeve servere. `api_key` je obavezan za klijenta, ali vLLM ga ne validira, pa bilo koji string funkcioniše:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Zatim pošaljite zahtev za dovršavanje razgovora. Ovo koristi isti format poruka kao OpenAI API — listu poruka sa ulogama poput `"user"` i `"assistant"`. Postavljanje `stream=True` znači da će odgovor stizati postepeno umesto odjednom:

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

Na kraju, iterirajte kroz strimovane delove i štampajte svaki deo teksta kako stiže:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložena skripta [chat_with_model.py](assets/chat_with_model.py) sadrži ceo primer i može se preuzeti.


## Rešavanje problema

### Veza odbijena

Proverite da li server radi:
```bash
curl http://localhost:8001/health
```

## Rezime

U ovom priručniku ste naučili kako da:

- Pokrenete kontejnerizovani vLLM sa ROCm podrškom na integrisanom GPU-u
- Pokrenete vLLM server sa OpenAI-kompatibilnim API krajnjim tačkama na portu 8001
- Šaljete upite pomoću `vllm-prompt`
- Upućujete API pozive vLLM serveru koristeći i strimovane i nestrimovane zahteve
- Rešavate uobičajene probleme sa pokretanjem servera, memorijom i klijentskim vezama

Sada imate kontejnerizovano vLLM okruženje za posluživanje velikih jezičkih modela sa optimizovanim performansama na integrisanom GPU-u.

## Sledeći koraci

- **Isprobajte različite modele** — Zamenite model u konfiguraciji `vllm-launch` da eksperimentišete sa različitim LLM-ovima i uporedite performanse.
- **Izgradite aplikaciju** — Koristite OpenAI-kompatibilan API da integišete vLLM u Python aplikaciju, četbota ili tok automatizacije.
- **Fino podešavanje i posluživanje** — Fino podesite model koristeći LoRA ili QLoRA, a zatim ga postavite sa vLLM-om za optimizovanu inferencu.

## Dodatni resursi

- **[Zvanična dokumentacija vLLM](https://docs.vllm.ai/)** — Sveobuhvatni vodiči i API reference
- **[vLLM GitHub repozitorijum](https://github.com/vllm-project/vllm)** — Izvorni kod, problemi i diskusije zajednice