The PNG is `frames/opt-preview-camera_20261011-0923_menucar-ABSENT.png` — a real 1280x800
capture of the option-preview screen from the instrumented run (source
`work/MENU-CAR-FLATTENED/frames/md_raw.003.ppm`, taken 1 s after a MENUDRAW burst fired,
`out/md_raw.log`). Its name is the honest one: it is the *screen*, and the car is **not in it**.
Measured on it: 31,389 distinct colours; sampled over 49,105 px, 0.75 % have a horizontal
gradient > 60 and every one of those sits in the bottom HUD band (rows 600-799) or rows 0-199,
while rows 200-599 are edge-free — i.e. a dithered sky/ground gradient with no object in it.
The owner map on the same frames says `0/2560 cells owned (0.0 % of the frame) by 0 textures`,
while the instrument prints 7 mesh parts per frame. This is the "submitted, covering nothing"
state, not a picture of a mangled car; a picture of the *mangled* car still does not exist in
this project and I am not going to label a gradient as one.
