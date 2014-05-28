# Solidify Edges

***Warning: Blender crashes occasionally with this addon (issue #1).  Until this bug is investigated and fixed, I do not recommend to use this addon.***

This is an addon for [Blender](http://www.blender.org/).  It provides a command which makes a copy of a cylinder (or some other object) for each edge of a specified mesh object.

## How to install and enable

1. Download solidify_edges.py.
2. Open User Preferences in Blender, and select Addons tab.
3. Select the button at the bottom labeled “Install from File...”.
4. Select the file you downloaded in step 1.
5. Enable the installed addon by adding the check mark.

For details, see [Blender Manual](http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Add-Ons).

## How to use

Suppose that you would like to solidify the edges of a target mesh object with cylinders.

1. Add a cylinder mesh whose depth is 2 Blender Units (default).  Set other properties and material appropriately.  Check the ID of this cylinder.
2. Make the target mesh object active in the 3D View window.
3. In Object menu, select “Solidify Edges...”.
4. In the dialog box, select the ID of the cylinder which you created in step 1.
5. Press OK.
6. If you do not wish to render the cylinder created in step 1, delete it or set it to hide_render (the camera icon in the Outliner window).
7. If you do not wish to render the target mesh object, delete it or set it to hide_render.

Tip: If you would like to render the _vertices_ of the target mesh as copies of a certain object, you may want to check [DupliVerts](http://wiki.blender.org/index.php/Doc:2.6/Manual/Modeling/Objects/Duplication/DupliVerts) in Blender.

## Technical description

The operation involves two objects: a _target object_ and a _base object_.  The target object must be a mesh object.  A base object can be any object, but it is usually a cylindrical mesh object whose axis coincides its local Z-axis, whose depth is 2 Blender Units, and which is centered at its local origin.

For each edge of the target object, a copy of the base object is created.  This copy is translated to the midpoint of the edge, rotated to make the local Z-axis coincide the edge, and scaled in the direction of the local Z-axis by a factor of L/2, where L is the length of the edge.

## Limitations

* The copied objects have arbitrary rotations around their Z-axis.  This may be a problem if the base object does not have cylindrical symmetry around its Z-axis.
* If the base object is not mirror symmetric about its local XY-plane, the result is affected by the order in which the two vertices of an edge are stored, which usually has no meaning.

## Related addon

* [Solidify Wireframe](http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Modeling/Solidify_Wireframe) by Yorik is another addon which turns the edges of a mesh into a mesh object.  It produces a cubical mesh instead of copies of a cylinder.

## License

Solidify Edges is licensed under GNU General Public License Version 3.
