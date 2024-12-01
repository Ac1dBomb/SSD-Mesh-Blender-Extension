import bpy
import requests
import asyncio
import logging
import numpy as np
from transformers import T5ForConditionalGeneration, T5Tokenizer
from openvino.inference_engine import IECore
from onnx import load_model
from openml import datasets
import oneapi as oa
from intelPython import ip

# Configure logging
logging.basicConfig(level=logging.ERROR)

# LM Studio API endpoint
LM_STUDIO_URL = "http://localhost:5000/v1/chat/completions"

# Adjust this if necessary

# Function to get response from the LM Studio model
async def get_model_response(prompt, chat_history, system_prompt, model_params=None):
    try:
        model_params = model_params or {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1500,
            "model": "t5"  # Specify the model name here
        }
        payload = {
            "messages": generate_message_history(chat_history, system_prompt, prompt),
            **model_params
        }
        response = await asyncio.to_thread(requests.post, LM_STUDIO_URL, json=payload)
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

# Function to handle chatbox commands
def handle_chatbox_commands(command, chat_history):
    if command.startswith("/cube"):
        # Create a cube with the specified size
        size = float(command.split(" ")[1])
        bpy.ops.mesh.primitive_cube_add(size=size)
        chat_history.append({"type": "assistant", "content": f"Cube created with size {size}"})
    elif command.startswith("/sphere"):
        # Create a sphere with the specified radius
        radius = float(command.split(" ")[1])
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius)
        chat_history.append({"type": "assistant", "content": f"Sphere created with radius {radius}"})
    elif command.startswith("/cylinder"):
        # Create a cylinder with the specified height and radius
        height = float(command.split(" ")[1])
        radius = float(command.split(" ")[2])
        bpy.ops.mesh.primitive_cylinder_add(height=height, radius=radius)
        chat_history.append({"type": "assistant", "content": f"Cylinder created with height {height} and radius {radius}"})
    elif command.startswith("/extrude"):
        # Extrude the selected object by the specified amount
        amount = float(command.split(" ")[1])
        bpy.ops.mesh.extrude(amount=amount)
        chat_history.append({"type": "assistant", "content": f"Extruded by {amount}"})
    elif command.startswith("/bevel"):
        # Bevel the selected object by the specified angle
        angle = float(command.split(" ")[1])
        bpy.ops.mesh.bevel(angle=angle)
        chat_history.append({"type": "assistant", "content": f"Beveled by {angle}"})
    elif command.startswith("/loopcut"):
        # Create a loop cut on the selected object with the specified number of cuts
        number = int(command.split(" ")[1])
        bpy.ops.mesh.loopcut(number=number)
        chat_history.append({"type": "assistant", "content": f"Loop cut created with {number} cuts"})
    elif command.startswith("/material"):
        # Set the material properties
        if command.split(" ")[1] == "color":
            color = command.split(" ")[2]
            bpy.context.object.data.materials[0].diffuse_color = color
            chat_history.append({"type": "assistant", "content": f"Material color set to {color}"})
        elif command.split(" ")[1] == "texture":
            texture = command.split(" ")[2]
            bpy.context.object.data.materials[0].texture = texture
            chat_history.append({"type": "assistant", "content": f"Material texture set to {texture}"})
        elif command.split(" ")[1] == "reflectivity":
            reflectivity = float(command.split(" ")[2])
            bpy.context.object.data.materials[0].reflectivity = reflectivity
            chat_history.append({"type": "assistant", "content": f"Material reflectivity set to {reflectivity}"})
    elif command.startswith("/light"):
        # Set the light properties
        if command.split(" ")[1] == "intensity":
            intensity = float(command.split(" ")[2])
            bpy.context.scene.objects["Light"].data.energy = intensity
            chat_history.append({"type": "assistant", "content": f"Light intensity set to {intensity}"})
        elif command.split(" ")[1] == "color":
            color = command.split(" ")[2]
            bpy.context.scene.objects["Light"].data.color = color
            chat_history.append({"type": "assistant", "content": f"Light color set to {color}"})
        elif command.split(" ")[1] == "direction":
            direction = command.split(" ")[2]
            bpy.context.scene.objects["Light"].rotation_euler = direction
            chat_history.append({"type": "assistant", "content": f"Light direction set to {direction}"})
    elif command.startswith("/camera"):
        # Set the camera properties
        if command.split(" ")[1] == "position":
            position = command.split(" ")[2]
            bpy.context.scene.objects["Camera"].location = position
            chat_history.append({"type": "assistant", "content": f"Camera position set to {position}"})
        elif command.split(" ")[1] == "orientation":
            orientation = command.split(" ")[2]
            bpy.context.scene.objects["Camera"].rotation_euler = orientation
            chat_history.append({"type": "assistant", "content": f"Camera orientation set to {orientation}"})
        elif command.split(" ")[1] == "focal_length":
            focal_length = float(command.split(" ")[2])
            bpy.context.scene.objects["Camera"].data.lens = focal_length
            chat_history.append({"type": "assistant", "content": f"Camera focal length set to {focal_length}"})
    elif command.startswith("/animation"):
        # Set the animation properties
        if command.split(" ")[1] == "frame_rate":
            frame_rate = int(command.split(" ")[2])
            bpy.context.scene.render.fps = frame_rate
            chat_history.append({"type": "assistant", "content": f"Animation frame rate set to {frame_rate}"})
        elif command.split(" ")[1] == "duration":
            duration = float(command.split(" ")[2])
            bpy.context.scene.render.frame_range = (0, duration)
            chat_history.append({"type": "assistant", "content": f"Animation duration set to {duration}"})
        elif command.split(" ")[1] == "easing":
            easing = command.split(" ")[2]
            bpy.context.scene.render.easing = easing
            chat_history.append({"type": "assistant", "content": f"Animation easing set to {easing}"})
    elif command.startswith("/physics"):
        # Set the physics properties
        if command.split(" ")[1] == "gravity":
            gravity = float(command.split(" ")[2])
            bpy.context.scene.physics.gravity = gravity
            chat_history.append({"type": "assistant", "content": f"Physics gravity set to {gravity}"})
        elif command.split(" ")[1] == "friction":
            friction = float(command.split(" ")[2])
            bpy.context.scene.physics.friction = friction
            chat_history.append({"type": "assistant", "content": f"Physics friction set to {friction}"})
        elif command.split(" ")[1] == "collision_detection":
            collision_detection = command.split(" ")[2]
            bpy.context.scene.physics.collision_detection = collision_detection
            chat_history.append({"type": "assistant", "content": f"Physics collision detection set to {collision_detection}"})
    elif command.startswith("/render"):
        # Set the rendering properties
        if command.split(" ")[1] == "resolution":
            resolution = command.split(" ")[2]
            bpy.context.scene.render.resolution = resolution
            chat_history.append({"type": "assistant", "content": f"Rendering resolution set to {resolution}"})
        elif command.split(" ")[1] == "quality":
            quality = command.split(" ")[2]
            bpy.context.scene.render.quality = quality
            chat_history.append({"type": "assistant", "content": f"Rendering quality set to {quality}"})
        elif command.split(" ")[1] == "output_format":
            output_format = command.split(" ")[2]
            bpy.context.scene.render.output_format = output_format
            chat_history.append({"type": "assistant", "content": f"Rendering output format set to {output_format}"})
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
        loop = asyncio.get_event_loop()
        ai_response = loop.run_in_executor(None, get_model_response, prompt, context.scene.gpt4_chat_history, "system message")
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