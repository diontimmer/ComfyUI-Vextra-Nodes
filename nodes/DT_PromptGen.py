from transformers import GPT2Tokenizer, GPT2LMHeadModel, set_seed
import os
import random

script_path = os.path.dirname(os.path.realpath(__file__))
comfy_path = script_path.split('custom_nodes')[0]

if not os.path.exists(f'{comfy_path}custom_nodes/VextraNodes/binary/distilgpt2-stable-diffusion-v2'):
    print('Downloading model...')
    os.system(f'git clone https://huggingface.co/FredZhang7/distilgpt2-stable-diffusion-v2 {comfy_path}custom_nodes/VextraNodes/binary/distilgpt2-stable-diffusion-v2')

tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
tokenizer.add_special_tokens({'pad_token': '[PAD]'})
model = GPT2LMHeadModel.from_pretrained(f'{comfy_path}custom_nodes/VextraNodes/binary/distilgpt2-stable-diffusion-v2')

class GetPrompt():
    """
    This node provides a simple interface to apply PixelSort blur to the output image.
    """
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Input Types
        """
        return {
            "required": {
                "temperature": ("FLOAT", {"default": 0.9, "min": 0.1, "max": 1.0, "step": 0.1}),
                "top_k": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
                "max_length": ("INT", {"default": 80, "min": 1, "max": 1000, "step": 1}),
                "repetition_penalty": ("FLOAT", {"default": 1.2, "min": 0, "max": 10, "step": 0.1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 1000000000, "step": 1}),
                "prompt": ("STRING", {"default": '', "multiline": True}),
                },
            "optional": {

                },
            }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_prompt_from_model"

    CATEGORY = "VextraNodes"

    def get_prompt_from_model(self, temperature=0.9, top_k=8, max_length=80, repetition_penalty=1.2, seed=-1, prompt=''):
        seed = int(seed) if seed != -1 else random.randint(1, 1000000)
        set_seed(seed)
        num_return_sequences=1        # the number of results to generate
        input_ids = tokenizer(prompt, return_tensors='pt').input_ids
        output = model.generate(input_ids, do_sample=True, temperature=temperature, top_k=top_k, max_length=max_length, num_return_sequences=num_return_sequences, repetition_penalty=repetition_penalty, penalty_alpha=0.6, no_repeat_ngram_size=1, early_stopping=True)
        return (tokenizer.decode(output[0], skip_special_tokens=True), )

NODE_CLASS_MAPPINGS = {
    "Prettify Prompt Using distilgpt2": GetPrompt
}
