import bpy
import requests
from llama_cpp import Model, Context, Token
from oneapi import dpctl
from openvino.runtime import Core

# Configuration Parameters
API_URL = "http://127.0.0.1:5000/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here"  # Replace with an actual token if required
}
DEFAULT_MODEL = "llama"
TEMPERATURE = 0.7
MAX_TOKENS = 512

# Initialize LLaMA model using llama-cpp-python
model_path = "path/to/your/model.bin"
context = Context()
model = Model(model_path, context)

# Initialize OpenVINO for inference on Intel A750 GPU
core = Core()
model_name = "llama_openvino_model.xml"
compiled_model = core.compile_model(model_name, device_name="GPU")

def query_lm_studio(prompt, model=DEFAULT_MODEL):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def generate_blender_code(prompt):
    # Fetch AI-generated response from LM Studio
    ai_response = query_lm_studio(prompt)
    
    if not ai_response:
        return None
    
    # Convert AI response to Blender code using LLaMA model
    tokens = Token.from_string(ai_response["choices"][0]["message"]["content"])
    generated_code = model.generate(tokens, TEMPERATURE, MAX_TOKENS)
    
    # Optimize code on Intel GPU using OpenVINO
    optimized_code = compiled_model(generated_code)
    
    return optimized_code

class AIInteractionPanel(bpy.types.Panel):
    bl_label = "AI Interaction"
    bl_idname = "OBJECT_PT_ai_interaction"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AI Tools"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Enter Prompt:")
        layout.prop(context.scene, "ai_prompt", text="")
        layout.operator("ai.query")

class AIQueryOperator(bpy.types.Operator):
    bl_idname = "ai.query"
    bl_label = "Query AI"

    def execute(self, context):
        prompt = context.scene.get("ai_prompt", "")
        if prompt:
            code = generate_blender_code(prompt)
            if code:
                print(f"Generated Blender Code:\n{code}")
                # Add generated code to the scene or use it as needed
            else:
                print("Error generating Blender code")
        return {"FINISHED"}

def register():
    bpy.types.Scene.ai_prompt = bpy.props.StringProperty(name="AI Prompt")
    bpy.utils.register_class(AIInteractionPanel)
    bpy.utils.register_class(AIQueryOperator)

def unregister():
    bpy.utils.unregister_class(AIInteractionPanel)
    bpy.utils.unregister_class(AIQueryOperator)
    del bpy.types.Scene.ai_prompt

if __name__ == "__main__":
    register()
