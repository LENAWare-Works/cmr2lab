#!/usr/bin/env python3
"""imagesweep.py -- read the header dimensions of every candidate file, to answer
"does file X exist on this disk" without a vision pass. Built 2026-10-11 for
ONE-WHEEL-FRAME. Feed it a file list (one path per line)."""

def dims(path):
    try:
        with open(path,'rb') as f:
            h=f.read(64)
            if h[:4]==b'\xff\xd8\xff':  # jpeg
                f.seek(2)
                while True:
                    b=f.read(2)
                    if len(b)<2 or b[0]!=0xFF: return None
                    m=b[1]
                    if m in (0xD8,0xD9,0x01) or 0xD0<=m<=0xD7: continue
                    ln=f.read(2)
                    if len(ln)<2: return None
                    L=struct.unpack('>H',ln)[0]
                    if m in (0xC0,0xC1,0xC2,0xC3,0xC5,0xC6,0xC7,0xC9,0xCA,0xCB,0xCD,0xCE,0xCF):
                        d=f.read(5)
                        if len(d)<5: return None
                        prec=d[0]; H,W=struct.unpack('>HH',d[1:5])
                        return ('JPEG',W,H)
                    f.seek(L-2,1)
            if h[:8]==b'\x89PNG\r\n\x1a\n':
                W,H=struct.unpack('>II',h[16:24]); return ('PNG',W,H)
            if h[:2]==b'BM':
                W,H=struct.unpack('<ii',h[18:26]); return ('BMP',abs(W),abs(H))
            if h[:4]==b'RIFF' and h[8:12]==b'WEBP':
                return ('WEBP',None,None)
            if h[:6] in (b'GIF87a',b'GIF89a'):
                W,H=struct.unpack('<HH',h[6:10]); return ('GIF',W,H)
            if h[:4] in (b'II*\x00',b'MM\x00*'):
                return ('TIFF',None,None)
            if h[:2]==b'P6' or h[:2]==b'P5':
                parts=h.split()
                return ('PNM',int(parts[1]),int(parts[2]))
    except Exception:
        return None
    return None

hits=[]
for line in open('/tmp/cl2.txt'):
    p=line.strip()
    if not p: continue
    d=dims(p)
    if d:
        hits.append((d,p))
print('image-like files scanned:',len(hits))
for d,p in hits:
    if d[1]==1355 or d[2]==1800 or (d[1] and 0.70<d[1]/d[2]<0.80):
        print('MATCH',d,p)
