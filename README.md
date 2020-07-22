# Gimp-Python scripts for animation

## Introduction

GIMP is a good tool for animation, but it can be quite laborious to use it, involving a lot of repetitive clicks.  This project contains code written for GIMP's python-fu feature that helps to speed up various animation tasks.

## Compatibility

Tested with GIMP 2.10.12 on Windows.  No plugins or extra software needed.

GIMP = GNU Image Manipulation Program, an open source graphics editor, available for free download at https://www.gimp.org/downloads/.

## GIMP Setup

The process assumes you don't have any other images open in GIMP apart from the images related to the animation, so close anything else you have open before starting.

You will need the following GIMP dialogs open all the time:

- Filters > Python-fu > Console (a separate window from the main GIMP window)
- Windows > Dockable Dialogs > Undo History (a dialog shown within the main GIMP window)
- Windows > Dockable Dialogs > Layers (a dialog shown within the main GIMP window)

Copy/paste the code from [animation.py](animation.py) into the Python-fu console.  This will define functions, but not run them, so it won't make any changes to your images yet.  Keep the Python-fu console open throughout the whole process - you can switch between the console and the main GIMP window as required.  If you close it by mistake, just open it again and copy/paste [animation.py](animation.py) again.

If you don't like the result of any script operation, use GIMP's Undo History and click above the list of changes made by the script to reverse its effect.

## Process

These scripts are designed to help get animations that have been drawn on multiple bits of paper into GIMP as multiple layers within a single image, from where they can be exported as an animated GIF, or as separate images or a sprite grid for use in a game.

Of course, you can adapt this process and modify your copy of the Python code to suit your specific needs.

### Draw, scan and save

1. Draw animation frames on paper.  Write a frame number on each frame so you can keep track of them.
2. Scan each piece of paper into GIMP using "File > Create > From Scanner/Camera..."  (as a colour picture).  Try to have the orientation the same for each piece of paper; it doesn't have to be correct, just the same for each image at this point.
3. Open the python-fu console "Filters > Python-fu > Console".
4. Run `stack()` in the Python-fu console.  All the images get combined into one image as layers.
5. Use "Image > Transform" to rotate the image to the correct orientation.
6. Use "Image > Scale" to scale the image to the pixel dimensions you want.  It's best if the image fits on your screen at 100% zoom.
7. Save the image (in GIMP's `.xcf` format).
8. File > Close All and discard changes.  This is necessary because the Python-fu can't close your other now-empty images for you.
9. Reopen the GIMP file you saved.

### Colour and outline

The scanned images often have poor contrast.  You can run the script `bc()` to apply Contrast + 50% to all layers.  You might want more sophisticated enhancement, e.g. apply a colour curve or GIMP's Cartoon filter (Filters > Artistic > Cartoon...) which can ink your outlines for you.  Unfortunately you'll need to apply these manually to each layer separately.  You can save colour curve presets, and make a note of Cartoon settings, to make sure you do it consistently.

If you have only drawn outlines, this is the time to colour in using GIMP's Flood Fill tool.

It's very easy to get confused between the top visible layer and the currently active (selected) layer.  You can run the Python `frame()` function to select the top visible layer and hide the rest.

### Split and align layers if required

If you have multiple frames drawn on each sheet of paper, it's now time to split them into multiple layers.

1. Right-click on each layer in the Layers dialog and select "Duplicate Layer" until you have as many copies of the layer as there are frames in the layer.
2. Rename each layer with the frame number that the layer will represent.  E.g. if you have three copies of a layer that contains frames 1, 2 and 3, then you will end up with three copies of that layer called "1", "2" and "3".  To rename a layer, click it in the Layer dialog and press F2.
3. Create guide lines (by dragging down and across from the ruler) that you can use to align your frames.
4. Go through each layer and use the Move tool to shift the whole layer to line up the frames.  To select a single layer, run the Python function `frame(1)` to activate layer 1, `frame(2)` to activate layer 2, etc. - this also hides all the other layers, to avoid confusion.
5. Select a rectangle that contains all frame contents, and the Image > Crop to Selection.
6. Go through each layer (using the `frame` function) and delete any mess around the edges, e.g. parts of other frames, using the usual GIMP drawing / selection tools.

### Sort frames

1. If you haven't already numbered the layers, rename each layer to have the frame number "1", "2" etc.  To rename a layer, click it in the Layer dialog (Windows > Dockable Dialogs > Layers) and press F2.
2. In the Python-fu console, run `sort()` to sort the frames from bottom to top.

### Preview animation

1. Click "Filters > Animation > Playback...".  The Playback dialog opens.
2. If your images are transparent, change "Cumulative layers (combine)" to "One frame per layer (replace)".  If your images have no transparency, the options are equivalent.
3. Press the play icon to see your animation.
4. Change the "1x" option to see your animation at a different playback rate.  (The "fps" option doesn't seem to have any effect for me).
5. Close the dialog when done.

### Save animation as animated GIF

1. Click File > Export As...
2. Enter a filename ending in `.gif` and click Export.
3. Tick "As Animation".  You probably want "Loop forever" to stay ticked.
4. Enter the Delay: 10 fps = 100 ms, 12.5 fps = 80 ms, 25 fps = 40 ms.
5. Select Frame Disposal "One frame per layer (replace)".
6. Tick the two boxes at the bottom to apply the same Delay and Disposal to all frames.
7. Click Export, and wait.
8. When done, open the `.gif` file in a web browser to see the result.

GIMP can't save movie files, so you'll need other software if you want your animation as `.avi`, `.mp4` etc.

### Save animation as separate frames

Run `png()` function.

You can also specify a path and filename root e.g. `png(r"C:\Users\me\Pictures\my_anim")` will save the layers as `my_anim_01.png`, `my_anim_02.png`, `my_anim_03.png` etc.

### Save animation as sprite map

TODO

### Remove box around frame (transparent edge)

Your scans will be full white rectangles with no transparency.  To add an Alpha Channel to your frames and delete the white edge around the outside, run Python function `nobox()`.

After removing the frame, run the Python function `showall()` to see all the frames overlaid on each other, then you can easily crop the image to a box that includes all the content in all the frames.


### Mirror the frames (reverse loop playback)

GIMP doesn't offer to reverse your animation when it's finished playing.  You can do this by copying each frame in reverse order, except the last one.  The Python function to do this is `mirror()`.

Note, the copied frame has no relationship to the original frame, so make sure any other editing is completed before doing this!  The copy gets a new incremental frame number that does not show its relationship to the original frame number.

