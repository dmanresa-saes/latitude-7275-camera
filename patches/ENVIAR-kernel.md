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
