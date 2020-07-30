#!/usr/bin/env python
"""
Animation helper plugin for GIMP.

Written by Anthony Hayward.

Project homepage: https://github.com/burgerian/gimp-python-animation
"""

import gimpfu
from gimpfu import (
    gimp, pdb
)


def stack(target=None):
    for image in gimp.image_list():
        pdb.gimp_selection_none(image)
        if image.layers:
            if not target:
                target = image
            elif image != target:
                for layer in image.layers:
                    pdb.gimp_edit_cut(layer)
                    floating = pdb.gimp_edit_paste(target.layers[0], True)
                    pdb.gimp_floating_sel_to_layer(floating)


def bc(image=None, brightness=0, contrast=50):
    if not image:
        image = gimp.image_list()[0] 
    for layer in image.layers:
        pdb.gimp_drawable_brightness_contrast(layer, brightness / 100.0, contrast / 100.0)


def nobox(image=None):
    if not image:
        image = gimp.image_list()[0]
    pdb.gimp_context_set_sample_transparent(True)
    for layer in image.layers:
        layer.add_alpha()
        (w, h) = (image.width - 1, image.height - 1)
        for (x, y) in [(0, 0), (w, 0), (0, h), (w, h)]:
            pdb.gimp_image_select_contiguous_color(image, 2, layer, x, y)
            pdb.gimp_edit_clear(layer)


def sort(image=None):
    if not image:
        image = gimp.image_list()[0]
    for layer in image.layers:
        pdb.gimp_layer_resize_to_image_size(layer)
    more = True
    while more:
        more = False
        for a, b in zip(image.layers, image.layers[1:]):
            move_down = False
            try:
                move_down = int(a.name) < int(b.name)
            except ValueError:
                move_down = a.name < b.name
            if move_down:
                pdb.gimp_image_lower_item(image, a)
                more = True
                break


def number(image=None):
    if not image:
        image = gimp.image_list()[0]
    highest = 0
    unnumbered = 0
    for layer in image.layers:
        try:
            n = int(layer.name)
            if n > highest:
                highest = n
        except ValueError:
            unnumbered += 1
    v = highest + unnumbered
    for layer in image.layers:
        try:
            int(layer.name)
        except ValueError:
            layer.name = str(v)
            v -= 1


def renumber(image=None):
    if not image:
        image = gimp.image_list()[0]
    for (layer_index, layer) in enumerate(image.layers):
        layer.name = str(len(image.layers) - layer_index)


def frame(image=None, name=None):
    if not image:
        image = gimp.image_list()[0]
    if isinstance(name, int):
        name = str(name)
    if name:
        for layer in image.layers:
            if layer.name == name:
                layer.visible = True
                pdb.gimp_image_set_active_layer(image, layer)
            else:
                layer.visible = False
    else:
        first = True
        for (layer_index, layer) in enumerate(image.layers):
            if first and (layer.visible or layer_index == len(image.layers) - 1):
                layer.visible = True
                pdb.gimp_image_set_active_layer(image, layer)
                first = False
            else:
                layer.visible = False

f = frame


def up(image=None):
    if not image:
        image = gimp.image_list()[0]
    if not image.layers:
        return
    selected = False
    select_layer = None
    for layer in image.layers:
        if layer.visible:
            if not selected and select_layer:
                select_layer.visible = True
                pdb.gimp_image_set_active_layer(image, select_layer)
                selected = True
            layer.visible = False
        else:
            layer.visible = False
            if not selected:
                select_layer = layer
    if not selected:
        select_layer.visible = True
        pdb.gimp_image_set_active_layer(image, select_layer)


def down(image=None):
    if not image:
        image = gimp.image_list()[0]
    if not image.layers:
        return
    select_next = False
    selected = False
    for layer in image.layers:
        if select_next and not selected:
            layer.visible = True
            pdb.gimp_image_set_active_layer(image, layer)
            selected = True
        elif layer.visible:
            select_next = True
            layer.visible = False
    if not selected:
        layer = image.layers[0]
        layer.visible = True
        pdb.gimp_image_set_active_layer(image, layer)


def showall(image=None):
    if not image:
        image = gimp.image_list()[0]
    for layer in image.layers:
        layer.visible = True


def mirror(image=None):
    if not image:
        image = gimp.image_list()[0]
    max_layer = 0
    for layer in image.layers:
        try:
            if int(layer.name) > max_layer:
                max_layer = int(layer.name)
        except ValueError:
            pass
    layers_to_reverse = image.layers[1:]
    pdb.gimp_selection_none(image)
    for layer in layers_to_reverse:
        pdb.gimp_edit_copy(layer)
        floating = pdb.gimp_edit_paste(image.layers[0], True)
        pdb.gimp_floating_sel_to_layer(floating)
        max_layer += 1
        floating.name = str(max_layer)


def png(image=None):
    if not image:
        image = gimp.image_list()[0]
    prefix = pdb.gimp_image_get_filename(image)[:-4] + "_"
    gimp.progress_init("Save frames as {}_*.png".format(prefix))
    for (layer_index, layer) in enumerate(image.layers):
        try:
            filename = "{}{:02d}.png".format(prefix, int(layer.name))
        except ValueError:
            filename = "{}{}.png".format(prefix, layer.name)
        pdb.file_png_save(
            image, layer,
            filename, None,
            True, # interlace
            9, # compression
            True, # bkgd
            True, # gama
            True, # offs
            True, # phys
            True, # time
        )
        gimp.progress_update(100 * (layer_index + 1) / len(image.layers))
    gimp.message("All frames saved as {}_*.png".format(prefix))


def gif(image=None, suffix=None, fps=24):
    if not image:
        image = gimp.image_list()[0]
    file_path = pdb.gimp_image_get_filename(image)[:-4]
    if suffix:
        file_path += "_" + suffix.strip()
    file_path += ".gif"
    ms = int(1000.0 / fps)
    temp_image = False
    try:
        gimp.progress_init("Save animated GIF @ {} fps = {} ms/frame as {}".format(
            fps, ms, file_path))
        if pdb.gimp_image_base_type(image) != 2:
            temp_image = True
            image = pdb.gimp_image_duplicate(image)
            pdb.gimp_image_convert_indexed(
                image,
                0, # dither-type=CONVERT-DITHER-NONE
                0, # palette-type=CONVERT-PALETTE-GENERATE
                255, # num-cols
                False, # alpha-dither
                False, # remove-unused
                "" # palette
            )
            gimp.progress_update(50)
        pdb.file_gif_save(
            image, image.layers[0],
            file_path, file_path,
            True, # interlace
            True, # loop
            ms, # default-delay
            2 # default-dispose
        )
        gimp.progress_update(100)
        gimp.message("Saved animated GIF @ {} fps = {} ms/frame as {}".format(
            fps, ms, file_path))
    finally:
        if temp_image:
            pdb.gimp_image_delete(image)


gimpfu.register(
    "python_animation_helper_stack",
    "Stack all layers from all other images onto the current image",
    "Plugin to stack all layers from all other images onto the current image.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Stack all images onto this one",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "target", "Image to modify", None), # type, name, description, default
    ],
    [],
    stack,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_bc",
    r"Adjust brightness and contrast on all layers.",
    "Plugin to increase contrast on all layers of the current image.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    r"Brightness/contrast on all layers",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image to modify", None), # type, name, description, default
		(gimpfu.PF_SLIDER, "brightness", "Brightness", 0, (-50, 50, 1)),
		(gimpfu.PF_SLIDER, "contrast", "Contrast", 50, (-50, 50, 1)),
	],
	# output/return values
    [],
    bc,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_nobox",
    "Add alpha channel to all layers and remove bounding white box",
    "Plugin to add alpha channel to all layers and remove bounding white box in the current image.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Remove white box",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image to modify", None), # type, name, description, default
    ],
    [],
    nobox,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_sort",
    "Set all layers to image size and sort by name",
    "Plugin to set all layers to image size and sort by name.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Sort layers",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image to modify", None), # type, name, description, default
    ],
    [],
    sort,
    menu="<Image>/Filters/Animation",
)


gimpfu.register(
    "python_animation_helper_number",
    "Number unnumbered frames, bottom to top",
    "Plugin to number unnumbered frames, bottom to top.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Number unnumbered layers",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image to modify", None), # type, name, description, default
    ],
    [],
    number,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_renumber",
    "Number all frames, bottom to top",
    "Plugin to number all frames, bottom to top.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Renumber all layers",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image to modify", None), # type, name, description, default
    ],
    [],
    renumber,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_frame",
    "Focus on top visible frame",
    "Plugin to focus on top visible frame.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Solo layer: top visible",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
    ],
    [],
    frame,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_up",
    "Focus on previous frame",
    "Plugin to focus on previous frame.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    r"Solo layer /\ /\ /\ up",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
    ],
    [],
    up,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_down",
    "Focus on previous frame",
    "Plugin to focus on previous frame.",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    r"Solo layer \/ \/ \/ down",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
    ],
    [],
    down,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_showall",
    "Show all layers (piled up)",
    "Plugin to show all layers",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Show all layers",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
    ],
    [],
    showall,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_mirror",
    "Repeat frames in reverse order (mirror)",
    "Plugin to repeat frames in reverse order (mirror)",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Repeat frames backwards",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
    ],
    [],
    mirror,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_gif",
    "Save as animated GIF",
    "Plugin to save as animated GIF",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Export as animated GIF",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
        (gimpfu.PF_STRING, "suffix", "Suffix (to append to .xcf filename)", ""),
        (gimpfu.PF_SPINNER, "fps", "Frames per second", 24, (1, 60, 1)),
    ],
    [],
    gif,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_png",
    "Save frames as PNG images",
    "Plugin to save frames as PNG images",
    "Anthony Hayward",
    "Anthony Hayward 2020.  LGPL License",
    "2020",
    "Export each frame as PNG",
    "*",
	# input parameters. Same count and order as for plugin_func parameters 
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
    ],
    [],
    png,
    menu="<Image>/Filters/Animation",
)

gimpfu.main()
