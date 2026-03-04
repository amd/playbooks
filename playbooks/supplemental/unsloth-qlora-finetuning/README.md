## Overview

Unsloth is a high-efficiency LLM fine-tuning framework designed to make advanced model customization accessible on modern hardware.

It streamlines supervised fine-tuning (SFT), parameter-efficient fine-tuning (PEFT), QLoRA, and reinforcement learning approaches such as GRPO—allowing developers to adapt powerful foundation models to domain-specific tasks without large-scale infrastructure.

Rather than relying on costly distributed training clusters, Unsloth enables practical, reproducible fine-tuning workflows that run efficiently on local AI systems like Ryzen™ AI Halo.

## What You'll Learn

- How to set up the Unsloth environment
- How to fine-tune an LLM using QLoRA with Unsloth
- How to fine-tune an LLM using GRPO with Unsloth
- How to use Unsloth to benchmark kernel performance on an iGPU

## Why Unsloth?
Fine-tuning large language models has traditionally required significant compute resources and complex infrastructure. For many developers, adapting a foundation model to a specific domain—such as finance or enterprise applications—can be difficult and costly. Unsloth makes this process practical and accessible.

Unsloth is built to streamline modern LLM fine-tuning workflows, supporting techniques such as Supervised Fine-Tuning (SFT), Parameter-Efficient Fine-Tuning (PEFT), QLoRA, and reinforcement learning methods like GRPO. Instead of managing distributed systems or heavy engineering overhead, developers can focus on task design, data quality, and evaluation.

A key advantage of Unsloth is its strong support for parameter-efficient methods. With PEFT and QLoRA, only a small subset of parameters needs to be trained, significantly reducing memory requirements and training time while maintaining model performance. This allows powerful models to be adapted on a single machine.

Unsloth also enables advanced alignment through GRPO-based reinforcement learning. Beyond imitation learning, developers can directly optimize model behavior toward domain-specific objectives—such as generating investor-focused financial summaries or emphasizing risk signals.

By combining efficiency, simplicity, and reproducibility, Unsloth bridges the gap between cutting-edge research and practical deployment, enabling developers to turn general-purpose foundation models into domain-specialized systems.

## Prerequisites



## Installing unsloth

```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth" unsloth-zoo
pip install bitsandbytes
pip install --no-deps --upgrade timm # Only for Gemma 3N
```

## Installing and running jupyterlab
```bash
pip install jupyterlab
jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

## Unsloth LORA Finetune Example  

#### FastModel supports loading nearly any model now! This includes Vision and Text models!
```python
from unsloth import FastModel
import torch

model, tokenizer = FastModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",
    dtype = None, # None for auto detection
    max_seq_length = 1024, # Choose any for long context!
    load_in_4bit = True,  # 4 bit quantization to reduce memory
    full_finetuning = False, # [NEW!] We have full finetuning now!
    # token = "YOUR_HF_TOKEN", # HF Token for gated models
)

```

### Gemma 3N can process Text, Vision and Audio!

#### Let's first experience how Gemma 3N can handle multimodal inputs. We use Gemma 3N's recommended settings of temperature = 1.0, top_p = 0.95, top_k = 64
```python
from transformers import TextStreamer
# Helper function for inference
def do_gemma_3n_inference(messages, max_new_tokens = 128):
    _ = model.generate(
        **tokenizer.apply_chat_template(
            messages,
            add_generation_prompt = True, # Must add for generation
            tokenize = True,
            return_dict = True,
            return_tensors = "pt",
        ).to("cuda"),
        max_new_tokens = max_new_tokens,
        temperature = 1.0, top_p = 0.95, top_k = 64,
        streamer = TextStreamer(tokenizer, skip_prompt = True),
    )
```

### Gemma 3N can see images!
![alt text](assets/image.png)

```python
sloth_link = "https://files.worldwildlife.org/wwfcmsprod/images/Sloth_Sitting_iStock_3_12_2014/story_full_width/8l7pbjmj29_iStock_000011145477Large_mini__1_.jpg"

messages = [{
    "role" : "user",
    "content": [
        { "type": "image", "image" : sloth_link },
        { "type": "text",  "text" : "Which films does this animal feature in?" }
    ]
}]
# You might have to wait 1 minute for Unsloth's auto compiler
do_gemma_3n_inference(messages, max_new_tokens = 256)
```

#### Let's make a poem about sloths!

```python
messages = [{
    "role": "user",
    "content": [{ "type" : "text",
                  "text" : "Write a poem about sloths." }]
}]
do_gemma_3n_inference(messages)
```

### Gemma 3N can also hear!

```python
from IPython.display import Audio, display
Audio("https://www.nasa.gov/wp-content/uploads/2015/01/591240main_JFKmoonspeech.mp3")
!wget -qqq https://www.nasa.gov/wp-content/uploads/2015/01/591240main_JFKmoonspeech.mp3 -O audio.mp3

audio_file = "audio.mp3"

messages = [{
    "role" : "user",
    "content": [
        { "type": "audio", "audio" : audio_file },
        { "type": "text",  "text" : "What is this audio about?" }
    ]
}]
do_gemma_3n_inference(messages, max_new_tokens = 256)
```

### Let's combine all 3 modalities together!

```python
messages = [{
    "role" : "user",
    "content": [
        { "type": "audio", "audio" : audio_file },
        { "type": "image", "image" : sloth_link },
        { "type": "text",  "text" : "What is this audio and image about? "\
                                    "How are they related?" }
    ]
}]
do_gemma_3n_inference(messages, max_new_tokens = 256)
```

### Let's finetune Gemma 3N!
You can finetune the vision and text parts for now through selection - the audio part can also be finetuned - we're working to make it selectable as well!

We now add LoRA adapters so we only need to update a small amount of parameters!

```python
model = FastModel.get_peft_model(
    model,
    finetune_vision_layers     = False, # Turn off for just text!
    finetune_language_layers   = True,  # Should leave on!
    finetune_attention_modules = True,  # Attention good for GRPO
    finetune_mlp_modules       = True,  # Should leave on always!

    r = 8,           # Larger = higher accuracy, but might overfit
    lora_alpha = 8,  # Recommended alpha == r at least
    lora_dropout = 0,
    bias = "none",
    random_state = 3407,
)
```

### Data Prep
We now use the Gemma-3 format for conversation style finetunes. We use Maxime Labonne's FineTome-100k dataset in ShareGPT style. Gemma-3 renders multi turn conversations like below:

<bos><start_of_turn>user
Hello!<end_of_turn>
<start_of_turn>model
Hey there!<end_of_turn>
We use our get_chat_template function to get the correct chat template. We support zephyr, chatml, mistral, llama, alpaca, vicuna, vicuna_old, phi3, llama3, phi4, qwen2.5, gemma3 and more.

```python
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "gemma-3",
)
```
We get the first 3000 rows of the dataset
```python
from datasets import load_dataset
dataset = load_dataset("mlabonne/FineTome-100k", split = "train[:3000]")
```
We now use standardize_data_formats to try converting datasets to the correct format for finetuning purposes!
```python
from unsloth.chat_templates import standardize_data_formats
dataset = standardize_data_formats(dataset)
```

Let's see how row 100 looks like!
```python
dataset[100]
```
We now have to apply the chat template for Gemma-3 onto the conversations, and save it to text. We remove the <bos> token using removeprefix('<bos>') since we're finetuning. The Processor will add this token before training and the model expects only one.
```python
def formatting_prompts_func(examples):
   convos = examples["conversations"]
   texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False).removeprefix('<bos>') for convo in convos]
   return { "text" : texts, }

dataset = dataset.map(formatting_prompts_func, batched = True)
```
Let's see how the chat template did! Notice there is no <bos> token as the processor tokenizer will be adding one.
```python
dataset[100]["text"]
```

### Train the model
Now let's train our model. We do 60 steps to speed things up, but you can set num_train_epochs=1 for a full run, and turn off max_steps=None.

```python
from trl import SFTTrainer, SFTConfig
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    eval_dataset = None, # Can set up evaluation!
    args = SFTConfig(
        dataset_text_field = "text",
        per_device_train_batch_size = 1,
        gradient_accumulation_steps = 4, # Use GA to mimic batch size!
        warmup_steps = 5,
        # num_train_epochs = 1, # Set this for 1 full training run.
        max_steps = 60,
        learning_rate = 2e-4, # Reduce to 2e-5 for long training runs
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.001,
        lr_scheduler_type = "linear",
        seed = 3407,
        report_to = "none", # Use TrackIO/WandB etc
    ),
)
```
We also use Unsloth's train_on_completions method to only train on the assistant outputs and ignore the loss on the user's inputs. This helps increase accuracy of finetunes!
```python
from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<start_of_turn>user\n",
    response_part = "<start_of_turn>model\n",
)
```

Let's verify masking the instruction part is done! Let's print the 100th row again. Notice how the sample only has a single <bos> as expected!

```python
tokenizer.decode(trainer.train_dataset[100]["input_ids"])
```

Now let's print the masked out example - you should see only the answer is present:

```python
tokenizer.decode([tokenizer.pad_token_id if x == -100 else x for x in trainer.train_dataset[100]["labels"]]).replace(tokenizer.pad_token, " ")
```
```python
# @title Show current memory stats
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"{start_gpu_memory} GB of memory reserved.")
```
### Let's train the model!
To resume a training run, set trainer.train(resume_from_checkpoint = True)
```python
trainer_stats = trainer.train()
```

```python
# @title Show final memory and time stats
used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
used_percentage = round(used_memory / max_memory * 100, 3)
lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)
print(f"{trainer_stats.metrics['train_runtime']} seconds used for training.")
print(
    f"{round(trainer_stats.metrics['train_runtime']/60, 2)} minutes used for training."
)
print(f"Peak reserved memory = {used_memory} GB.")
print(f"Peak reserved memory for training = {used_memory_for_lora} GB.")
print(f"Peak reserved memory % of max memory = {used_percentage} %.")
print(f"Peak reserved memory for training % of max memory = {lora_percentage} %.")
```


### Inference
Let's run the model via Unsloth native inference! According to the Gemma-3 team, the recommended settings for inference are temperature = 1.0, top_p = 0.95, top_k = 64
```python
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "gemma-3",
)
messages = [{
    "role": "user",
    "content": [{
        "type" : "text",
        "text" : "Continue the sequence: 1, 1, 2, 3, 5, 8,",
    }]
}]
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt = True, # Must add for generation
    return_tensors = "pt",
    tokenize = True,
    return_dict = True,
).to("cuda")
outputs = model.generate(
    **inputs,
    max_new_tokens = 64, # Increase for longer outputs!
    # Recommended Gemma-3 settings!
    temperature = 1.0, top_p = 0.95, top_k = 64,
)
tokenizer.batch_decode(outputs)
```
You can also use a TextStreamer for continuous inference - so you can see the generation token by token, instead of waiting the whole time!

```python
messages = [{
    "role": "user",
    "content": [{"type" : "text", "text" : "Why is the sky blue?",}]
}]
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt = True, # Must add for generation
    return_tensors = "pt",
    tokenize = True,
    return_dict = True,
).to("cuda")

from transformers import TextStreamer
_ = model.generate(
    **inputs,
    max_new_tokens = 64, # Increase for longer outputs!
    # Recommended Gemma-3 settings!
    temperature = 1.0, top_p = 0.95, top_k = 64,
    streamer = TextStreamer(tokenizer, skip_prompt = True),
)
```
### Saving, loading finetuned models
To save the final model as LoRA adapters, either use Hugging Face's push_to_hub for an online save or save_pretrained for a local save.

[NOTE] This ONLY saves the LoRA adapters, and not the full model. To save to 16bit or GGUF, scroll down!

```python
model.save_pretrained("gemma_3n_lora")  # Local saving
tokenizer.save_pretrained("gemma_3n_lora")
# model.push_to_hub("HF_ACCOUNT/gemma_3n_lora", token = "YOUR_HF_TOKEN") # Online saving
# tokenizer.push_to_hub("HF_ACCOUNT/gemma_3n_lora", token = "YOUR_HF_TOKEN") # Online saving
```
Now if you want to load the LoRA adapters we just saved for inference, set False to True:

```python
if False:
    from unsloth import FastModel
    model, tokenizer = FastModel.from_pretrained(
        model_name = "gemma_3n_lora", # YOUR MODEL YOU USED FOR TRAINING
        max_seq_length = 2048,
        load_in_4bit = True,
    )

messages = [{
    "role": "user",
    "content": [{"type" : "text", "text" : "What is Gemma-3N?",}]
}]
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt = True, # Must add for generation
    return_tensors = "pt",
    tokenize = True,
    return_dict = True,
).to("cuda")

from transformers import TextStreamer
_ = model.generate(
    **inputs,
    max_new_tokens = 128, # Increase for longer outputs!
    # Recommended Gemma-3 settings!
    temperature = 1.0, top_p = 0.95, top_k = 64,
    streamer = TextStreamer(tokenizer, skip_prompt = True),
)
```

### Saving to float16 for VLLM
We also support saving to float16 directly for deployment! We save it in the folder gemma-3N-finetune. Set if False to if True to let it run!
```python
if False: # Change to True to save finetune!
    model.save_pretrained_merged("gemma-3N-finetune", tokenizer)
```
If you want to upload / push to your Hugging Face account, set if False to if True and add your Hugging Face token and upload location!
```python
if False: # Change to True to upload finetune
    model.push_to_hub_merged(
        "HF_ACCOUNT/gemma-3N-finetune", tokenizer,
        token = "YOUR_HF_TOKEN"
    )
```
### GGUF / llama.cpp Conversion
To save to GGUF / llama.cpp, we support it natively now for all models! For now, you can convert easily to Q8_0, F16 or BF16 precision. Q4_K_M for 4bit will come later!
```python
if False: # Change to True to save to GGUF
    model.save_pretrained_gguf(
        "gemma_3n_finetune",
        tokenizer,
        quantization_method = "Q8_0", # For now only Q8_0, BF16, F16 supported
    )
```
Likewise, if you want to instead push to GGUF to your Hugging Face account, set if False to if True and add your Hugging Face token and upload location!
```python
if False: # Change to True to upload GGUF
    model.push_to_hub_gguf(
        "HF_ACCOUNT/gemma_3n_finetune",
        tokenizer,
        quantization_method = "Q8_0", # Only Q8_0, BF16, F16 supported
        token = "YOUR_HF_TOKEN",
    )
```
Now, use the gemma-3N-finetune.gguf file or gemma-3N-finetune-Q4_K_M.gguf file in llama.cpp.



## Next Steps
And we're done! If you have any questions on Unsloth, we have a Discord channel! If you find any bugs or want to keep updated with the latest LLM stuff, or need help, join projects etc, feel free to join our Discord!

## Resources

Below are some additional resources to learn more about unsloth and finetuning on 

* A comprehensive official guide covering basics and best practices for supervised fine-tuning (SFT), QLoRA, RL methods (including GRPO), dataset prep, and workflows. Fine‑tuning LLMs Guide | Unsloth Documentation https://docs.unsloth.ai/get-started/fine-tuning-llms-guide?utm_source=chatgpt.com

* Unsloth GitHub Repository: The central code repo with installation instructions, example notebooks, and links to additional resources such as community discussions and blog posts. Unsloth on GitHub (unslothai/unsloth)https://github.com/unslothai/unsloth?utm_source=chatgpt.com

* A model-specific walkthrough showing how to run and fine-tune the Qwen3 family with Unsloth, including setups for longer context lengths and advanced workflows: https://unsloth.ai/docs/models/qwen3-how-to-run-and-fine-tune?utm_source=chatgpt.com

* Train your own reasoning model - Llama GRPO notebook Free Colab-GRPO.ipynb
* Saving finetunes to Ollama. Free notebook-Ollama.ipynb
