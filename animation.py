def stack():
    target = None
    for image in gimp.image_list():
        pdb.gimp_selection_none(image)
        if image.layers:
            if not target:
                target = image
            else:
                for layer in image.layers:
                    pdb.gimp_edit_cut(layer)
                    floating = pdb.gimp_edit_paste(target.layers[0], True)
                    pdb.gimp_floating_sel_to_layer(floating)


def bc():
    brightness = 0
    contrast = 0.5
    image = gimp.image_list()[0]
    for layer in image.layers:
        pdb.gimp_drawable_brightness_contrast(layer, brightness, contrast)


def nobox():
    image = gimp.image_list()[0]
    for layer in image.layers:
        layer.add_alpha()
        pdb.gimp_image_select_contiguous_color(image, 2, layer, 0, 0)
        pdb.gimp_edit_clear(layer)


def sort():
    image = gimp.image_list()[0]
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


def frame(name=None):
    if isinstance(name, int):
        name = str(name)
    image = gimp.image_list()[0]
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


def showall():
    image = gimp.image_list()[0]
    for layer in image.layers:
        layer.visible = True


def mirror():
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


def png(prefix=None):
    image = gimp.image_list()[0]
    if not prefix:
        filename = pdb.gimp_image_get_filename(image)
        prefix = filename[:-4] + "_"
    for layer in image.layers:
        try:
            filename = "{}{:02d}.png".format(prefix, int(layer.name))
        except ValueError:
            filename = "{}{}.png".format(prefix, layer.name)
        print("Exporting layer {} to {}".format(layer.name, filename))
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


