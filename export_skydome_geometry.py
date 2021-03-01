"""
This script generates the skydome geometry data as stored in
iron/Sources/iron/data/ConstData.hx.

USAGE:
    On MacOS/Linux:
        Open Blender from the terminal to see the console output.
    On Windows:
        Open the Blender console via "Window > Toggle System Console".

    Select the skydome object in object mode and run this script. Note
    that the script flips the normals in the output. The original mesh
    is not modified.

    After running the script, open the console. If the script ran
    successfully, the generated vertex data was printed to the console,
    ready to copy to ConstData.hx.
"""
import bmesh
import bpy


def list_representation(lst) -> str:
    """List to string without spaces."""
    return f"[{','.join(str(i) for i in lst)}]"


def run():
    obj = bpy.context.object

    if obj is None:
        print("No object selected, aborting!")
        return

    if obj.type != "MESH":
        print(f"Selected object '{obj.name}' is not a mesh, aborting!")
        return

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="FIXED")

    indices = []
    pos = []
    nor = []

    # Fill index buffer
    for face in bm.faces:
        # Turn the normals inside
        face.normal_flip()

        for vert in face.verts:
            indices.append(vert.index)

    # Vertex buffer data
    for vert in bm.verts:
        pos.extend(vert.co)
        nor.extend(vert.normal)

    pos_rounded = [round(elem, 5) for elem in pos]
    nor_rounded = [round(elem, 5) for elem in nor]

    bm.free()

    print("\n====================")
    print(f"Calculated mesh data for object '{obj.name}':")
    print(f"Indices: {list_representation(indices)}")
    print("")
    print(f"Positions: {list_representation(pos_rounded)}")
    print("")
    print(f"Normals: {list_representation(nor_rounded)}")


if __name__ == "__main__":
    run()
