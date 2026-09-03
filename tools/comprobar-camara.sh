#!/bin/bash
# Comprueba, paso a paso, la cadena de la camara IPU3 del Latitude 7275.
# Uso: ~/camara-ipu3/comprobar-camara.sh   (pide sudo para dmesg)
ok(){ printf '  [OK]   %s\n' "$*"; }
ko(){ printf '  [MAL]  %s\n' "$*"; }
echo "1. Linea del kernel"
grep -q acpi_enforce_resources=lax /proc/cmdline && ok "acpi_enforce_resources=lax activo" || ko "falta acpi_enforce_resources=lax (reiniciar con el grub nuevo)"
echo "2. Controlador I2C4 (INT3446, donde esta el sensor)"
d=$(readlink /sys/bus/platform/devices/INT3446:00/driver 2>/dev/null | xargs -r basename)
[ -n "$d" ] && ok "INT3446:00 con driver $d" || ko "INT3446:00 sin driver (mirar dmesg: error -16 = conflicto ACPI)"
echo "3. PMIC TPS68470 (INT3472:04)"
[ -e /sys/bus/i2c/drivers/int3472-tps68470/i2c-INT3472:04 ] && ok "PMIC enlazado" || ko "PMIC sin enlazar (modulo de updates/ no cargado?)"
m=$(modinfo -n intel_skl_int3472_tps68470 2>/dev/null); echo "         modulo: $m"
echo "4. Sensor OV5670 (INT3479:00)"
[ -e /sys/bus/i2c/devices/i2c-INT3479:00 ] && ok "dispositivo I2C creado" || ko "no existe i2c-INT3479:00"
[ -e /sys/bus/i2c/drivers/ov5670/i2c-INT3479:00 ] && ok "driver ov5670 enlazado" || ko "ov5670 no enlazado (chip ID? GPIOs reset/powerdown?)"
echo "5. dmesg (necesita sudo)"
sudo dmesg 2>/dev/null | grep -E 'INT3446|tps68470|ov5670|cio2|imgu|INT3479' | tail -15 | sed 's/^/         /'
echo "6. libcamera"
if command -v cam >/dev/null; then cam -l 2>&1 | sed 's/^/         /'; else ko "cam no instalado (emerge media-libs/libcamera)"; fi
command -v libcamerify >/dev/null && ok "libcamerify disponible: libcamerify chrome-vaapi" || ko "libcamerify no instalado (USE v4l en libcamera)"
