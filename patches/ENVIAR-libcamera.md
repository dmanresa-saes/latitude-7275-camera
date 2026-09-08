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

## ENVIADA la primera tanda el 2026-09-04 a las 08:28 (CEST)

A libcamera-devel@lists.libcamera.org con `git send-email`, desde dmanresa@gmail.com.
Antes de enviar se corrigio el `From:` de la carta (salia el usuario local) y se
anadio el enlace al repositorio.
Message-ID de la carta: `<20260904062840.46739-1-dmanresa@gmail.com>` (parches -2, -3, -4).
Archivo: https://patchwork.libcamera.org/project/libcamera/list/?submitter=dmanresa
Seguimiento: respuestas en Gmail; para v2, `git format-patch -v2 --cover-letter` y
`--in-reply-to` al Message-ID de la carta.

## RESPUESTAS de Dan Scally (2026-09-04, entre 09:35 y 09:50 CEST), leidas el 2026-09-08

Dan es el mantenedor del IPA IPU3. Contesto a los tres parches y a la carta
el mismo dia. Resumen y plan:

- Carta: bienvenida ("we don't often get people working on the IPU3 IPA").
  Ccm y Lsc ya estan en SU serie "[PATCH v3 00/10] libipa: Re-work IPU3 IPA
  to use libipa algorithms" (patchwork series 6162; el 2026-09-08 aun NO
  esta en master, v0.7.2-132). Los mandos de croma del TCC y del sharpening
  IEFD NO los va a hacer nadie: "that would be very welcome". ESA es nuestra
  segunda tanda.
- 1/3 AGC (ganancias G/B cambiadas): "good spot", pide rebase y ofrece
  Reviewed-by: Daniel Scally. Luego anade que el rework de libipa (patch
  28166) tambien lo arregla. En master (c08caf6) el fallo SIGUE (agc.cpp
  lineas 226-228). Decision: rebasar y enviar v2 solo de este parche; es
  minimo y arregla un bug real hoy.
- 2/3 black level: NO como parametro de tuning. Debe venir del
  CameraSensorHelper del sensor (src/ipa/libipa/camera_sensor_helper.cpp),
  que para ov5670 no define blackLevel_ (ov5675 si: 4096 = 0x40 a 10 bits),
  y el BLC del IPU3 debe leerlo de ahi. Plan v2, dos parches:
    a) libipa: camera_sensor_helper: add the OV5670 black level (4096).
    b) ipa: ipu3: blc: use the sensor black level from the helper, con la
       conversion medida: unidad obgrid = medio LSB de 10 bits, o sea
       obgrid = blackLevel16 >> 5 (4096 -> 128). Mantener 64 si no hay dato.
- 3/3 gamma: superado por su serie (GammaAlgorithm en libipa con gamma por
  defecto en tuning). Sobre nuestra observacion de que el firmware ignora
  la LUT: el tiene el MISMO firmware y a el le funciona; pide que probemos
  su serie y veamos si cambiar la gamma surte efecto. Hacer esa prueba
  (aplicar series 6162 sobre master, gamma 0.5/1.1/3.0, medir Y).

Trabajo que queda en el clon ~/camara/libcamera: master local esta 59
commits detras de origin y con cambios sin guardar en awb.h y softisp/agc.cpp
(revisar antes de rebasar).
