def stack():
    target = None
    for i in gimp.image_list():
        if i.layers:
            if not target:
                target = i
            else:
                for layer in i.layers:
                    layer.add_alpha()
                    pdb.gimp_edit_cut(layer)
                    floating = pdb.gimp_edit_paste(target.layers[0], True)
                    pdb.gimp_floating_sel_to_layer(floating)

def bc():
    brightness = 0
    contrast = 0.5
    i = gimp.image_list()[0]    
    for layer in i.layers:
        pdb.gimp_drawable_brightness_contrast(layer, brightness, contrast)

def nobox():
    i = gimp.image_list()[0]
    for layer in i.layers:
        layer.add_alpha()
        pdb.gimp_image_select_contiguous_color(i, 2, layer, 0, 0)
        pdb.gimp_edit_clear(layer)

def sort():
    i = gimp.image_list()[0]
    more = True
    while more:
        more = False
        for a, b in zip(i.layers, i.layers[1:]):
            move_down = False
            try:
                move_down = int(a.name) < int(b.name)
            except ValueError:
                move_down = a.name < b.name
            if move_down:
                pdb.gimp_image_lower_item(i, a)
                more = True
                break

def frame(name=None):
    if isinstance(name, int):
        name = str(name)
    i = gimp.image_list()[0]
    if name:
        for layer in i.layers:
            if layer.name == name:
                layer.visible = True
                pdb.gimp_image_set_active_layer(i, layer)
            else:
                layer.visible = False
    else:
        first = True
        for (layer_index, layer) in enumerate(i.layers):
            if first and (layer.visible or layer_index == len(i.layers) - 1):
                layer.visible = True
                pdb.gimp_image_set_active_layer(i, layer)
                first = False
            else:
                layer.visible = False

def mirror():
    i = gimp.image_list()[0]
    max_layer = 0
    for layer in i.layers:
        try:
            if int(layer.name) > max_layer:
                max_layer = int(layer.name)
        except ValueError:
            pass
    layers_to_reverse = i.layers[1:]
    for layer in layers_to_reverse:
        pdb.gimp_edit_copy(layer)
        floating = pdb.gimp_edit_paste(i.layers[0], True)
        pdb.gimp_floating_sel_to_layer(floating)
        max_layer += 1
        floating.name = str(max_layer)


