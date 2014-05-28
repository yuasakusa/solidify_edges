# Solidify Edges: An addon for Blender to make a copy of an object for
# each edge of a specified mesh.
# Copyright (C) 2014 Yu Asakusa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


bl_info = {
    "name": "Solidify Edges",
    "description":
        "Creates a copy of an object for each edge of the active mesh object.",
    "author": "Yu Asakusa",
    "version": (1, 0, 1),
    "category": "Mesh",
    "location":
        "3D View > Object > Solidify Edges",
}


import bpy
import math
from mathutils import *


def rotation_matrix(v):
    """Return one of the 3x3 rotation matrices which map (0,0,1) to v.normalized().

    Note that there are many such matrices; it is not specified which
    of them is returned.  v must be nonzero.
    """
    direction = v.normalized()
    colatitude = Matrix.Rotation(math.acos(direction.z), 3, 'Y')
    azimuth = Matrix.Rotation(math.atan2(direction.y, direction.x), 3, 'Z')
    return azimuth * colatitude * azimuth.transposed()


class MeshSolidifyEdges(bpy.types.Operator):
    """Create a copy of an object for each edge of the active mesh object."""
    bl_idname = "mesh.solidify_edges"
    bl_label = "Solidify Edges"
    bl_options = {'UNDO'}

    base_ob_name = bpy.props.StringProperty(
        name="Base", description="Object to make copies of")

    @classmethod
    def poll(cls, context):
        target = context.active_object
        return target is not None and target.type == 'MESH'

    def execute(self, context):
        scene = context.scene
        target = context.active_object
        if target is None or target.type != 'MESH':
            raise TypeError('A mesh object must be active')
        base = context.blend_data.objects.get(self.base_ob_name)
        if base is None:
            return {'FINISHED'}
        orig_mat = base.matrix_world.to_3x3()
        axis = orig_mat * Vector((0.0, 0.0, 1.0))
        orig_mat = rotation_matrix(axis).transposed() * orig_mat
        mesh = target.to_mesh(
            scene=scene, apply_modifiers=True,
            settings='PREVIEW', calc_tessface=False)
        mesh.transform(target.matrix_world)
        vertices = mesh.vertices
        bpy.ops.object.select_all(action='DESELECT')
        for edge in mesh.edges:
            v0 = vertices[edge.vertices[0]].co
            v1 = vertices[edge.vertices[1]].co
            location = 0.5 * (v0 + v1)
            direction = 0.5 * (v1 - v0)
            scale = direction.length
            new_obj = base.copy()
            mat = (rotation_matrix(direction) *
                   Matrix.Scale(scale, 3, (0.0, 0.0, 1.0)) * orig_mat)
            mat = Matrix.Translation(location) * mat.to_4x4()
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
    self.layout.operator(MeshSolidifyEdges.bl_idname, text="Solidify Edges...")


def register():
    bpy.utils.register_class(MeshSolidifyEdges)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(MeshSolidifyEdges)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
