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

## SEGUNDA TANDA ENVIADA el 2026-09-09 (09:01 CEST), ficheros en `libcamera-upstream/round2/`
[PATCH 0/2] ipa: ipu3: Add Saturation and Sharpness algorithms,
Message-ID <20260909070146.18825-1-dmanresa@gmail.com>, cc Dan Scally.
- 1/2 Saturation: bloque TCC con los valores del driver y la tabla de ganancia
  de croma escalada por controls::Saturation (0..2, tuning `saturation:`,
  1.0 = driver). Medido: croma 0,00 / 7,97 / 15,83 con 0 / 1 / 2.
- 2/2 Sharpness: bloque IEFD con los valores del driver y unsharp amount,
  dir_shrp y limites escalados por controls::Sharpness (0..9, tuning
  `sharpness:`). Medido: sigma laplaciano 2,24 / 2,47 / 2,81 / 3,43 con
  0 / 1 / 4 / 9. Y_EE_NR descartado (ningun binario del firmware lo activa).
Basada en la serie v3 de Dan (6162): usa `context.ctrlMap`. Rama local
`ipu3-round2` en el worktree ~/camara/libcamera-dan (build en `build/`,
werror=false). Si Dan saca v4, rebasar y reenviar como v2.
Herramientas: `metrica.py` (Y media, croma media, nitidez) y `blackpoint.py`,
copiadas a `tools/` del repo. Comparativa: ~/camara-ipu3/sat-sharp-comparativa.png.
Estado kernel el 09-09: Hans de Goede dio Reviewed-by al parche DMI de
intel-lpss; Andy Shevchenko pide que Thierry lo lleve como parche 2 de su
v11 (contestado, Message-ID <20260909065104.15817-1-dmanresa@gmail.com>);
falta el Ack de Lee Jones. El robot media-ci no pudo aplicarlo solo (depende
de la serie del 5285): normal.

## Segunda tanda: revision de Barnabas Pocze (09-09 09:34/09:48) y v2 ENVIADA (10:13 CEST)
Barnabas (Ideas on Board) reviso los dos parches a la hora de enviarlos, solo
estilo: float en vez de double; sin `static` en el namespace anonimo;
cuantizar con `UQ<>` de libipa/fixedpoint.h (u12.0 ganancia TCC, u4.5
unsharp amount, u1.6 dir_shrp, u13.0 limites); copiar r_sqr por asignacion
de struct como el kernel; comentar que la config TCC replica
imgu_css_cfg_acc(); tabla IEFD con inicializadores designados como
ipu3-tables.c. Todo aplicado, recompilado y reprobado (croma dobla de 1.0 a
2.0; nitidez 2,86 -> 4,10 de 1.0 a 9.0). v2 en `libcamera-upstream/round2-v2/`,
Message-ID <20260909081355.28471-1-dmanresa@gmail.com>, cc Dan y Barnabas.
Truco: al construir UQ<> desde un bitfield del uapi hay que hacer
static_cast<uint16_t>/uint8_t o el constructor es ambiguo.
Dan (09-09 08:53): agradece el Tested-by de gamma y arreglara Span en su v4.

## Black level v3 ENVIADA el 2026-09-10 (19:21 CEST), ficheros en `libcamera-upstream/v3/`
Dan Scally reviso la v2 el 10-09 a las 17:25: (1) `uint16_t` en vez de
`int16_t` para la constante y el miembro; (2) dejar solo el `\copydoc` como
bloque de documentacion y mover la explicacion del `>> 5` a un comentario
junto al propio desplazamiento. Ademas CONFIRMO el hallazgo en una Surface
Go 2 con OV5693: hay que pasarle al ISP el doble del pedestal configurado en
el sensor. Aplicado todo y reprobado (nivel 128, punto negro p1=8).
Message-ID de la v3 <20260910172120.73148-1-dmanresa@gmail.com>.
Ademas se le contesto a su duda de por que la unidad es media LSB
(Message-ID <20260910172222.73322-1-dmanresa@gmail.com>): encaja con que el
OB grid se aplique despues de que el formateador de entrada ensanche el dato
de 10 a 11 bits; el resto del pipeline va mas ancho (los umbrales de
saturacion del AWB estan documentados sobre [0, 8191]). No hay nada en el
uAPI que fije la unidad, asi que queda como observacion empirica en dos
sensores.

## Black level v4 ENVIADA el 2026-09-11 (17:39 CEST), ficheros en `libcamera-upstream/v4/`
Revisiones de la v3:
- Laurent Pinchart (10-09 20:05 y 20:09). Sobre el 1/2: "That's not the right
  way to measure the data pedestal" — TENIA RAZON y era objecion de fondo, no
  de estilo: yo deducia el pedestal de la salida del ISP, que es justo lo que
  el 2/2 configura con ese valor, o sea circular. Sobre el 2/2: mensaje de
  commit y comentario "too long, with lots of irrelevant information".
- Dan Scally (11-09 13:26, DESPUES de Laurent, y coincide con el): cortar el
  mensaje de commit tras el primer parrafo, s/The helper/CameraSensorHelper/
  y redaccion concreta del comentario con dos ejemplos (pedestal 16 -> 32,
  64 -> 128).
Solucion del 1/2: la fuente correcta estaba en casa. El CPF OEM de este modulo
(`~/camara-ipu3/tuning-oem/ov5670_4BF523T2_oem.json`, clave
`nivel_negro_10bit`) trae la CARACTERIZACION del fabricante: 30 entradas,
6 exposiciones x 5 ganancias, los 4 canales Bayer. A ganancia 1: 64,1..64,4.
Hasta ganancia 15,9: 62,0..64,5. Eso si es una medida del pedestal, y es lo
que cita ahora el mensaje de commit. (La nota del doc que decia "63 a 10 bits"
era un redondeo malo: los valores reales rondan 64,2.)
Message-ID v4 <20260911153918.96470-1-dmanresa@gmail.com>; respuesta directa a
Laurent en <20260911153951.96564-1-dmanresa@gmail.com>, reconociendo el fallo
y ofreciendo el dato del datasheet a quien lo tenga (yo no).
LECCION: no justificar un valor de sensor con medidas tomadas a traves del
bloque del ISP que ese mismo valor configura.

## 2026-09-11 17:47 — Laurent: "AI slop". PARADO, pendiente de decision del usuario
Respuesta de Laurent a mi correo de reconocimiento (archivo libcamera-devel
061992): "I have a very hard time not reading this as AI slop". No es objecion
tecnica. Disparador: la frase "You are right, and it is worse than merely
imprecise: ... so it could not confirm anything" — registro de LLM.
NO se ha contestado. Cualquier respuesta (negar, admitir, explicar) es una
afirmacion publica sobre el usuario, no una aclaracion tecnica.
Dato para decidir: en el kernel SI se declara (Assisted-by, y el usuario se lo
dijo a Sakari por su nombre). En libcamera nuestros parches no llevan etiqueta
y libcamera NO tiene convencion: nada en contributing.rst ni coding-style.rst,
cero Assisted-by en el historial del arbol. La asimetria es nuestra.
La v4 (17:39) sigue sin review; no depende de esto.

## 2026-09-11 18:52 — el usuario contesta EL MISMO a Laurent (archivo 061993)
"I direct this work and test it on my own hardware. I use an AI assistant to
write it up, and I should have said so on this list, as I do in my kernel
patches." Comprobado en el archivo publico.
REGLA A PARTIR DE AHORA: todo parche de libcamera declara la asistencia, igual
que los del kernel. NO se reenvian la v4 ni la v2 de Saturation/Sharpness solo
por la etiqueta (seria ruido): se aplica en la siguiente version de cada una.
Formatos en uso con esta misma firma: kernel `Assisted-by: Claude Code:...`;
libcamera (la otra sesion, RFC awb gainMin 061741 de agosto) una frase en el
mensaje: "Developed with the assistance of an AI tool (Claude) and verified
on ..."; libcamera (esta sesion) nada hasta hoy. El doc del kernel
(coding-assistants.rst) fija `Assisted-by: LLM [TOOL1] [TOOL2]`, donde las
herramientas son de analisis, no el modelo; pero Sakari pregunto "which one?"
ante un LLM pelado. Falta que el usuario fije la redaccion exacta.
Y nombrar el modelo real: hasta la manana del 11-09 fue Fable 5.1, desde la
tarde Opus 5.
