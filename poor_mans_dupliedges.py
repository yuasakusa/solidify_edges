bl_info = {
    "name": "Poor Man's DupliEdges",
    "description":
        "Copies a base object along the edges of a specified mesh object.",
    "author": "Yu Asakusa",
    "version": (1, 0),
    "category": "Object",
    "location":
        "3D View > Object > DupliEdges",
}


import bpy
import math
from mathutils import *


class DupliEdgesOperator(bpy.types.Operator):
    """Copy a base object along the edges of a specified mesh object."""
    bl_idname = "object.dupliedges_operator"
    bl_label = "DupliEdges"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        shape = context.active_object
        if shape is None or shape.type != 'MESH':
            raise TypeError('A mesh object must be active')
        base = None
        for obj in context.selected_objects:
            # The following line uses != instead of 'is not', and this is correct.
            # See http://blender.stackexchange.com/a/5955
            if obj != shape:
                if base is not None:
                    raise ValueError('Only one object must be selected')
                base = obj
        if base is None:
            raise ValueError('Only one object must be selected')
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
            scene.objects.link(new_obj)
        bpy.data.meshes.remove(mesh)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(DupliEdgesOperator.bl_idname)


def register():
    bpy.utils.register_class(DupliEdgesOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(DupliEdgesOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
