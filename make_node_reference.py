"""
Generates the logic nodes reference page for Armory3D's wiki:
https://github.com/armory3d/armory/wiki/reference

USAGE:
    First, generate the node screenshots (1). After that, open a
    terminal in the folder of this script and execute the following
    command (Blender must have the Armory add-on activated of course):

    path/to/blender.exe -b -P make_node_reference.py"

    This will create a "reference.md" file in the folder of this script
    from which you can copy the content into the logic node reference
    article. DO NOT commit that file to the armory_tools repo!

    Todo: Create a GitHub action to automatically update the reference
    upon logic node changes.

    (1) https://github.com/armory3d/armory_wiki_images/blob/master/logic_nodes/make_screenshots.py
        Please also read the usage notes in that file!
"""
import ensurepip
import itertools
import os
import subprocess
import sys
from typing import List

import bpy
from nodeitems_utils import NodeItem

from arm.logicnode import arm_nodes
import arm.props

ensurepip.bootstrap()
os.environ.pop("PIP_REQ_TRACKER", None)
subprocess.check_output([bpy.app.binary_path_python, '-m', 'pip', 'install', '--upgrade', 'markdownmaker'])

from markdownmaker.document import Document
from markdownmaker.markdownmaker import *

PY_NODE_DIR = "https://github.com/armory3d/armory/blob/master/blender/arm/logicnode/"
HX_NODE_DIR = "https://github.com/armory3d/armory/blob/master/Sources/armory/logicnode/"
IMG_DIR = "https://github.com/armory3d/armory_wiki_images/raw/master/logic_nodes/"


def get_anchor(text: str) -> str:
    """Gets the GitHub anchor id for a link."""
    return "#" + text.lower().replace(" ", "-")


def make_node_link(nodename: str) -> str:
    """Create a link to a node given by the name of the node"""
    return Link(label=InlineCode(nodename), url=get_anchor(nodename))


def get_nodetype(typename: str):
    """Convert the type name to the actual type."""
    return bpy.types.bpy_struct.bl_rna_get_subclass_py(typename)


def generate_node_documentation(nodeitem: NodeItem, category: arm_nodes.ArmNodeCategory):
    nodetype = get_nodetype(nodeitem.nodetype)
    doc: str = nodetype.__doc__
    if doc is not None:
        doc_parts = doc.split("@")

        # Show docstring until the first "@"
        node_description = doc_parts[0].rstrip("\n")
        # Remove trailing whitespace and ignore newlines
        node_description = " ".join(node_description.split()).replace("\n", "")

        deprecation_note = Optional()
        Document.add(deprecation_note)
        Document.add(Paragraph(node_description))

        has_see = False
        has_inputs = False
        has_outputs = False
        has_options = False
        see_list = []
        input_list = []
        output_list = []
        option_list = []
        for part in doc_parts:
            # Reference to other logic nodes
            if part.startswith("seeNode "):
                if not has_see:
                    has_see = True
                    Document.add(Paragraph(Bold("See also:")))
                    Document.add(UnorderedList(see_list))

                see_list.append(Italic(make_node_link(part[8:].rstrip())))

            # General references
            elif part.startswith("see "):
                if not has_see:
                    has_see = True
                    Document.add(Paragraph(Bold("See also:")))
                    Document.add(UnorderedList(see_list))

                see_list.append(Italic(part[4:].rstrip()))

        # Add node screenshot
        image_file = IMG_DIR + category.name.lower() + "/" + nodeitem.nodetype + ".jpg"
        Document.add(Image(url=image_file, alt_text=nodeitem.label + " node"))

        for part in doc_parts:
            # Input sockets
            if part.startswith("input "):
                if not has_inputs:
                    has_inputs = True
                    Document.add(Paragraph(Bold("Inputs:")))
                    Document.add(UnorderedList(input_list))

                socket_name, description = part[6:].split(":", 1)
                description = " ".join(description.split()).replace("\n", "")
                input_list.append(f"{InlineCode(socket_name)}: {description}")

            # Output sockets
            elif part.startswith("output "):
                if not has_outputs:
                    has_outputs = True
                    Document.add(Paragraph(Bold("Outputs:")))
                    Document.add(UnorderedList(output_list))

                socket_name, description = part[7:].split(":", 1)
                description = " ".join(description.split()).replace("\n", "")
                output_list.append(f"{InlineCode(socket_name)}: {description}")

            # Other UI options
            elif part.startswith("option "):
                if not has_options:
                    has_options = True
                    Document.add(Paragraph(Bold("Options:")))
                    Document.add(UnorderedList(option_list))

                option_name, description = part[7:].split(":", 1)
                description = " ".join(description.split()).replace("\n", "")
                option_list.append(f"{InlineCode(option_name)}: {description}")

            elif part.startswith("deprecated "):
                alternatives, message = part[11:].split(":", 1)

                message = " ".join(message.split()).replace("\n", "")
                if not message.endswith(".") and not message == "":
                    message += "."

                links = []
                for alternative in alternatives.split(","):
                    if alternative == "":
                        continue
                    links.append(str(make_node_link(alternative)))

                if len(links) > 0:
                    alternatives = f"Please use the following node(s) instead: {', '.join(links)}."
                    message = alternatives + " " + message

                deprecation_note.content = Quote(f"{Bold('DEPRECATED.')} This node is deprecated and will be removed in future versions of Armory. {message}")

        # Link to sources
        node_file_py = "/".join(nodetype.__module__.split(".")[2:]) + ".py"
        node_file_hx = nodetype.bl_idname[2:] + ".hx"  # Discard LN prefix

        pylink = Link(label="Python", url=PY_NODE_DIR + node_file_py)
        hxlink = Link(label="Haxe", url=HX_NODE_DIR + node_file_hx)

        Document.add(Paragraph(f"{Bold('Sources:')} {pylink} | {hxlink}"))


def run():
    print("Generating documentation...")

    Document.add(Header("Logic Nodes Reference"))

    Document.add(Paragraph(Italic(
        "This document was generated automatically. Please do not edit this"
        " page directly, instead change the docstrings of the nodes in their"
        f" {Link(label='Python files', url='https://github.com/armory3d/armory/tree/master/blender/arm/logicnode')}"
        f" or the {Link(label='generator script', url='https://github.com/armory3d/armory_tools/blob/master/make_node_reference.py')}"
        f" and {Link(label='open a pull request', url='https://github.com/armory3d/armory/wiki/contribute#creating-a-pull-request')}."
        " Thank you for contributing to this reference!")))

    Document.add(Paragraph(Italic(f"This reference was built for {Bold(f'Armory {arm.props.arm_version}')}.")))

    Document.add(HorizontalRule())

    with HeaderSubLevel():
        Document.add(Header("Node Categories"))

        category_items: List[Node] = []

        for section, section_categories in arm_nodes.category_items.items():
            # Ignore empty sections ("default" e.g)
            if len(section_categories) > 0:
                category_items.append(Bold(section.capitalize()))
                category_items.append(UnorderedList([Link(c.name, get_anchor(c.name)) for c in section_categories]))

        Document.add(UnorderedList(category_items))

        for category in arm_nodes.get_all_categories():
            Document.add(Header(category.name))

            if category.description != "":
                Document.add(Paragraph(category.description))

            with HeaderSubLevel():
                # Sort nodes alphabetically and discard section order
                iterator = itertools.chain(category.get_all_nodes(), category.deprecated_nodes)
                for nodeitem in sorted(iterator, key=lambda n: n.label):
                    Document.add(Header(nodeitem.label))

                    generate_node_documentation(nodeitem, category)

    output_path = os.path.abspath(__file__)
    output_path = os.path.dirname(output_path)
    output_path = os.path.join(output_path, "reference.md")

    with open(output_path, "w") as out_file:
        out_file.write(Document.write())


if __name__ == "__main__":
    run()
