Blender GPT-4 Integration with LLaMA-Mesh-GGUF
Overview
This repository contains a Python-based Blender extension designed to integrate with the LLaMA-Mesh-GGUF model hosted on a local server (LM Studio) at http://localhost:5000. The extension allows you to interactively generate and manipulate Blender code using advanced language models.

Key Features
Interactive Prompting: Easily input prompts directly into the Blender UI.
Real-time Rendering: Optimized for seamless real-time rendering within Blender.
Model Integration: Uses LLaMA-Mesh-GGUF model for generating responses.
Customizable Model Parameters: Fine-tune model parameters to optimize response quality.
Error Handling: Robust error handling to manage failed or malformed requests.
Batch Queries: If Blender triggers frequent AI calls, batch them to reduce server load.
Caching Responses: Cache responses for similar prompts to minimize redundant processing.
Custom Model Parameters: Fine-tune model parameters such as temperature and max_tokens.
Installation
Clone the Repository: git clone https://github.com/your-username/blender-gpt4-extension.git
Open Blender: Start Blender from your desktop or through your preferred method.
Install Dependencies: Install required packages using pip: pip install requests asyncio
Register the Extension: In Blender, go to Edit > Preferences > Add-ons. Click on the "Install" button and select the blender-gpt4-extension directory.
Enable the Extension: Enable the extension by checking the checkbox next to it.
Usage
Open Blender: Start Blender and go to the 3D Viewport.
Navigate to Custom Panel: In the top-right corner of the 3D Viewport, locate the "AI Tools" tab. Click on it to expand the panel.
Input Prompt: Enter your prompt in the "Enter Prompt" field.
Generate Code: Click the "Query AI" button to generate Blender code based on your prompt.
View Response: The generated code will be displayed in the "Response" field.
Advanced Usage
Batch Queries: If Blender triggers frequent AI calls, batch them to reduce server load. To do this, go to the "Batch Queries" tab in the "AI Tools" panel and select the number of queries to batch.
Caching Responses: Cache responses for similar prompts to minimize redundant processing. To do this, go to the "Caching" tab in the "AI Tools" panel and select the caching strategy.
Custom Model Parameters: Fine-tune model parameters such as temperature and max_tokens. To do this, go to the "Model Parameters" tab in the "AI Tools" panel and adjust the parameters as needed.
Troubleshooting
Check Network Connection: Ensure that LM Studio is running and accessible at http://localhost:5000.
Verify Model Name: Make sure that the model name ("model": "llama") is correctly specified.
Error Messages: Check the Blender UI for any error messages to diagnose issues.
Server Logs: Check the server logs for any errors or issues.
Contributing
Contributions are welcome! If you encounter bugs or have suggestions, please create an issue or submit a pull request.

Code Structure
The extension is structured into several Python scripts and assets:

__init__.py: Main entry point for Blender to load the add-on.
ai_interaction.py: Handles AI interaction logic with LM Studio.
ui_elements.py: Defines custom UI elements (panels, operators).
utils.py: Utility functions for common tasks.
Configuration
Configuration parameters are defined in the __init__.py file. You can customize these parameters to suit your specific needs:

API_URL: The URL of the LM Studio local server.
HEADERS: The headers to include in requests to the LM Studio server.
DEFAULT_MODEL: The default model to use for generating responses.
TEMPERATURE: The temperature parameter for the model.
MAX_TOKENS: The maximum number of tokens to generate.
Example Code Snippets
Here are some example code snippets to get you started:

Connecting to the LM Studio Local Server:
import requests

def query_lm_studio(prompt, model="llama"): payload = { "model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 512 } response = requests.post("http://localhost:5000/v1/chat/completions", headers={"Content-Type": "application/json"}, json=payload) if response.status_code == 200: return response.json() else: print(f"Error: {response.status_code}, {response.text}") return None



*   **Integrating the Blender Python API**:
    ```python
import bpy

def ai_response(context, prompt):
    response = query_lm_studio(prompt)
    if response:
        context.scene["ai_result"] = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    else:
        context.scene["ai_result"] = "Error connecting to AI server."

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
            ai_response(context, prompt)
        return {"FINISHED"}