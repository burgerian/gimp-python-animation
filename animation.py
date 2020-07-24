# https://github.com/burgerian/gimp-python-animation

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
        (w, h) = (image.width - 1, image.height - 1)
        for (x, y) in [(0, 0), (w, 0), (0, h), (w, h)]:
            pdb.gimp_image_select_contiguous_color(image, 2, layer, x, y)
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
    for layer in image.layers:
        pdb.gimp_layer_resize_to_image_size(layer)


def number():
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


def renumber():
    image = gimp.image_list()[0]
    for (layer_index, layer) in enumerate(image.layers):
        layer.name = str(len(image.layers) - layer_index)


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

f = frame


def up():
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


def down():
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


def gif(ms=40, prefix=None):
    image = gimp.image_list()[0]
    if not prefix:
        filename = pdb.gimp_image_get_filename(image)
        prefix = filename[:-4]
    print("Preparing temporary image")
    image = pdb.gimp_image_duplicate(image)
    try:
        if pdb.gimp_image_base_type(image) != 2:
            print("Converting temporary image to indexed colour mode")
            pdb.gimp_image_convert_indexed(
                image,
                0, # dither-type=CONVERT-DITHER-NONE
                0, # palette-type=CONVERT-PALETTE-GENERATE
                255, # num-cols
                False, # alpha-dither
                False, # remove-unused
                "" # palette
            )
        filename = prefix + ".gif"
        print("Saving animated GIF as {}".format(filename))
        pdb.file_gif_save(
            image, image.layers[0],
            filename, filename,
            True, # interlace
            True, # loop
            ms, # default-delay
            2 # default-dispose
        )
    finally:
        pdb.gimp_image_delete(image)


