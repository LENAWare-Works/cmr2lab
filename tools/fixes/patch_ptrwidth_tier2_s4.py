#!/usr/bin/env python3
"""patch_s4.py -- the second cluster of interface widening, all of it width-only
(no field's *interpretation* changes: every slot below is read back as a whole
pointer, never as an int)."""
import os, sys, shutil, datetime
ROOT="/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp"
STAMP=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
APPLY="--apply" in sys.argv
ALL = [
 # Sound_NoOpMusicCallback: takes the string/node pointer it is called with
 ("Sound.cpp",        "void Sound_NoOpMusicCallback(int unused)",  "void Sound_NoOpMusicCallback(intptr_t unused)", 1),
 ("Sound.cpp",        "void Sound_NoOpMusicCallback(int unused);", "void Sound_NoOpMusicCallback(intptr_t unused);", 2),
 ("SceneNode.cpp",    "void Sound_NoOpMusicCallback(int unused);", "void Sound_NoOpMusicCallback(intptr_t unused);", 1),
 ("StageObjects.cpp", "void Sound_NoOpMusicCallback(int unused);", "void Sound_NoOpMusicCallback(intptr_t unused);", 2),
 # the shadow-caster arrays: every read is a whole-slot pointer read
 ("SceneNode.cpp", "int g_sceneLightState[30];",  "intptr_t g_sceneLightState[30];", 1),
 ("SceneNode.cpp", "int g_sceneLightState2[10];", "intptr_t g_sceneLightState2[10];", 1),
 ("Graphics.cpp",  "extern int g_sceneLightState2[10];", "extern intptr_t g_sceneLightState2[10];", 1),
 # the collision candidate slot holds a pointer
 ("VehiclePhysics.cpp", "extern int g_unk0x00591948;", "extern intptr_t g_unk0x00591948;", 1),
 ("StageObjects.cpp",   "int g_unk0x00591948;",        "intptr_t g_unk0x00591948;", 1),
 # Quad2D::flags caches the tagged pDest pointer (Sprite.cpp:671-706)
 ("Sprite.cpp", "    unsigned int flags;     // 0x94", "    intptr_t flags;        // 0x94  tagged pDest pointer", 1),
 ("Sprite.cpp", "    unsigned int lastFlags;",         "    intptr_t lastFlags;", 1),
]
for f, old, new, want in ALL:
    p=os.path.join(ROOT,f); s=open(p,errors="replace").read(); n=s.count(old)
    if n!=want:
        print(f"  !!! {f}: expected {want}, found {n}: {old[:60]!r}"); continue
    if APPLY:
        if not os.path.exists(p+".bak-S4-"+STAMP): shutil.copy2(p,p+".bak-S4-"+STAMP)
        open(p,"w").write(s.replace(old,new))
    print(f"  {'applied' if APPLY else 'WOULD'} {f}: {old[:58]}")
