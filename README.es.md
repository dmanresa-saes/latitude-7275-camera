# Cámara del Dell Latitude 7275 en Linux (Intel IPU3 + OV5670)

Cámara frontal del Dell Latitude 7275 (Skylake, Intel IPU3 `8086:1919` /
CIO2 `8086:9d32`, sensor OmniVision OV5670, PMIC TI TPS68470) funcionando en
libcamera con el ISP por hardware del ImgU y la **calibración OEM del módulo
de cámara extraída del driver de Windows de Dell**.

| pieza | estado |
|---|---|
| PMIC TPS68470 | board data añadida al kernel (parche en `patches/`) |
| Sensor OV5670 | driver mainline, enlaza en I2C4 con `acpi_enforce_resources=lax` |
| ISP (ImgU) | libcamera, pipeline `ipu3`, 1280x720 a 30 fps, ~1 W, 9 % de un hilo |
| Color | matrices, punto blanco, nivel de negro y **lens shading** del `.cpf` de Dell |
| Nitidez | máscara de enfoque del bloque IEFD (el único con acelerador activo en el firmware) |
| Chrome | `libcamerify chrome` |

## Qué aporta

1. **Kernel**: entrada DMI del Latitude 7275 en `tps68470_board_data.c`
   (reutiliza la del Latitude 7212; solo cambia el nombre del dispositivo
   I2C del PMIC). No está en mainline.
2. **libcamera, IPA de ipu3** (`patches/libcamera-0.7.0-ipu3-ccm-oem.patch`):
   - `Ccm`: matriz de color interpolada por temperatura (portado de rkisp1).
   - `Lsc`: lens shading en el bloque SHD del ImgU. Formato de la LUT
     descubierto experimentalmente: entradas de 12 bits, ganancia
     `1 + v / 2^(10 - gain_factor)`.
   - `Saturation`: control de la tabla de ganancia de croma del bloque TCC,
     que el driver activa de serie con hasta 1,5x.
   - `Sharpness`: realce por el bloque IEFD (máscara de enfoque y realce
     direccional). El bloque Y_EE_NR no sirve: ningún binario del firmware
     activa su acelerador (`yuvp1_b0_acc`), comprobado con `tools/fwdump.c`.
   - `Awb`: curva de punto blanco OEM para estimar la temperatura,
     `gainCorrection`, `minGreenLevel`, `statsOffset`, ayudas de tuning.
   - `BlackLevelCorrection`: `blackLevel` configurable. El obgrid del ImgU va
     en medios LSB de 10 bits: el 64 del sensor se escribe como 128.
   - `ToneMapping`: gamma configurable (el firmware del modo vídeo la ignora).
   - `Agc`: corregido el cruce de ganancias verde/azul en la estimación de
     luminancia.
3. **`tools/decode_cpf_sky.py`**: decodifica los ficheros de tuning Intel
   CPFF "planos" de la era Skylake (`OV5670_<modulo>_SKY.cpf` del paquete
   Dell *Intel 2D Imaging Driver* 30.10154.6618.148): matrices de color por
   iluminante, cromaticidad, nivel de negro, lens shading. El módulo de cada
   equipo lo dice la ACPI: `\_SB.PCI0.LNK2._DDN` (aquí `4BF523T2`).
   Estructuras según los headers públicos de Intel en
   `intel/ipu6-camera-bins` (`ia_cmc_types.h`).

## Lo que no se pudo

- **Gamma**: el firmware ignora la LUT de gamma en modo vídeo (aplica una
  curva fija). El brillo se ajusta con el objetivo del AGC. El modo foto del
  ImgU aborta con libcamera.
- **Nitidez**: solo el IEFD responde; con la máscara al máximo la métrica de
  borde llega a 13 frente a 32 en Windows (que también dobla el ruido).
- Las secciones LAIQ/LISP del `.cpf` (tuning del 3A e ISP de Intel) son para
  binarios propietarios; no se usan.

## Nota sobre la calibración

`config/ov5670.yaml` contiene números derivados de la calibración propietaria
de Dell/Intel para el módulo 4BF523T2. El código es LGPL-2.1+ (libcamera) y
GPL-2.0 (kernel); los datos de calibración tienen la misma consideración que
en otros proyectos que reutilizan tuning OEM.

Detalles, medidas y procedimiento en `docs/` y en las herramientas de
`tools/` (`medir.py`, `yuv.py`, `esquinas.py`, `pedestal.py`, `nitidez.py`).
