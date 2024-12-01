import bpy
import asyncio
import logging

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
        # Additional UI elements
        layout.label(text="Object Type:")
        layout.prop(context.scene, "object_type", text="")
        layout.label(text="Tool Settings:")
        layout.prop(context.scene, "tool_settings", text="")
        layout.label(text="Material Settings:")
        layout.prop(context.scene, "material_settings", text="")
        layout.label(text="Lighting Settings:")
        layout.prop(context.scene, "lighting_settings", text="")
        layout.label(text="Camera Settings:")
        layout.prop(context.scene, "camera_settings", text="")
        layout.label(text="Animation Settings:")
        layout.prop(context.scene, "animation_settings", text="")
        layout.label(text="Physics Settings:")
        layout.prop(context.scene, "physics_settings", text="")
        layout.label(text="Rendering Settings:")
        layout.prop(context.scene, "rendering_settings", text="")

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
    # Additional properties
    bpy.types.Scene.object_type = bpy.props.StringProperty(
        name="Object Type",
        description="Select the object type",
        default=""
    )
    bpy.types.Scene.tool_settings = bpy.props.StringProperty(
        name="Tool Settings",
        description="Select the tool settings",
        default=""
    )
    bpy.types.Scene.material_settings = bpy.props.StringProperty(
        name="Material Settings",
        description="Select the material settings",
        default=""
    )
    bpy.types.Scene.lighting_settings = bpy.props.StringProperty(
        name="Lighting Settings",
        description="Select the lighting settings",
        default=""
    )
    bpy.types.Scene.camera_settings = bpy.props.StringProperty(
        name="Camera Settings",
        description="Select the camera settings",
        default=""
    )
    bpy.types.Scene.animation_settings = bpy.props.StringProperty(
        name="Animation Settings",
        description="Select the animation settings",
        default=""
    )
    bpy.types.Scene.physics_settings = bpy.props.StringProperty(
        name="Physics Settings",
        description="Select the physics settings",
        default=""
    )
    bpy.types.Scene.rendering_settings = bpy.props.StringProperty(
        name="Rendering Settings",
        description="Select the rendering settings",
        default=""
    )

def unregister():
    bpy.utils.unregister_class(AIInteractionPanel)
    bpy.utils.unregister_class(AIQueryOperator)
    del bpy.types.Scene.ai_prompt
    # Additional properties
    del bpy.types.Scene.object_type
    del bpy.types.Scene.tool_settings
    del bpy.types.Scene.material_settings
    del bpy.types.Scene.lighting_settings
    del bpy.types.Scene.camera_settings
    del bpy.types.Scene.animation_settings
    del bpy.types.Scene.physics_settings
    del bpy.types.Scene.rendering_settings

if __name__ == "__main__":
    register()