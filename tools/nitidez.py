import sys,glob
f=sorted(glob.glob(sys.argv[1]+'/*.nv12'))[-1]; d=open(f,'rb').read(); W,H=1280,720; Y=d[:W*H]
def lap_var(x0,x1,y0,y1):
    vals=[]
    for y in range(y0+1,y1-1):
        for x in range(x0+1,x1-1):
            c=Y[y*W+x]; l=4*c-Y[y*W+x-1]-Y[y*W+x+1]-Y[(y-1)*W+x]-Y[(y+1)*W+x]; vals.append(l)
    m=sum(vals)/len(vals); return (sum((v-m)**2 for v in vals)/len(vals))**0.5
def std(x0,x1,y0,y1):
    v=[Y[y*W+x] for y in range(y0,y1) for x in range(x0,x1)]; m=sum(v)/len(v); return m,(sum((a-m)**2 for a in v)/len(v))**0.5
mw,sw=std(1000,1240,80,160)
print('  nitidez (sigma laplaciano) papeles %.1f  puerta-borde %.1f | ruido pared: media %.0f sigma %.2f' % (lap_var(1060,1270,530,620), lap_var(560,620,200,600), mw, sw))
