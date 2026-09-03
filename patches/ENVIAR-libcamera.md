# Cómo enviar la primera tanda a libcamera

Serie en `libcamera-upstream/` (3 parches + carta), generada con
`git format-patch` sobre `upstream/master` (849cd2d, 2026-05-01) en una
rama local `ipu3-fixes` del clon de `~/camara/libcamera`. Compila con
`-Dpipelines=ipu3 -Dipas=ipu3` y `utils/checkstyle.py` solo objeta el
reformateo que clang-format propone sobre código preexistente del AGC
(ignorable) y la falta de la herramienta `reuse`.

Los trailers `Co-Authored-By: Claude...` y `Claude-Session:` se han quitado de
los ficheros exportados porque `checkstyle` no los admite; los commits locales
los conservan. Decide tú si quieres mencionar la asistencia de IA en la carta.

Envío (lista pública, sin suscripción obligatoria pero recomendada):

    git send-email --to=libcamera-devel@lists.libcamera.org \
        libcamera-upstream/0000-cover-letter.patch libcamera-upstream/000[1-3]-*.patch

Segunda tanda (tras validar el lens shading con la pared uniforme): Ccm,
Lsc, Saturation, Sharpness y los mandos del Awb. Están en
`libcamera-0.7.0-ipu3-ccm-oem.patch` contra 0.7.0; habrá que portarlos a
master igual que estos (`ValueNode` en vez de `YamlObject`).
