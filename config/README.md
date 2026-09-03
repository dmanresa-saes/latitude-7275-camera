# Configuración del sistema (Gentoo, kernel 6.18, libcamera 0.7.0)

- **Kernel:** parche `patches/0001-...Latitude-7275.patch` sobre
  `drivers/platform/x86/intel/int3472/tps68470_board_data.c`. Sin recompilar el
  kernel: se compila el módulo `intel_skl_int3472_tps68470` fuera del árbol y
  se deja en `/lib/modules/<kver>/updates/`.
- **Línea del kernel:** `acpi_enforce_resources=lax`. El controlador I2C4
  (INT3446) donde cuelga el sensor comparte MMIO con una OperationRegion ACPI
  (`\_SB.PCI0.GEXP.BAR0`) y el kernel lo rechaza en modo estricto.
- **libcamera:** `patches/libcamera-0.7.0-ipu3-ccm-oem.patch` en
  `/etc/portage/patches/media-libs/libcamera/` con USE `v4l tools`.
  Instala `ov5670.yaml` (aquí en `config/`) en `/usr/share/libcamera/ipa/ipu3/`.
- **Chrome y apps V4L2:** `libcamerify <app>`.
