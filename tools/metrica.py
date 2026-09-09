#!/usr/bin/env python3
"""Metricas globales de un .nv12: Y media, croma media |U-128|+|V-128|, y nitidez (sigma del laplaciano de Y,
submuestreado). Uso: metrica.py ANCHO ALTO f.nv12 [...]"""
import sys
w, h = int(sys.argv[1]), int(sys.argv[2])
for f in sys.argv[3:]:
    d = open(f, 'rb').read(); y = d[:w*h]; uv = d[w*h:w*h + w*h//2]
    ymean = sum(y) / (w*h)
    c = sum(abs(uv[i]-128) + abs(uv[i+1]-128) for i in range(0, len(uv), 2)) / (len(uv)//2)
    lap = []
    for r in range(8, h-8, 4):
        row = r*w
        for x in range(8, w-8, 4):
            lap.append(4*y[row+x] - y[row+x-1] - y[row+x+1] - y[row-w+x] - y[row+w+x])
    m = sum(lap)/len(lap); sig = (sum((v-m)**2 for v in lap)/len(lap))**0.5
    print(f"{f}: Ymedia={ymean:.1f} croma={c:.2f} nitidez(sigma lap)={sig:.2f}")
