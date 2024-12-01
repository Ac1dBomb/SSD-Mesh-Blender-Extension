import bpy
import requests
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

class ChatMessage(BaseModel):
    type: str
    content: str

# Function to get response from the model
@app.post("/model_chat/")
async def model_chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    chat_history = data.get("chat_history", [])
    system_prompt = "You are an assistant designed to help with Blender modeling tasks."

    # Simulate getting response from the model
    response_content = f"Generated Python script for: {prompt}"
    
    new_message = ChatMessage(type="assistant", content=response_content)
    chat_history.append(new_message.dict())
    
    return {"chat_history": chat_history}

# Start FastAPI server
def start_fastapi_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Operator to handle button press for model response
class GPT4BlenderOperator(bpy.types.Operator):
    bl_idname = "wm.gpt4_generate_response"
    bl_label = "Generate Blender Code"

    def execute(self, context):
        chat_history = []
        system_prompt = "You are an assistant designed to help with Blender modeling tasks."
        
        # Get response from model
        prompt = context.scene.gpt4_chat_input
        response_content = requests.post("http://127.0.0.1:8000/model_chat/", json={"prompt": prompt, "chat_history": chat_history}).json()
        
        logging.info(f"Model Response: {response_content}")
        
        # Add response to chat history
        new_message = bpy.types.PropertyGroup()
        new_message.type = "assistant"
        new_message.content = response_content["chat_history"][-1]["content"]
        context.scene.gpt4_chat_history.add().update(new_message)
        
        return {'FINISHED'}

# Register the operator and properties
def register():
    bpy.utils.register_class(GPT4BlenderOperator)
    init_props()

def unregister():
    clear_props()
    bpy.utils.unregister_class(GPT4BlenderOperator)

if __name__ == "__main__":
    register()
