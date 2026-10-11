import sys,struct,os,glob
sys.path.insert(0,'/home/deck/lena/work/RACE')
import bfl

def sample_pt(gx,gy,w,h):
    u=(gx+0.5)/16.0; v=(gy+0.5)/16.0
    return int(u*w), int(v*h)   # matches floorf on non-negative

def block_px(blk,dxt5):
    """return list of 16 (r,g,b,a) in 4x4 raster order"""
    out=[]
    if dxt5:
        a0,a1=blk[0],blk[1]; abits=int.from_bytes(blk[2:8],'little')
        c0,c1=struct.unpack_from('<HH',blk,8); cbits=struct.unpack_from('<I',blk,12)[0]
        col=lambda c:(((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31)
        cols=[col(c0),col(c1)]
        if c0>c1: cols+=[tuple((2*cols[0][k]+cols[1][k])//3 for k in range(3)),tuple((cols[0][k]+2*cols[1][k])//3 for k in range(3))]
        else: cols+=[tuple((cols[0][k]+cols[1][k])//2 for k in range(3)),(0,0,0)]
        for py in range(4):
            for px in range(4):
                idx=(cbits>>(2*(4*py+px)))&3; ai=(abits>>(3*(4*py+px)))&7
                if ai==0: a=a0
                elif ai==1: a=a1
                elif a0>a1: a=((8-ai)*a0+(ai-1)*a1)//7
                else: a=((6-ai)*a0+(ai-1)*a1)//5 if ai<7 else 0
                out.append((cols[idx][0],cols[idx][1],cols[idx][2],a))
    else:
        c0,c1=struct.unpack_from('<HH',blk,0); cbits=struct.unpack_from('<I',blk,4)[0]
        col=lambda c:(((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31)
        cols=[col(c0),col(c1)]
        if c0>c1: cols+=[tuple((2*cols[0][k]+cols[1][k])//3 for k in range(3)),tuple((cols[0][k]+2*cols[1][k])//3 for k in range(3))]
        else: cols+=[tuple((cols[0][k]+cols[1][k])//2 for k in range(3)),(0,0,0)]
        for py in range(4):
            for px in range(4):
                idx=(cbits>>(2*(4*py+px)))&3
                a=0 if (c0<=c1 and idx==3) else 255
                out.append((cols[idx][0],cols[idx][1],cols[idx][2],a))
    return out

def lattice(blob,w,h,dxt5):
    bw=(w+3)//4
    pts=[sample_pt(gx,gy,w,h) for gy in range(16) for gx in range(16)]
    cache={}
    r=g=b=a=0;n=0;za=0;seen=set()
    for (x,y) in pts:
        bx,by=x//4,y//4
        key=(bx,by)
        if key not in cache:
            o=(by*bw+bx)*(16 if dxt5 else 8)
            blk=blob[o:o+(16 if dxt5 else 8)]
            if len(blk)<(16 if dxt5 else 8): cache[key]=None
            else: cache[key]=block_px(blk,dxt5)
        px=cache[key]
        if px is None: continue
        i=(y%4)*4+(x%4)
        pr,pg,pb,pa=px[i]
        r+=pr;g+=pg;b+=pb;a+=pa;n+=1
        if pa==0: za+=1
        if len(seen)<24: seen.add((pr,pg,pb,pa))
    if not n: return None
    return (r//n,g//n,b//n,a//n,za,len(seen))

PORT={35:(256,256,(13,13,12,207),48),36:(1024,1024,(100,94,101,253),1),
      37:(256,256,(51,50,50,207),48),38:(1024,1024,(100,94,101,253),1),
      39:(512,512,(31,30,35,204),0),40:(256,256,(22,22,21,187),60),
      41:(512,512,(85,66,69,204),0),42:(256,128,(54,56,52,255),0),
      43:(256,256,(41,19,3,0),256)}
files=[]
files+=sorted(glob.glob('/home/deck/lena/.lena_cmr2/game/Game/Cars/*.bfl'))
files+=sorted(glob.glob('/home/deck/lena/.lena_cmr2/game/FrontEnd/*.bfl'))
files+=sorted(glob.glob('/home/deck/lena/.lena_cmr2/game/Game/Tracks/*/*.bfl'))
print("files:",len(files))
best={k:[] for k in PORT}
for path in files:
    try:
        buf=bfl.load(path); es=bfl.entries(buf)
    except Exception as e:
        continue
    for fid,off,nlen,name,p in es:
        bl=bfl.blob(buf,off)
        if bl[:4]!=b'DDS ': continue
        (size,flags,h,w,pitch,depth,mips)=struct.unpack_from('<7I',bl,4)
        fcc=bl[0x54:0x58]
        if fcc not in (b'DXT5',b'DXT1'): continue
        dxt5=(fcc==b'DXT5')
        need=16 if dxt5 else 8
        if len(bl)<128+((w+3)//4)*((h+3)//4)*need: continue
        for k,(pw,ph,pm,pz) in PORT.items():
            if (w,h)!=(pw,ph): continue
            lm=lattice(bl[128:],w,h,dxt5)
            if not lm: continue
            d=sum(abs(lm[i]-pm[i]) for i in range(4))
            if d<=45:
                best[k].append((d,os.path.basename(path),name,lm))
for k in sorted(PORT):
    pw,ph,pm,pz=PORT[k]
    print("\nport id %d  %dx%d mean=(%d,%d,%d,%d) zeroAlpha=%d"%(k,pw,ph,pm[0],pm[1],pm[2],pm[3],pz))
    if not best[k]: print("   NO MATCH within 45 (sum abs diff over RGBA)")
    for d,f,nm,lm in sorted(best[k])[:4]:
        print("   d=%3d %-14s %-18s lattice=(%d,%d,%d,%d) za=%d distinct=%d"%(d,f,nm,lm[0],lm[1],lm[2],lm[3],lm[4],lm[5]))
