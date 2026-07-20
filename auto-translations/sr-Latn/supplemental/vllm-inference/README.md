<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može da prikaže. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->


## Pregled

vLLM je visokoperformansni mehanizam za zaključivanje dizajniran za velike jezičke modele (LLM). Pruža optimizovano posluživanje sa kontinuiranim grupisanjem (batching) za visoku propusnost i API kompatibilan sa OpenAI za jednostavnu integraciju aplikacija. Ovo čini vLLM odličnim izborom za produkciona okruženja gde su brzina i efikasnost resursa ključni.

Ovaj priručnik vas uči kako da poslužujete LLM-ove pomoću kontejnerizovanog vLLM-a na integrisanom GPU-u i kako da komunicirate sa modelima preko OpenAI Python API-ja.

## Šta ćete naučiti

- Kako da podesite i pokrenete vLLM server sa podrškom za AMD ROCm™
- Kako da komunicirate sa modelima preko API krajnjih tačaka kompatibilnih sa OpenAI
- Kako da šaljete upite lokalnom serveru pomoću `vllm-prompt`

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite ažuriranja softvera

> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati pomoću AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje softverskih preduslova

Ovaj priručnik koristi unapred izgrađenu (prebuilt) sliku kontejnera koja uključuje vLLM, ROCm podršku i pomoćne skripte potrebne za pokretanje servera. Nije potrebno ručno instalirati PyTorch, vLLM, niti lokalne skripte priručnika.

Ne postoji korak instalacije vLLM-a na hostu. Pokrenite vLLM pomoću:

```bash
vllm-launch
```

Pokretač (launcher) pokreće kontejner, ciljano koristi integrisani GPU i izlaže lokalni vLLM server kompatibilan sa OpenAI. Alternativno, kliknite na vLLM ikonu na traci zadataka.

## Brzi početak

### 1. Potvrdite da vLLM server radi

Skripti `vllm-launch` može biti potrebno nekoliko minuta da inicijalizuje sve. Kada se pokrene, server je dostupan na `http://localhost:8001`. Ostavite otvoren terminal za pokretanje jer server radi u prvom planu, a zatim otvorite poseban terminal za preostale korake. Primeri ispod koriste `Qwen/Qwen3-1.7B`; ako je vaš pokretač konfigurisan za drugi model, zamenite tim identifikatorom modela u zahtevima.

### 2. Pošaljite upit

Koristite priloženu skriptu `vllm-prompt` da pošaljete zahtev lokalnom vLLM serveru kompatibilnom sa OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Ćaskajte sa modelom pomoću OpenAI Python API-ja

Pošto vLLM izlaže API kompatibilan sa OpenAI, možete koristiti Python paket `openai` za komunikaciju sa njim.

Prvo, kreirajte virtuelno Python okruženje:

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

Kreirajte `OpenAI` klijenta usmerenog na lokalni vLLM server umesto na OpenAI servere. `api_key` je obavezan za klijenta, ali vLLM ga ne validira, pa bilo koji niz karaktera funkcioniše:

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

Na kraju, prođite kroz strimovane delove i ispišite svaki komad teksta kako stiže:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložena skripta [chat_with_model.py](assets/chat_with_model.py) sadrži ceo primer i može se preuzeti.


## Rešavanje problema

### Konekcija odbijena

Proverite da li server radi:
```bash
curl http://localhost:8001/health
```

## Rezime

U ovom priručniku naučili ste kako da:

- Pokrenete kontejnerizovani vLLM sa ROCm podrškom na integrisanom GPU-u
- Pokrenete vLLM server sa API krajnjim tačkama kompatibilnim sa OpenAI na portu 8001
- Šaljete upite pomoću `vllm-prompt`
- Upućujete API pozive vLLM serveru koristeći i strimovane i nestrimovane zahteve
- Rešavate uobičajene probleme pri pokretanju servera, memoriji i konekcijama klijenta

Sada imate kontejnerizovano vLLM okruženje za posluživanje velikih jezičkih modela sa optimizovanim performansama na integrisanom GPU-u.

## Sledeći koraci

- **Isprobajte različite modele** — Zamenite model u konfiguraciji `vllm-launch` da biste eksperimentisali sa različitim LLM-ovima i uporedili performanse.
- **Napravite aplikaciju** — Koristite API kompatibilan sa OpenAI da integrišete vLLM u Python aplikaciju, chatbot ili automatizovani radni tok.
- **Fino podesite i poslužujte** — Fino podesite model koristeći LoRA ili QLoRA, a zatim ga primenite pomoću vLLM-a za optimizovano zaključivanje.

## Dodatni resursi

- **[Zvanična dokumentacija za vLLM](https://docs.vllm.ai/)** — Sveobuhvatni vodiči i reference za API
- **[vLLM GitHub repozitorijum](https://github.com/vllm-project/vllm)** — Izvorni kod, problemi (issues) i diskusije zajednice