Blender GPT-4 Integration with LLaMA-Mesh-GGUF
Overview
This repository contains a Python-based Blender extension designed to integrate with the LLaMA-Mesh-GGUF model hosted on a local server (LM Studio) at http://localhost:5000. The extension allows you to interactively generate and manipulate Blender code using advanced language models. It provides a seamless way to leverage AI-driven interactions within Blender, enhancing your workflow and productivity.

Key Features
Interactive Prompting:

Easily input prompts directly into the Blender UI.
Support for real-time rendering of generated Blender code.
Model Integration:

Uses LLaMA-Mesh-GGUF model for generating responses.
Customizable model parameters to fine-tune performance and output quality.
Real-time Rendering:

Optimized for seamless real-time rendering within Blender.
Minimal latency, ensuring smooth interactions between Blender and the AI model.
Error Handling:

Robust error handling to manage failed or malformed requests.
Descriptive error messages and fallback mechanisms for server downtime.
UI Enhancements:

Extends Blender's UI with custom panels and operators.
Customizable interface for better user interaction and navigation.
Installation
Clone the Repository:

git clone https://github.com/your-username/blender-gpt4-extension.git

Open Blender:

Start Blender from your desktop or through your preferred method.
Ensure you have Python installed on your system.
Install Dependencies:

Install required packages using pip:
pip install requests asyncio

Register the Extension:

In Blender, go to Edit > Preferences > Add-ons.
Click on the "Install" button and select the blender-gpt4-extension directory.
Enable the extension by checking the checkbox next to it.
Configure API Key (if required):

If your LM Studio instance requires authentication, update the HEADERS dictionary in the code to include the necessary token.
Usage
Open Blender and go to the 3D Viewport.
Navigate to Custom Panel:
In the top-right corner of the 3D Viewport, locate the "AI Tools" tab.
Click on it to expand the panel.
Input Prompt:
Enter your prompt in the "Enter Prompt" field.
Generate Code:
Click the "Query AI" button to generate Blender code based on your prompt.
Advanced Usage
Batch Queries:

If Blender triggers frequent AI calls, batch them to reduce server load.
Configure batching parameters in the extension settings.
Caching Responses:

Cache responses for similar prompts to minimize redundant processing.
Configure caching parameters in the extension settings.
Custom Model Parameters:

Fine-tune model parameters such as temperature and max_tokens.
Adjust these parameters in the code to optimize response quality.
Customization
Modify UI Elements:

Extend or modify the custom UI elements (panels, buttons) by editing the Python scripts.
Save changes and reload Blender to see your customizations.
Add New Features:

Implement new features by adding additional functions and operators.
Ensure that all code is well-documented for future maintenance and updates.
Troubleshooting
Check Network Connection:

Ensure that LM Studio is running and accessible at http://localhost:5000.
Verify network settings and firewall rules if necessary.
Verify Model Name:

Make sure that the model name ("model": "llama") is correctly specified.
Check for any typos or mismatches in the model configuration.
Error Messages:

Check the Blender UI for any error messages to diagnose issues.
Look at the console output for detailed error information.
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

# Configuration Parameters
API_URL = "http://127.0.0.1:5000/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here"  # Replace with an actual token if required
}
DEFAULT_MODEL = "llama"
TEMPERATURE = 0.7
MAX_TOKENS = 512

Example Code Snippets
Connecting to the LM Studio Local Server
import requests

def query_lm_studio(prompt, model="llama"):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

Integrating the Blender Python API
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

def register():
    bpy.types.Scene.ai_prompt = bpy.props.StringProperty(name="AI Prompt")
    bpy.types.Scene.ai_result = bpy.props.StringProperty(name="AI Result")
    bpy.utils.register_class(AIInteractionPanel)
    bpy.utils.register_class(AIQueryOperator)

def unregister():
    bpy.utils.unregister_class(AIInteractionPanel)
    bpy.utils.unregister_class(AIQueryOperator)
    del bpy.types.Scene.ai_prompt
    del bpy.types.Scene.ai_result

Optimizing Response Handling
def optimize_responses(responses):
    # Batch queries, cache responses, handle errors, etc.
    pass

Test Cases
To validate the integration and performance of your extension, consider the following test cases:

Basic Functionality:

Send a simple prompt to LM Studio and verify that a valid response is received.
Latency Test:

Measure the time taken for the AI model to respond to prompts.
Ensure that the latency is acceptable for real-time rendering.
Error Handling:

Simulate server downtime or invalid requests and verify that error messages are displayed correctly.
Performance Optimization:

Test batch queries and caching mechanisms.
Measure the impact on performance and resource usage.