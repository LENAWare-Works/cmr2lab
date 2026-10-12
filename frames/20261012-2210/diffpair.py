#!/usr/bin/env python3
"""Byte-level pair diff between two 1280x800 P6 PPMs. CPU only, no GPU."""
import sys, struct

def px(p):
    d = open(p,'rb').read()
    f=[]; i=2
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

frames = [2600,2900,3200,3500,4000,4500,5000]
print("frame  differ_px  %differ  maxdelta  mean_abs  identical")
for fr in frames:
    a=f"/home/deck/lena/work/FIXBOTH-20261012/shots/fx-b.ppm.{fr}"
    b=f"/home/deck/lena/work/FIXBOTH-20261012/shots/fx-d.ppm.{fr}"
    try:
        w1,h1,A=px(a); w2,h2,B=px(b)
    except Exception as e:
        print(f"{fr}   (missing: {e})"); continue
    if (w1,h1)!=(w2,h2): print(f"{fr}   size mismatch"); continue
    n=len(A); diff=0; maxd=0; tot=0
    for k in range(0,n,3):
        d1=abs(A[k]-B[k]); d2=abs(A[k+1]-B[k+1]); d3=abs(A[k+2]-B[k+2])
        m=max(d1,d2,d3)
        if m: diff+=1; tot+=d1+d2+d3
        if m>maxd: maxd=m
    npix=n//3
    print(f"{fr}  {diff:9d}  {100.0*diff/npix:6.2f}%  {maxd:8d}  {tot/npix/3:8.2f}  {'YES' if diff==0 else 'no'}")
