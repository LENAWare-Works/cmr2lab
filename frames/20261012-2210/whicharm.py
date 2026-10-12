import struct, zlib
def px(p):
    d=open(p,'rb').read()
    if d.startswith(b'\x89PNG'):
        i=8; idat=b''
        while i<len(d):
            ln=struct.unpack('>I',d[i:i+4])[0]; typ=d[i+4:i+8]; dat=d[i+8:i+8+ln]
            if typ==b'IHDR': w,h=struct.unpack('>II',dat[:8])
            if typ==b'IDAT': idat+=dat
            i+=12+ln
        raw=zlib.decompress(idat)
        return w,h,b''.join(raw[y*(w*3+1)+1:(y+1)*(w*3+1)] for y in range(h))
    f=[];i=2
    while len(f)<3:
        while d[i:i+1].isspace(): i+=1
        if d[i:i+1]==b'#':
            while d[i:i+1]!=b'\n': i+=1
            continue
        j=i
        while not d[j:j+1].isspace(): j+=1
        f.append(int(d[i:j])); i=j
    i+=1; w,h,_=f
    return w,h,d[i:i+w*h*3]
for fr in (3000,3500,4000):
    png=f"PLAYABLE-20261012/png/installed-build.{fr}.png"
    try: W,H,A=px(png)
    except Exception as e: print(fr,"no png",e); continue
    for arm in ("v2","v3"):
        try: w,h,B=px(f"PLAYABLE-20261012/shots/{arm}.ppm.{fr}")
        except Exception: print(fr,arm,"missing"); continue
        if (w,h)!=(W,H): print(fr,arm,"size"); continue
        n=sum(1 for k in range(0,len(A),3) if A[k:k+3]!=B[k:k+3])
        print(f"installed-build.{fr}.png vs {arm}.ppm.{fr}: {n} px differ ({100.0*n/(W*H):.4f}%)")
