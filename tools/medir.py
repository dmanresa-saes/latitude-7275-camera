import sys,glob,struct,zlib
f=sorted(glob.glob(sys.argv[1]+'/*.nv12'))[-1]; d=open(f,'rb').read(); W,H=1280,720; Y=d[:W*H]; UV=d[W*H:W*H*3//2]; rows=[]; px={}
for y in range(H):
    row=bytearray([0]); base=(y//2)*W
    for x in range(W):
        c=Y[y*W+x]-16; i=base+(x//2)*2; u=UV[i]-128; v=UV[i+1]-128
        r=max(0,min(255,int(1.164*c+1.596*v))); g=max(0,min(255,int(1.164*c-0.392*u-0.813*v))); b=max(0,min(255,int(1.164*c+2.017*u)))
        row+=bytes((r,g,b))
        if 950<=x<1250 and 60<=y<160: px.setdefault('pared',[]).append((r,g,b))
        if 450<=x<700 and 300<=y<500: px.setdefault('puerta',[]).append((r,g,b))
    rows.append(bytes(row))
def chunk(t,b): return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows),6))+chunk(b'IEND',b'')
open(sys.argv[2],'wb').write(png)
print(sys.argv[2], {k:tuple(round(sum(p[i] for p in v)/len(v)) for i in range(3)) for k,v in px.items()})
