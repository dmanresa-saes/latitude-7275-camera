import sys,re
# lee lineas "y=N  G:R/B ..." y estima el pedestal p con dos zonas neutras: pared (y=2,x=8) y silla (y=10,x=11)
Z={}
for line in open(sys.argv[1]):
    m=re.match(r'\s*y=(\d+)\s+(.*)',line)
    if not m: continue
    y=int(m.group(1)); cells=re.findall(r'(\d+):([\d.]+)/([\d.]+)',m.group(2))
    for x,(g,r,b) in enumerate(cells): Z[(y,x)]=(float(g),float(r),float(b))
def est(w,c):
    Gw,rw,bw=Z[w]; Gc,rc,bc=Z[c]; Rw,Bw,Rc,Bc=rw*Gw,bw*Gw,rc*Gc,bc*Gc
    pr=(Rw*Gc-Rc*Gw)/((Rw-Rc)-(Gw-Gc)) if ((Rw-Rc)-(Gw-Gc))!=0 else float('nan')
    pb=(Bw*Gc-Bc*Gw)/((Bw-Bc)-(Gw-Gc)) if ((Bw-Bc)-(Gw-Gc))!=0 else float('nan')
    return Gw,rw,bw,Gc,rc,bc,pr,pb
for w,c in (((2,8),(10,11)),((2,7),(10,12)),((1,9),(9,11))):
    Gw,rw,bw,Gc,rc,bc,pr,pb=est(w,c)
    print('  pared%s G=%.0f %.2f/%.2f  silla%s G=%.0f %.2f/%.2f  -> pedestal p_r=%.1f p_b=%.1f'%(w,Gw,rw,bw,c,Gc,rc,bc,pr,pb))
