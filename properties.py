import bpy

def init_props():
    bpy.types.Scene.gpt4_chat_history = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.gpt4_model = bpy.props.EnumProperty(
        name="GPT Model",
        description="Select the GPT model to use",
        items=[("local", "Local Model", "Use local model")],
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

init_props()
# Register and unregister functions
def get_model_response(prompt, chat_history, system_prompt, model_params=None, retry_count=3):
    try:
        url = "http://localhost:5000/generate"  # Local model API URL
        
        payload = {
            "model": "llama",  # Model name can be adjusted
            "prompt": prompt,
            "chat_history": chat_history,
            "system_prompt": system_prompt,
            **model_params
        }

        for attempt in range(retry_count):
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return response.json().get("text", "No response from model")
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(1, 2))  # Randomized delay before retry
                    continue
                return "Error: Request to model failed after multiple attempts."
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Error: Unexpected issue occurred"