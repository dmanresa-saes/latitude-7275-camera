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

## ENVIADO el 2026-09-08 (v2), ficheros en `libcamera-upstream/v2/`
- [PATCH v2] ipa: ipu3: agc: Fix swapped green and blue gains (rebase + Reviewed-by Dan),
  Message-ID <20260908161805.335568-1-dmanresa@gmail.com>, en el hilo del 1/3.
- [PATCH v2 0/2] ipa: ipu3: Take the OV5670 black level from the sensor helper,
  Message-ID <20260908163708.341308-1-dmanresa@gmail.com>, en el hilo del 2/3:
  1/2 helper ov5670 blackLevel_=4096; 2/2 BLC lee el helper y desplaza >>5.
  Medido (misma escena, uncalibrated.yaml, NV12 limitado): con 64 el
  percentil 1 de Y es 32 y U/V oscuro 132/131; con 128, 15 y 128/128.
  Herramienta: `~/camara-ipu3/blackpoint.py ANCHO ALTO f.nv12`.
- Gamma (3/3): retirado. Prueba de la serie de Dan (6162) en curso: no
  compila sobre master actual con -Werror (usa `Span` obsoleto); se
  compila con -Dwerror=false en un worktree.
Rama local: `ipu3-agc-v2` en ~/camara/libcamera (3 commits sobre origin/master).
Compilar: `meson setup build-ipu3 -Dpipelines=ipu3 -Dipas=ipu3` y probar sin
instalar con LD_LIBRARY_PATH/LIBCAMERA_IPA_MODULE_PATH/LIBCAMERA_IPA_CONFIG_PATH
(ver ~/camara-ipu3/runcam.sh).

## Gamma: prueba de la serie de Dan hecha el 2026-09-08 (18:40)
Serie v3 (patchwork 6162) sobre master c08caf6, compilada con -Dwerror=false
(usa `Span` obsoleto). Con uncalibrated.yaml + `gamma:` bajo ToneMapping,
1280x720 NV12, misma escena: gamma 0.5 -> mediana Y 28 (P10 4, P90 76);
1.1 -> 110 (43, 163); 3.0 -> 187 (133, 217). LA LUT SI SE RESPETA: nuestra
afirmacion de que el firmware la ignoraba era falsa (algo fallaba en la
prueba de 0.7.0, no en el ImgU). Respondido a Dan con Tested-by para sus
dos parches de gamma del IPU3, Message-ID <20260908164118.342206-1-dmanresa@gmail.com>.
Consecuencia para nuestro tuning 0.7.0 (ov5670.yaml): cuando llegue la serie
de Dan a master, la gamma se ajusta con `gamma:` en el tuning, sin parche.
Nota: en master (con y sin la serie) el AGC del IPU3 escupe "Effective
exposure value is 0. This is a bug in AGC" en los primeros fotogramas; la
imagen sale bien. No es nuestro; vigilar si alguien lo reporta.
