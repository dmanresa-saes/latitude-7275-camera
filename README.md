# Dell Latitude 7275 camera on Linux (Intel IPU3 + OmniVision OV5670)

The front camera of the Dell Latitude 7275 (Skylake, Intel IPU3 ImgU
`8086:1919` / CIO2 `8086:9d32`, OV5670 sensor, TI TPS68470 PMIC) working in
libcamera through the ImgU hardware ISP, with the **OEM calibration of the
camera module extracted from Dell's Windows driver**.

*Versión en castellano: [README.es.md](README.es.md).*

| piece | status |
|---|---|
| TPS68470 PMIC | board data added to the kernel driver (`patches/`) |
| OV5670 sensor | mainline driver, binds on I2C4 with `acpi_enforce_resources=lax` |
| ISP (ImgU) | libcamera `ipu3` pipeline, 1280x720 @ 30 fps, ~1 W, 9 % of one thread |
| colour | colour matrices, white point locus, black level and **lens shading** from Dell's `.cpf` |
| sharpness | unsharp mask of the IEFD block (the only sharpening accelerator enabled in the firmware) |
| Chrome / V4L2 apps | `libcamerify <app>` |

## What is in here

1. **Kernel**: a DMI entry for the Latitude 7275 in
   `drivers/platform/x86/intel/int3472/tps68470_board_data.c`, reusing the
   Latitude 7212 regulator and GPIO data (only the PMIC I2C device name
   differs). Not in mainline. Without it the PMIC driver fails with
   "No board-data found for this model" and the sensor is never powered.
2. **libcamera ipu3 IPA** (`patches/libcamera-0.7.0-ipu3-ccm-oem.patch`):
   - `Ccm`: colour temperature interpolated colour correction matrix
     (ported from the rkisp1 IPA).
   - `Lsc`: lens shading correction in the ImgU SHD block. LUT format
     found experimentally: 12-bit entries, gain = `1 + v / 2^(10 - gain_factor)`,
     grid over the BDS output, channels in the sensor Bayer order.
   - `Saturation`: control of the TCC chroma gain table, which the kernel
     driver enables by default with a boost of up to 1.5x.
   - `Sharpness`: IEFD unsharp mask and directional sharpening. The Y_EE_NR
     block does not work: no firmware binary enables its accelerator
     (`yuvp1_b0_acc`), see `tools/fwdump.c`.
   - `Awb`: OEM white point locus for the colour temperature estimate,
     `gainCorrection`, `minGreenLevel`, `statsOffset`, tuning aids.
   - `BlackLevelCorrection`: tunable `blackLevel`. The ImgU obgrid unit is
     half a 10-bit LSB: the sensor's 64 must be written as 128. With the
     hard-coded 64 a residual pedestal biases AWB and gets multiplied by
     the colour gains.
   - `ToneMapping`: tunable gamma. Note that in the video pipe the firmware
     ignores the LUT contents and applies a fixed curve.
   - `Agc`: fix of swapped green/blue gains in the luminance estimate.
3. **`tools/decode_cpf_sky.py`**: decoder for the "flat" Skylake-era Intel
   CPFF tuning files (`OV5670_<module>_SKY.cpf` in Dell's *Intel 2D Imaging
   Driver* 30.10154.6618.148): colour matrices per illuminant, chromaticity,
   black level, lens shading. The module of a given unit is in ACPI:
   `\_SB.PCI0.LNK2._DDN` (`4BF523T2` here). Record layouts follow Intel's
   public headers in `intel/ipu6-camera-bins` (`ia_cmc_types.h`).
4. **`tools/fwdump.c`**: lists the ISP binaries of an ImgU firmware with
   their accelerator enable flags, using the kernel driver structures.

## What could not be done

- The video pipe firmware ignores the gamma LUT (fixed curve) and the
  Y_EE_NR parameters. The still pipe aborts under libcamera. Brightness is
  set through the AGC target instead.
- The LAIQ/LISP sections of the `.cpf` (Intel 3A and ISP tuning) target
  Intel's proprietary binaries and are not used.

## Calibration data notice

`config/ov5670.yaml` contains numbers derived from Dell/Intel's proprietary
calibration of module 4BF523T2. Code is LGPL-2.1+ (libcamera) and GPL-2.0
(kernel); the tools are MIT. The calibration data has the same standing as
in other projects reusing OEM tuning.

Measurements, images and procedures are in `docs/`; measurement scripts in
`tools/` (`medir.py`, `yuv.py`, `esquinas.py`, `pedestal.py`, `nitidez.py`).
