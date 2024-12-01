import bpy

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
        layout.operator("ai.generate_code")

class AIQueryOperator(bpy.types.Operator):
    bl_idname = "ai.generate_code"
    bl_label = "Generate Code"

    def execute(self, context):
        prompt = context.scene.ai_prompt
        response = query_lm_studio(prompt)
        
        if response:
            layout = bpy.context.area.ui_type
            if hasattr(layout, 'draw'):
                layout.draw(context)
            self.report({'INFO'}, f"Code Generated: {response}")
        else:
            self.report({'ERROR'}, "Failed to generate code")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AIInteractionPanel)
    bpy.utils.register_class(AIQueryOperator)
    bpy.types.Scene.ai_prompt = bpy.props.StringProperty(
        name="AI Prompt",
        description="Input your prompt here",
        default=""
    )

def unregister():
    bpy.utils.unregister_class(AIInteractionPanel)
    bpy.utils.unregister_class(AIQueryOperator)
    del bpy.types.Scene.ai_prompt

if __name__ == "__main__":
    register()

