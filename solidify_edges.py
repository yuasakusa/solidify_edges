bl_info = {
    "name": "Solidify Edges",
    "description":
        "Creates a copy of an object for each edge of the active mesh object.",
    "author": "Yu Asakusa",
    "version": (1, 0),
    "category": "Mesh",
    "location":
        "3D View > Object > Solidify Edges",
}


import bpy
import math
from mathutils import *


class MeshSolidifyEdges(bpy.types.Operator):
    """Create a copy of an object for each edge of the active mesh object."""
    bl_idname = "mesh.solidify_edges"
    bl_label = "Solidify Edges"
    bl_options = {'REGISTER', 'UNDO'}

    base_ob_name = bpy.props.StringProperty(
        name="Base", description="Object to make copies of")

    @classmethod
    def poll(cls, context):
        shape = context.active_object
        return shape is not None and shape.type == 'MESH'

    def execute(self, context):
        scene = context.scene
        shape = context.active_object
        if shape is None or shape.type != 'MESH':
            raise TypeError('A mesh object must be active')
        base = context.blend_data.objects.get(self.base_ob_name)
        # The following line uses != instead of 'is not', and this is correct.
        # See http://blender.stackexchange.com/a/5955
        if base is None:
            return {'FINISHED'}
        orig_mat = base.matrix_world.to_3x3()
        axis = orig_mat * Vector((0.0, 0.0, 1.0))
        axis.normalize()
        colatitude1 = Matrix.Rotation(math.acos(axis.z), 3, 'Y')
        azimuth1 = Matrix.Rotation(math.atan2(axis.y, axis.x), 3, 'Z')
        # rot1 maps 'axis' to +Z
        rot1 = azimuth1 * colatitude1.transposed() * azimuth1.transposed()
        orig_mat = rot1 * orig_mat
        mesh = shape.to_mesh(
            scene=scene, apply_modifiers=True,
            settings='PREVIEW', calc_tessface=False)
        mesh.transform(shape.matrix_world)
        vertices = mesh.vertices
        bpy.ops.object.select_all(action='DESELECT')
        for edge in mesh.edges:
            v0 = vertices[edge.vertices[0]].co
            v1 = vertices[edge.vertices[1]].co
            direction = v1 - v0
            length = direction.length
            direction.normalize()
            new_obj = base.copy()
            colatitude = Matrix.Rotation(math.acos(direction.z), 3, 'Y')
            azimuth = Matrix.Rotation(math.atan2(direction.y, direction.x), 3, 'Z')
            # rot maps +Z to 'direction'
            rot = azimuth * colatitude * azimuth.transposed()
            mat = rot * Matrix.Scale(length, 3, (0.0, 0.0, 1.0)) * orig_mat
            mat = Matrix.Translation(v0) * mat.to_4x4()
            new_obj.matrix_world = mat
            new_obj.select = True
            scene.objects.link(new_obj)
        bpy.data.meshes.remove(mesh)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop_search(self, 'base_ob_name', context.blend_data, 'objects')


def menu_func(self, context):
    self.layout.operator(MeshSolidifyEdges.bl_idname)


def register():
    bpy.utils.register_class(MeshSolidifyEdges)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(MeshSolidifyEdges)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
