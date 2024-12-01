import bpy
import requests
import logging
import gradio as gr
import time
import random
import gc

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_model_response(prompt, chat_history, system_prompt, model_params=None, retry_count=3):
    try:
        model_params = model_params or {"temperature": 0.7, "top_p": 0.9, "max_tokens": 1500}
        url = "http://localhost:5000/generate"  # LM Studio API URL
        
        payload = {
            "model": "llama",  # Model name can be adjusted
            "prompt": prompt,
            "chat_history": chat_history,
            "system_prompt": system_prompt,
            **model_params
        }

        # Retry logic for failed requests
        for attempt in range(retry_count):
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("text", "No response from model")
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(1, 2))  # Randomized delay before retry
                    continue
                return "Error: Request to model failed after multiple attempts."
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "Error: Unexpected issue occurred"

def generate_message_history(chat_history, system_prompt, prompt):
    # Limit chat history to the last 5 exchanges for optimized payload
    history_limit = 5
    messages = [{"role": "system", "content": system_prompt}]
    
    for message in chat_history[-history_limit:]:
        if message["type"] == "assistant":
            messages.append({"role": "assistant", "content": "```\n" + message["content"] + "\n```"})
        else:
            messages.append({"role": message["type"].lower(), "content": message["content"]})

    messages.append({"role": "user", "content": "Can you please write Blender code for me that accomplishes the following task: " + prompt + "? \n. Do not respond with anything that is not Python code. Do not provide explanations"})
    return messages

async def gradio_interface(prompt, state):
    chat_history = state or []
    response = await asyncio.to_thread(get_model_response, prompt, chat_history, "You are a helpful Blender scripting assistant.")
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": response})
    
    # Reduce chat history if it gets too large to save memory
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
    
    # Clean up memory and trigger garbage collection
    gc.collect()

    return response, chat_history

# Gradio interface setup with async
gr.Interface(fn=gradio_interface, inputs=["text", "state"], outputs=["text", "state"]).launch()

def init_props():
    bpy.types.Scene.gpt4_chat_history = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.gpt4_model = bpy.props.EnumProperty(
        name="GPT Model",
        description="Select the GPT model to use",
        items=[("local", "Local Model", "Use local model"), ("lm_studio", "LM Studio", "Use LM Studio model")],
        default="local",
    )
    bpy.types.Scene.gpt4_chat_input = bpy.props.StringProperty(
        name="Message",
        description="Enter your message",
        default="",
    )
    bpy.types.Scene.gpt4_button_pressed = bpy.props.BoolProperty(default=False)
    bpy.types.PropertyGroup.type = bpy.props.StringProperty()
    bpy.types.PropertyGroup.content = bpy.props.StringProperty()

def clear_props():
    del bpy.types.Scene.gpt4_chat_history
    del bpy.types.Scene.gpt4_chat_input
    del bpy.types.Scene.gpt4_button_pressed

def split_area_to_text_editor(context):
    area = context.area
    for region in area.regions:
        if region.type == 'WINDOW':
            override = {'area': area, 'region': region}
            bpy.ops.screen.area_split(override, direction='VERTICAL', factor=0.5)
            break

    new_area = context.screen.areas[-1]
    new_area.type = 'TEXT_EDITOR'
    return new_area
