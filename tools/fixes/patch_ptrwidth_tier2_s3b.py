#!/usr/bin/env python3
"""patch_s3b.py -- the interface widenings that let stage 3's rewrites stand."""
import os, sys, shutil, datetime
ROOT="/home/deck/lena/.lena_cmr2/port/tree/CMR2Decomp"
STAMP=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
APPLY="--apply" in sys.argv
E=[
 ("Graphics.h","    static int m_unk0x0065fa38;","    static intptr_t m_unk0x0065fa38;","cached Texture* for the stage cache"),
 ("Graphics.cpp","int CGraphics::m_unk0x0065fa38;","intptr_t CGraphics::m_unk0x0065fa38;","definition"),
 ("Graphics.h","    static void ConfigureTextureStageBlendMode(int param1, int param2);","    static void ConfigureTextureStageBlendMode(int param1, intptr_t param2);","param2 is a Texture*"),
 ("Graphics.cpp","void CGraphics::ConfigureTextureStageBlendMode(int param1, int param2)","void CGraphics::ConfigureTextureStageBlendMode(int param1, intptr_t param2)","definition"),
 ("Graphics.h","    static void ApplyTextureStageChange(int param1, int param2);","    static void ApplyTextureStageChange(int param1, intptr_t param2);","param2 is a Texture*: 19 call sites pass one"),
 ("Graphics.cpp","void CGraphics::ApplyTextureStageChange(int param1, int param2)","void CGraphics::ApplyTextureStageChange(int param1, intptr_t param2)","definition"),
 ("Graphics.cpp","        m_pTextureManager->pD3D->SetTextureStageState(param1, D3DTSS_COLORARG2, (DWORD)pTexture);",
                 "        /* the original passes a nullable Texture* as the DWORD value; this branch is pTexture==NULL,\n           so the value is 0 on every target -- the cast only has to be legal */\n        m_pTextureManager->pD3D->SetTextureStageState(param1, D3DTSS_COLORARG2, (DWORD)(uintptr_t)pTexture);","in the NULL branch"),
 ("Graphics.cpp","        m_pTextureManager->pD3D->SetTextureStageState(param1, D3DTSS_ALPHAARG2, (DWORD)pTexture);",
                 "        m_pTextureManager->pD3D->SetTextureStageState(param1, D3DTSS_ALPHAARG2, (DWORD)(uintptr_t)pTexture);","same, ALPHAARG2"),
 ("Sprite.cpp","        CGraphics::ApplyTextureStageChange(0, (int)(q)->pTexture);","        CGraphics::ApplyTextureStageChange(0, (intptr_t)(q)->pTexture);","QUAD2D_SET_STATE macro -- 15 macro sites hang off this one line"),
]
SOUND=[("        mmr = acmFormatEnum(had, &afd, AcmFormatEnumCallback, (DWORD)pFind, 0);",
        "        mmr = acmFormatEnum(had, &afd, AcmFormatEnumCallback, (DWORD_PTR)pFind, 0);"),
       ("    if (acmDriverEnum(AcmDriverEnumCallback, (DWORD)&find, 0) != 0)",
        "    if (acmDriverEnum(AcmDriverEnumCallback, (DWORD_PTR)&find, 0) != 0)"),
       ("        mmr = acmFormatEnum(had, &afd, AcmFormatEnumCallback, (DWORD)&find, 0);",
        "        mmr = acmFormatEnum(had, &afd, AcmFormatEnumCallback, (DWORD_PTR)&find, 0);")]
E += [("Sound.cpp", o, n, "the shim declares this dwInstance parameter as DWORD_PTR") for o, n in SOUND]
for f, old, new, why in E:
    p=os.path.join(ROOT,f); s=open(p,errors="replace").read(); n=s.count(old)
    if n!=1:
        print(f"  !!! {f}: expected 1 occurrence, found {n}: {old[:70]!r}"); continue
    if APPLY:
        if not os.path.exists(p+".bak-S3B-"+STAMP): shutil.copy2(p,p+".bak-S3B-"+STAMP)
        open(p,"w").write(s.replace(old,new))
    print(f"  {'applied' if APPLY else 'WOULD'} {f}: {why}")
