# Cómo enviar el parche del kernel

Parche: `0001-platform-x86-int3472-Add-TPS68470-board-data-for-Dell-Latitude-7275.patch`,
rebasado sobre mainline (torvalds/master, 2026-09-03) y limpio en `checkpatch.pl --strict`.

Destinatarios (MAINTAINERS de mainline):

- To: Daniel Scally <dan.scally@ideasonboard.com>, Sakari Ailus <sakari.ailus@linux.intel.com>
  (INTEL SKYLAKE INT3472 ACPI DEVICE DRIVER)
- Cc: Hans de Goede <hansg@kernel.org>, Ilpo Järvinen <ilpo.jarvinen@linux.intel.com>,
  platform-driver-x86@vger.kernel.org, linux-kernel@vger.kernel.org

Con git send-email (configurar antes `sendemail.smtpServer` etc.):

    git send-email --to="Daniel Scally <dan.scally@ideasonboard.com>" \
        --to="Sakari Ailus <sakari.ailus@linux.intel.com>" \
        --cc="Hans de Goede <hansg@kernel.org>" \
        --cc="Ilpo Järvinen <ilpo.jarvinen@linux.intel.com>" \
        --cc=platform-driver-x86@vger.kernel.org --cc=linux-kernel@vger.kernel.org \
        0001-platform-x86-int3472-Add-TPS68470-board-data-for-Dell-Latitude-7275.patch

Antes de enviar: comprobar que el parche aplica sobre el árbol
`platform-drivers-x86.git` rama `for-next` (`git apply --check`), y si el
mantenedor prefiere que la nota de `acpi_enforce_resources=lax` vaya aparte,
quitarla del mensaje.

## ENVIADO el 2026-09-04 a las 08:20 (CEST)

Con `git send-email` desde dmanresa@gmail.com, a los destinatarios de arriba.
Message-ID: `<20260904062006.39209-1-dmanresa@gmail.com>`
Archivo publico: https://lore.kernel.org/platform-driver-x86/20260904062006.39209-1-dmanresa@gmail.com/
Seguimiento: respuestas al hilo en Gmail; si piden v2, `git format-patch -v2` y responder con `--in-reply-to` a ese Message-ID.

## RESPUESTA de Sakari Ailus (2026-09-04 09:04 CEST), leida el 2026-09-08

Dos cosas, ninguna de fondo:
1. El parrafo "Tested on a Latitude 7275..." y la "Note:" sobre
   `acpi_enforce_resources=lax` deben ir DEBAJO de la linea `---` (no en el
   mensaje de commit).
2. Pregunta si el conflicto I2C4/GEXP es el mismo que el del Latitude 5285,
   serie de Thierry Chatard "Enable cameras on Dell Latitude 5285 2-in-1"
   v10 (2026-08-31, Message-ID <20260831160754.9857-1-tchatard@gmail.com>,
   patchwork.linuxtv.org series 29704). RESPUESTA: SI, identico. Comprobado
   en nuestro DSDT (`~/bios-7275/dsdt.dsl`): `Device (GEXP)` declara
   `OperationRegion (BAR0, SystemMemory, SB04, 0x208)` y el I2C4 (INT3446)
   devuelve su _CRS con la misma variable SB04. Su parche 1/8
   "mfd: intel-lpss: add resource conflict quirk for Dell Latitude 5285"
   (Reviewed-by Andy Shevchenko) anade QUIRK_IGNORE_RESOURCE_CONFLICTS a
   INT3446 por DMI. Para la 7275 basta anadir una entrada DMI
   "Latitude 7275" a su tabla `intel_lpss_quirk_dmi[]`.
   Lo que NO compartimos: el fallo de _DEP (GNVS C0TP=0) que le obliga a una
   lista estatica de consumidores de reloj; en la 7275 el tps68470-clk ya
   tiene a i2c-INT3479:00 como consumidor (clk_summary), asi que no hace falta.

Plan (v2):
- Contestar a Sakari (borrador en RESPUESTA-sakari-borrador.txt).
- v2 del parche: mover Tested/Note bajo `---`; en la nota citar la serie del
  5285 y decir que la 7275 necesita la misma quirk.
- Parche aparte, encima del 1/8 de Thierry: "mfd: intel-lpss: add Dell
  Latitude 7275 to the resource conflict quirk" (solo la entrada DMI), o
  pedirle a Thierry que la incluya en su v11 con nuestro Tested-by. Para
  dar Tested-by hay que compilar intel-lpss-acpi con su parche: en el kernel
  dist-bin es built-in (CONFIG_MFD_INTEL_LPSS_ACPI=y), asi que exige kernel
  propio (punto 3 de ESTADO Y PENDIENTES) o fiarse del analisis del DSDT.

## ENVIADO el 2026-09-08 (18:13-18:16 CEST)
- Respuesta a Sakari: Message-ID <20260908161322.334690-1-dmanresa@gmail.com>
  (confirma que el conflicto I2C4/GEXP es el mismo que el del 5285).
- v2 del parche int3472 (`v2-0001-platform-x86-int3472-...patch`), hilo del
  original: Message-ID <20260908161445.334910-1-dmanresa@gmail.com>.
- Parche nuevo `0002-mfd-intel-lpss-add-Dell-Latitude-7275-to-the-resource-conflict-quirk.patch`,
  enhebrado bajo el 1/8 de Thierry, To: Lee Jones (mfd), Cc Thierry, Andy
  Shevchenko, Hans, Ilpo, Sakari, Dan, LKML, pdx86, linux-media.
  Message-ID <20260908161629.335223-1-dmanresa@gmail.com>. Aplica sobre
  mainline + 1/8 de Thierry (comprobado con git apply). No probado en
  ejecucion (intel-lpss-acpi es built-in en el kernel dist-bin); dicho en
  el correo.

## Hallazgo del 2026-09-08: la camara muere tras HIBERNAR (PMIC TPS68470)
Tras la hibernacion del 07-09 el PMIC volvio a sus valores de reset
(CORE 0,9 V, ANA/AUX 0,875 V en vez de 1,2 / 2,815 / 1,213 / 1,8 V) y el
sensor no responde por I2C ("ov5670_start_streaming failed to set powerup
registers"). Los drivers tps68470-regulator/gpio/clk no reprograman el chip
al reanudar. Rebind del PMIC imposible con el driver de serie: exige
consumidores ACPI (_DEP) y esa lista se vacia al arrancar ("INT3472 seems
to have no dependents"). Solucion local: `int3472-clk-consumidores-estaticos.patch`
en nuestro modulo fuera de arbol (lista estatica de consumidores de reloj
en la board data, mismo espiritu que el 4/8 de Thierry) + script
`~/.local/bin/rearmar-camara` (unbind/bind PMIC y sensor). CANDIDATO A
PARCHE UPSTREAM: tps68470 mfd/regulator sin restore tras hibernacion.
