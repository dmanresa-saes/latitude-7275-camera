import sys,glob
f=sorted(glob.glob(sys.argv[1]+'/*.nv12'))[-1]; d=open(f,'rb').read(); W,H=1280,720; Y=d[:W*H]; UV=d[W*H:]
def reg(x0,x1,y0,y1):
    ys=[Y[y*W+x] for y in range(y0,y1) for x in range(x0,x1)]
    us=[UV[(y//2)*W+(x//2)*2] for y in range(y0,y1,2) for x in range(x0,x1,2)]
    vs=[UV[(y//2)*W+(x//2)*2+1] for y in range(y0,y1,2) for x in range(x0,x1,2)]
    return round(sum(ys)/len(ys)), round(sum(us)/len(us)), round(sum(vs)/len(vs))
print('pared Y/U/V =', reg(950,1250,60,160), ' puerta Y/U/V =', reg(450,700,300,500), ' silla Y/U/V =', reg(400,600,560,700))
