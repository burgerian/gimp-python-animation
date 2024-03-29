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

YEAR = "2021"
COPYRIGHT = "Anthony Hayward " + YEAR + ".  LGPL License"

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
    image_size = (image.width, image.height)
    for layer in image.layers:
        if not pdb.gimp_drawable_has_alpha(layer):
            layer.add_alpha()
        if layer.offsets != (0, 0) or (layer.width, layer.height) != image_size:
            pdb.gimp_layer_resize_to_image_size(layer)
        (xmax, ymax) = (image.width - 1, image.height - 1)
        for (x, y) in [(0, 0), (xmax, 0), (0, ymax), (xmax, ymax)]:
            _num_channels, pixel = pdb.gimp_drawable_get_pixel(layer, x, y)
            if all(p > 240 for p in pixel):
                pdb.gimp_image_select_contiguous_color(image, 2, layer, x, y)
                pdb.gimp_edit_clear(layer)


def add_alpha(image=None):
    if not image:
        image = gimp.image_list()[0]
    image_size = (image.width, image.height)
    for layer in image.layers:
        if not pdb.gimp_drawable_has_alpha(layer):
            layer.add_alpha()
        if layer.offsets != (0, 0) or (layer.width, layer.height) != image_size:
            pdb.gimp_layer_resize_to_image_size(layer)


def sort(image=None):
    if not image:
        image = gimp.image_list()[0]
    image_size = (image.width, image.height)
    for layer in image.layers:
        if layer.offsets != (0, 0) or (layer.width, layer.height) != image_size:
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


def all_layers_to_image_size(image=None):
    if not image:
        image = gimp.image_list()[0]
    image_size = (image.width, image.height)
    for layer in image.layers:
        if layer.offsets != (0, 0) or (layer.width, layer.height) != image_size:
            pdb.gimp_layer_resize_to_image_size(layer)


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
    for layer in image.layers:
        layer.name = "was " + layer.name  # avoid duplicate names if a layer is already called "1"
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
    image_filename = pdb.gimp_image_get_filename(image)
    if not image_filename:
        gimp.message("Save image as xcf first!")
        return
    prefix = image_filename[:-4] + "_"
    gimp.progress_init("Save frames as {}_*.png".format(prefix))
    image_size = (image.width, image.height)
    for (layer_index, layer) in enumerate(image.layers):
        if layer.offsets != (0, 0) or (layer.width, layer.height) != image_size:
            pdb.gimp_layer_resize_to_image_size(layer)
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
    image_filename = pdb.gimp_image_get_filename(image)
    if not image_filename:
        gimp.message("Save image as xcf first!")
        return
    file_path = image_filename[:-4]
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


def sheet(image=None, cols=0):
    if not image:
        image = gimp.image_list()[0]
    if not cols:
        best = (1, 10000000)
        for cols in range(1, len(image.layers) + 1):
            rows = (len(image.layers) + (cols - 1)) // cols
            (sheet_width, sheet_height) = (cols * image.width, rows * image.height)
            sheet_aspect_ratio = sheet_width / sheet_height if sheet_width > sheet_height else sheet_height / sheet_width
            if sheet_aspect_ratio < best[1]:
                best = (cols, sheet_aspect_ratio)
        cols = best[0]
    image_filename = pdb.gimp_image_get_filename(image)
    if not image_filename:
        gimp.message("Save image as xcf first!")
        return
    file_path = "{}_sheet_{}_frames_{}_columns_{}x{}.png".format(
        image_filename[:-4], len(image.layers), cols, image.width, image.height)
    gimp.progress_init("Save sheet as {}".format(file_path))
    rows = (len(image.layers) + (cols - 1)) // cols
    sheet = pdb.gimp_image_new(image.width * cols, image.height * rows, 0)
    try:
        sheet_layer = pdb.gimp_layer_new(
            sheet, sheet.width, sheet.height,
            1, # type = RGBA-IMAGE
            "sprite sheet",
            100, # opacity = 100 %
            0 # mode = LAYER-MODE-NORMAL-LEGACY
        )
        pdb.gimp_image_insert_layer(sheet, sheet_layer, None, 0)

        (row, col) = (0, 0)
        for (layer_index, layer) in enumerate(image.layers):
            pdb.gimp_selection_none(image)
            pdb.gimp_layer_resize_to_image_size(layer)
            pdb.gimp_edit_copy(layer)
            floating = pdb.gimp_edit_paste(sheet_layer, True)
            (left, top) = floating.offsets
            pdb.gimp_layer_translate(floating, col * image.width - left, row * image.height - top)
            pdb.gimp_floating_sel_anchor(floating)
            col += 1
            if col >= cols:
                col = 0
                row += 1
            gimp.progress_update(100 * (layer_index + 1) / len(image.layers))
        pdb.file_png_save(
            sheet, sheet_layer,
            file_path, None,
            True, # interlace
            9, # compression
            True, # bkgd
            True, # gama
            True, # offs
            True, # phys
            True, # time
        )
        gimp.message("All frames saved as {}".format(file_path))
    finally:
        pdb.gimp_image_delete(sheet)


def reverse(image=None):
    if not image:
        image = gimp.image_list()[0]
    layer_count = len(image.layers)
    for i in range(0, layer_count - 1):
        l = image.layers[0]
        for j in range(i, layer_count - 1):
            pdb.gimp_image_lower_item(image, l)
    renumber(image)


gimpfu.register(
    "python_animation_helper_stack",
    "Stack all layers from all other images onto the current image",
    "Plugin to stack all layers from all other images onto the current image.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
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
    "Adjust brightness and contrast on all layers.",
    "Plugin to increase contrast on all layers of the current image.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "Brightness/contrast on all layers",
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
    "Add alpha channel to all layers and remove bounding white box (e.g. the piece of paper it was drawn on)",
    "Plugin to add alpha channel to all layers and remove bounding white box in the current image.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "Cut out",
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
    "python_animation_helper_add_alpha",
    "Add alpha channel to all layers, and resize to image size.",
    "Plugin to add alpha channel to all layers.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "Add alpha channel to all layers",
    "*",
	# input parameters. Same count and order as for plugin_func parameters
    [
		(gimpfu.PF_IMAGE, "image", "Image to modify", None), # type, name, description, default
    ],
    [],
    add_alpha,
    menu="<Image>/Filters/Animation",
)


gimpfu.register(
    "python_animation_helper_sort",
    "Set all layers to image size and sort by name",
    "Plugin to set all layers to image size and sort by name.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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
    "Mirror frame sequence (repeat frames in reverse order)",
    "Plugin to repeat frames in reverse order (mirror)",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "Mirror frame sequence (repeat in reverse order)",
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
    COPYRIGHT,
    YEAR,
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
    COPYRIGHT,
    YEAR,
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

gimpfu.register(
    "python_animation_helper_sheet",
    "Save frames as sprite sheet",
    "Plugin to save frames as a sprite sheet PNG image",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "Export as sprite sheet",
    "*",
	# input parameters. Same count and order as for plugin_func parameters
    [
		(gimpfu.PF_IMAGE, "image", "Image", None), # type, name, description, default
        (gimpfu.PF_INT, "cols", "Number of columns (0 for square sheet)", 0)
    ],
    [],
    sheet,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_all_layers_to_image_size",
    "All layers to image size",
    "Plugin to resize all layers to image size.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "All layers to image size",
    "*",
	# input parameters. Same count and order as for plugin_func parameters
    [
		(gimpfu.PF_IMAGE, "target", "Image to modify", None), # type, name, description, default
    ],
    [],
    all_layers_to_image_size,
    menu="<Image>/Filters/Animation",
)

gimpfu.register(
    "python_animation_helper_reverse",
    "Reverse",
    "Plugin to reverse the frame order.",
    "Anthony Hayward",
    COPYRIGHT,
    YEAR,
    "Reverse",
    "*",
	# input parameters. Same count and order as for plugin_func parameters
    [
		(gimpfu.PF_IMAGE, "target", "Image to modify", None), # type, name, description, default
    ],
    [],
    reverse,
    menu="<Image>/Filters/Animation",
)


gimpfu.main()
