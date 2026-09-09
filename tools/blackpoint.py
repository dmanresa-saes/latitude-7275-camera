#!/usr/bin/env python3
"""Punto negro de un .nv12 (sin numpy): percentiles de Y, media de Y y croma media de los pixeles mas oscuros.
Uso: blackpoint.py ANCHO ALTO fichero.nv12 [mas ficheros]"""
import sys
w, h = int(sys.argv[1]), int(sys.argv[2])
for f in sys.argv[3:]:
    d = open(f, 'rb').read()
    y = d[:w*h]; uv = d[w*h:w*h + w*h//2]
    ys = sorted(y); n = len(ys)
    pct = lambda p: ys[min(n-1, int(n*p/100))]
    p1 = pct(1)
    su = sv = c = 0
    # croma de los pixeles oscuros, muestreando a la rejilla de croma (2x2)
    for r in range(0, h, 2):
        row = r*w; crow = (r//2)*w
        for x in range(0, w, 2):
            if y[row+x] <= p1:
                su += uv[crow+x]; sv += uv[crow+x+1]; c += 1
    print(f"{f}: Ymin={ys[0]} p0.1={pct(0.1)} p1={p1} p5={pct(5)} p10={pct(10)} p25={pct(25)} med={pct(50)} p75={pct(75)} p90={pct(90)} Ymedio={sum(y)/n:.1f}  U/V oscuro={su/max(c,1):.1f}/{sv/max(c,1):.1f} (n={c})")
