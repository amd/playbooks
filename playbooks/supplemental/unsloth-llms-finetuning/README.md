## Overview

<!-- ![alt text](assets/unsloth.png) -->

Unsloth is a high-efficiency LLM fine-tuning framework designed to make advanced model customization accessible on modern hardware.

It streamlines supervised fine-tuning (SFT), parameter-efficient fine-tuning (PEFT), QLoRA, and reinforcement learning approaches such as GRPO—allowing developers to adapt powerful foundation models to domain-specific tasks without large-scale infrastructure.

Rather than relying on costly distributed training clusters, Unsloth enables practical, reproducible fine-tuning workflows that run efficiently on local AI systems like Ryzen™ AI Halo.

## What You'll Learn

- How to set up the Unsloth environment
- How to fine-tune a LLM using SFT with Unsloth
- How to save the fine-tune result in local storage

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

## Unsloth LORA Fine-tuning Example  

Unsloth can fine-tune the multi-modal model, benefit from FastModel's supporting loading nearly any model now. This includes Vision and Text models! Then here we use Gemma-3N-4B as an examble:

### Load model with unsloth

Let's configure the ENV varibles and load the model in Raw data precision:

```python
import os
from unsloth import FastModel
import torch

os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TORCH_COMPILE_DISABLE"] = "1"
torch._dynamo.disable()
device = "cuda:0"

model, tokenizer = FastModel.from_pretrained(
    model_name = "google/gemma-3n-E4B-it",
    dtype = None, # None for auto detection
    max_seq_length = 1024, # Choose any for long context!
    load_in_4bit = False,  # 4 bit quantization to reduce memory
    full_finetuning = False, # [NEW!] We have full finetuning now!
    dtype=torch.bfloat16, # Load in BF16
    device_map="auto",
    # token = "YOUR_HF_TOKEN", # HF Token for gated models
)
```
Unsloth welcome message and Loading the model weights:
![alt text](assets/welcome.png)
### Load model with unsloth in 4bit
4bit dynamic quants is for superior accuracy and low memory use. \
If you want to use quantized model, like 4bit model, you can set 'load_in_4bit' as True to enable the quantized model, and use 'unsloth/gemma-3n-E4B-it-unsloth-bnb-4bit', then it will save graphic memory.
* load_in_4bit = True
* "unsloth/gemma-3n-E4B-it-unsloth-bnb-4bit"

### Multi-modal Inference
Secondly, Gemma 3N can process multimodal inputs, like Text, Vision and Audio. \
Below are an inference example.

```python
from PIL import Image

text="Write a poem about sloths." # Text
image_file = Image.open("test.jpg") # Vision
audio_file = "assets/audio.mp3" # Audio

messages = [{
    "role" : "user",
    "content": [
        { "type": "audio", "audio" : audio_file },
        { "type": "image", "image" : image_file },
        { "type": "text",  "text" : "What is this audio and image about? "\
                                    "How are they related?" }
    ]
}]
do_gemma_3n_inference(messages, max_new_tokens = 256)
```
The image example as below: 
![alt text](assets/image_input.png)
### Fine-tune Gemma 3N model!
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

<bos><start_of_turn>user \
Hello!<end_of_turn> \
<start_of_turn>model \
Hey there!<end_of_turn> 

We use our get_chat_template function to get the correct chat template. We support zephyr, chatml, mistral, llama, alpaca, vicuna, vicuna_old, phi3, llama3, phi4, qwen2.5, gemma3 and more.
We get the first 3000 rows of the dataset. We now use standardize_data_formats to try converting datasets to the correct format for finetuning purposes!
Notice there is no <bos> token as the processor tokenizer will be adding one.

####We now have to apply the chat template for Gemma-3 onto the conversations, and save it to text. We remove the <bos> token using removeprefix('<bos>') since we're finetuning. The Processor will add this token before training and the model expects only one.

```python
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "gemma-3",
)

from datasets import load_dataset
dataset = load_dataset("mlabonne/FineTome-100k", split = "train[:3000]")

from unsloth.chat_templates import standardize_data_formats
dataset = standardize_data_formats(dataset)

# Apply conversations chat templete

def formatting_prompts_func(examples):
   convos = examples["conversations"]
   texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False).removeprefix('<bos>') for convo in convos]
   return { "text" : texts, }

dataset = dataset.map(formatting_prompts_func, batched = True)
```
The tokenlizing process shows as below:
![alt text](assets/trainer.png)

### Train the model
Now let's train our model. We do 60 steps to speed things up, but you can set num_train_epochs=1 for a full run, and turn off max_steps=None. To resume a training run, set trainer.train(resume_from_checkpoint = True)
We also use Unsloth's train_on_completions method to only train on the assistant outputs and ignore the loss on the user's inputs. This helps increase accuracy of finetunes!
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

from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<start_of_turn>user\n",
    response_part = "<start_of_turn>model\n",
)
```
The progress of training shows as below:
![alt text](assets/training.png)


```python
# @title Show current memory stats
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"{start_gpu_memory} GB of memory reserved.")
```
The GPU stat output should be like:
![alt text](assets/gpu.png)
#### Check GPU status
```python
trainer_stats = trainer.train()

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
The mem usage output should be like:

![alt text](assets/mem_stat.png)

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
* streamer = TextStreamer(tokenizer, skip_prompt = True),


### Saving, loading finetuned models
To save the final model as LoRA adapters, either use Hugging Face's push_to_hub for an online save or save_pretrained for a local save.

[NOTE] This ONLY saves the LoRA adapters, and not the full model. To save to 16bit or GGUF, scroll down! 

Local saving
```python
model.save_pretrained("gemma_3n_lora")  
tokenizer.save_pretrained("gemma_3n_lora")
```
Online saving
```python
model.push_to_hub("HF_ACCOUNT/gemma_3n_lora", token = "YOUR_HF_TOKEN") 
tokenizer.push_to_hub("HF_ACCOUNT/gemma_3n_lora", token = "YOUR_HF_TOKEN") 
```

### Saving to float16 for VLLM
We also support saving to float16 directly for deployment! We save it in the folder gemma-3N-finetune. If you want to upload / push to your Hugging Face account, set if False to if True and add your Hugging Face token and upload location!
* Offline saving: model.save_pretrained_merged("gemma-3N-finetune", tokenizer)
* Online saving: model.push_to_hub_merged( "HF_ACCOUNT/gemma-3N-finetune", tokenizer,token = "YOUR_HF_TOKEN" )

### Saving to GGUF / llama.cpp Conversion  
To save to GGUF / llama.cpp, we support it natively now for all models! For now, you can convert easily to Q8_0, F16 or BF16 precision. Q4_K_M for 4bit will come later! Likewise, if you want to instead push to GGUF to your Hugging Face account, add your Hugging Face token and upload location!
* Offline saving: model.save_pretrained_gguf("gemma_3n_finetune",tokenizer,quantization_method = "Q8_0", # For now only Q8_0, BF16, F16 supported)
* Online saving: model.push_to_hub_gguf("HF_ACCOUNT/gemma_3n_finetune",tokenizer,quantization_method = "Q8_0",token = "YOUR_HF_TOKEN",)

### You can load the LoRA adapters we just saved for inference.
![alt text](assets/infer.png)


Now, use the gemma-3N-finetune.gguf file or gemma-3N-finetune-Q4_K_M.gguf file in llama.cpp.

### Run the script with above content.

[test_unsloth.py](assets/test_unsloth.py)

```bash
python assets/test_unsloth.py
```


## Next Steps
And we're done! If you have any questions on Unsloth, we have a Discord channel! If you find any bugs or want to keep updated with the latest LLM stuff, or need help, join projects etc, feel free to join our Discord!

## Resources

Below are some additional resources to learn more about unsloth and finetuning on 

* A comprehensive official guide covering basics and best practices for supervised fine-tuning (SFT), QLoRA, RL methods (including GRPO), dataset prep, and workflows. Fine‑tuning LLMs Guide | Unsloth Documentation https://docs.unsloth.ai/get-started/fine-tuning-llms-guide?utm_source=chatgpt.com

* Unsloth GitHub Repository: The central code repo with installation instructions, example notebooks, and links to additional resources such as community discussions and blog posts. Unsloth on GitHub (unslothai/unsloth)https://github.com/unslothai/unsloth?utm_source=chatgpt.com

* A model-specific walkthrough showing how to run and fine-tune the Qwen3 family with Unsloth, including setups for longer context lengths and advanced workflows: https://unsloth.ai/docs/models/qwen3-how-to-run-and-fine-tune?utm_source=chatgpt.com

* Train your own reasoning model - Llama GRPO notebook Free Colab-GRPO.ipynb
* Saving finetunes to Ollama. Free notebook-Ollama.ipynb
