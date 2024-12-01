import bpy
import requests
import asyncio

# LM Studio API endpoint
LM_STUDIO_URL = "http://localhost:5000/v1/chat/completions"  # Adjust this if necessary

# Function to get response from the LM Studio model
def get_model_response(prompt, chat_history, system_prompt, model_params=None):
    try:
        model_params = model_params or {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1500,
            "model": "llama"  # Specify the model name here
        }
        
        payload = {
            "messages": generate_message_history(chat_history, system_prompt, prompt),
            **model_params
        }

        response = requests.post(LM_STUDIO_URL, json=payload)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from model")
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "Error: Unexpected issue occurred"

# Function to generate message history for sending to the model
def generate_message_history(chat_history, system_prompt, prompt):
    # Limit chat history to the last 5 exchanges for optimized payload
    history_limit = 5
    messages = [{"role": "system", "content": system_prompt}]
    
    for message in chat_history[-history_limit:]:
        if message["type"] == "assistant":
            messages.append({"role": "assistant", "content": "```\n" + message["content"] + "\n```"})
        else:
            messages.append({"role": message["type"].lower(), "content": message["content"]})

    messages.append({"role": "user", "content": prompt})
    return messages

# Operator to handle button press for model response
class GPT4BlenderOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_generate_response"
    bl_label = "Generate Blender Code"

    def execute(self, context):
        # Ensure the button is pressed only once to avoid multiple submissions
        if context.scene.gpt4_button_pressed:
            return {'CANCELLED'}
        
        # Mark button as pressed to avoid resubmission
        context.scene.gpt4_button_pressed = True
        prompt = context.scene.gpt4_chat_input

        # Get the response asynchronously and update chat history
        chat_history = context.scene.gpt4_chat_history
        ai_response = asyncio.run(get_model_response(prompt, chat_history, "system message"))

        if ai_response:
            context.scene.gpt4_chat_history.append({"role": "assistant", "content": ai_response})
        else:
            context.scene.gpt4_chat_history.append({"role": "assistant", "content": "Error connecting to AI server."})

        # Update Blender text editor with the result
        text_editor = split_area_to_text_editor(context)
        if len(context.scene.gpt4_chat_history) > 1:
            text_editor.text = context.scene.gpt4_chat_history[-1]["content"]

        # Reset button press flag
        context.scene.gpt4_button_pressed = False

        return {'FINISHED'}
    
# Register operator and add panel to Blender UI
def register():
    bpy.utils.register_class(GPT4BlenderOperator)
    init_props()

    # Add custom panel to Blender's UI
    bpy.types.VIEW3D_PT_tools_object.append(draw_panel)

def unregister():
    bpy.utils.unregister_class(GPT4BlenderOperator)
    clear_props()

    # Remove custom panel
    bpy.types.VIEW3D_PT_tools_object.remove(draw_panel)

# Panel for user input in Blender UI
def draw_panel(self, context):
    layout = self.layout

    layout.label(text="Blender GPT-4 Integration")

    layout.prop(context.scene, "gpt4_chat_input")
    layout.operator("wm.gpt4_generate_response", text="Generate Python Code")

    # Display chat history
    for message in context.scene.gpt4_chat_history:
        if message["role"] == "user":
            layout.label(text=f"User: {message['content']}")
        elif message["role"] == "assistant":
            layout.label(text=f"AI: {message['content']}")

# Run the register function to initialize
if __name__ == "__main__":
    register()
