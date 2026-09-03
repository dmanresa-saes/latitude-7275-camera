import sys,glob
f=sorted(glob.glob(sys.argv[1]+'/*.nv12'))[-1]; d=open(f,'rb').read(); W,H=1280,720; Y=d[:W*H]; UV=d[W*H:]
def reg(x0,x1,y0,y1):
    ys=[Y[y*W+x] for y in range(y0,y1,2) for x in range(x0,x1,2)]
    us=[UV[(y//2)*W+(x//2)*2] for y in range(y0,y1,2) for x in range(x0,x1,2)]
    vs=[UV[(y//2)*W+(x//2)*2+1] for y in range(y0,y1,2) for x in range(x0,x1,2)]
    return (round(sum(ys)/len(ys)), round(sum(us)/len(us)), round(sum(vs)/len(vs)))
print('  techo izq %s  techo centro %s  techo der %s  esq sup der %s  pared der medio %s' % (reg(20,200,0,60), reg(550,730,0,60), reg(1080,1260,0,60), reg(1180,1280,0,40), reg(1180,1280,300,420)))
