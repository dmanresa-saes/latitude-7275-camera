#!/usr/bin/env python3
"""Decodifica el tuning OEM Intel CPFF 'plano' de la era Skylake (2015), p.ej.
OV5670_4BF523T2_SKY.cpf del driver Dell 'Intel 2D Imaging' 30.10154.6618.148.
Diferencias con los .aiqb del Surface (TGL): un solo contenedor AIQB tras la
cabecera CPFF de 0x20; cabecera AIQB de 0x18; cadena de records desde 0x38.
Record = size u32, fmt u8, key u8, name_id u16.
  nid 3  : nivel de negro por ganancia (Q8, 4 canales)
  nid 15 : cromaticidad del sensor por iluminante: 3 juegos (tipico/alto/bajo) x
           N x {CIE x, CIE y (Q16), R/G, B/G (Q10)}
  nid 10 : lens shading: 8 rejillas 41x31 (una por iluminante), 4 canales, Q12
           (4096 = 1.0). Con --lsc se vuelcan a <salida>_lsc.json.
  nid 18 : matrices de color: N x {tipo iluminante u32, R/G, B/G (Q8),
           CIE x, y (Q16), CCM 3x3 (Q16), CCM 3x3 'saturada' (Q16)}
Uso: ./decode_cpf_sky.py fichero.cpf [salida.json]
"""
import json, struct, sys
LS = {0:'none',1:'A/tungsteno',2:'B',3:'C',4:'D50',5:'D55',6:'D65',7:'D75',8:'E',9:'F1',10:'F2/coolwhite',
      11:'F3',12:'F4/warmwhite',13:'F5',14:'F6',15:'F7/D65sim',16:'F8',17:'F9',18:'F10',19:'F11/TL84',20:'F12'}
def cct(x, y):
    n = (x-0.3320)/(0.1858-y); return 449*n**3+3525*n**2+6823.3*n+5520.33
def records(d):
    off = 0x38
    while off+8 <= len(d):
        size, fmt, key, nid = struct.unpack_from('<IBBH', d, off)
        if size < 8: break
        yield nid, d[off+8:off+size]; off += size
def main():
    d = open(sys.argv[1],'rb').read(); assert d[:4]==b'CPFF' and d[0x20:0x24]==b'AIQB'
    R = {}
    for nid, body in records(d): R.setdefault(nid, []).append(body)
    out = {'fichero': sys.argv[1], 'comentario': R[1][0][:16].split(b'\0')[0].decode()}
    # nid 18: CCMs
    b = R[18][0]; n, = struct.unpack_from('<H', b, 0); p = 2; ccms = []
    for _ in range(n):
        src, rg, bg, x, y = struct.unpack_from('<IHHHH', b, p); p += 12
        m1 = [v/65536 for v in struct.unpack_from('<9i', b, p)]; p += 36
        m2 = [v/65536 for v in struct.unpack_from('<9i', b, p)]; p += 36
        ccms.append({'src': src, 'iluminante': LS.get(src, str(src)), 'cct': round(cct(x/65536, y/65536)),
                     'cie_x': round(x/65536,4), 'cie_y': round(y/65536,4), 'rpg': round(rg/256,4), 'bpg': round(bg/256,4),
                     'ccm': [round(v,4) for v in m1], 'ccm_sat': [round(v,4) for v in m2]})
    ccms.sort(key=lambda c: c['cct']); out['ccm'] = ccms
    # nid 15: curva de cromaticidad
    b = R[15][0]; n, = struct.unpack_from('<I', b, 0); sets = []
    for s in range(3):
        pts = []
        for i in range(n):
            x, y, rg, bg = struct.unpack_from('<HHHH', b, 4 + (s*n+i)*8)
            pts.append({'cct': round(cct(x/65536, y/65536)), 'cie_x': round(x/65536,4), 'cie_y': round(y/65536,4), 'rpg': round(rg/1024,4), 'bpg': round(bg/1024,4)})
        sets.append(pts)
    out['cromaticidad'] = {'tipico': sets[0], 'alto': sets[1], 'bajo': sets[2]}
    # nid 3: black level
    b = R[3][0]; n, = struct.unpack_from('<H', b, 0); bl = []
    for i in range(n):
        exp, gain, gr, r, bb, gb = struct.unpack_from('<IIHHHH', b, 4 + i*16)
        bl.append({'exposicion_us': exp, 'ganancia': round(gain/65536,3), 'gr': round(gr/256,2), 'r': round(r/256,2), 'b': round(bb/256,2), 'gb': round(gb/256,2)})
    out['nivel_negro_10bit'] = bl
    if 10 in R and '--lsc' in sys.argv:
        b = R[10][0]; ver, n, w, h = struct.unpack_from('<HHHH', b, 0); p = 8; grids = []
        for i in range(n):
            src, a, bb, c = struct.unpack_from('<HHHH', b, p); p += 8
            chans = [list(struct.unpack_from('<%dH' % (w*h), b, p + k*w*h*2)) for k in range(4)]; p += 4*w*h*2
            grids.append({'src': src, 'iluminante': LS.get(src, str(src)), 'ancho': w, 'alto': h, 'q': 12, 'canales': chans})
        out['lens_shading'] = {'nota': 'canales en orden de fichero (probablemente Gr,R,B,Gb), ganancia = valor/4096', 'rejillas': grids}
        print('LSC:', n, 'rejillas %dx%d Q12, ganancia maxima en esquina %.2f' % (w, h, max(max(ch) for g in grids for ch in g['canales'])/4096))
    if len(sys.argv) > 2: json.dump(out, open(sys.argv[2],'w'), indent=1, ensure_ascii=False)
    print('CPF', out['comentario'], '| CCMs:', len(ccms), '| puntos cromaticidad:', len(sets[0]), '| black level entradas:', len(bl))
    print('%-14s %5s %6s %6s  CCM (filas)' % ('iluminante','CCT','R/G','B/G'))
    for c in ccms:
        m = c['ccm']; print('%-14s %5d %6.3f %6.3f  [%6.3f %6.3f %6.3f] [%6.3f %6.3f %6.3f] [%6.3f %6.3f %6.3f]' % (c['iluminante'], c['cct'], c['rpg'], c['bpg'], *m))
    print('curva cromaticidad (tipico):', ' '.join('%dK(%.3f,%.3f)' % (p['cct'], p['rpg'], p['bpg']) for p in sets[0]))
    print('nivel de negro: %.1f..%.1f (10 bit), %d entradas de ganancia %.0fx..%.0fx' % (min(v['gr'] for v in bl), max(v['gr'] for v in bl), len(bl), bl[0]['ganancia'], bl[-1]['ganancia']))
main()
