# fwdump: lista los binarios ISP de un firmware del ImgU (IPU3)

Usa las estructuras del propio driver del kernel (`ipu3-abi.h`, `ipu3-css-fw.h`,
copiadas de linux v6.18) con un adaptador de tipos para espacio de usuario.

    mkdir -p include/uapi && cp /usr/src/linux/include/uapi/linux/intel-ipu3.h include/uapi/
    gcc -include shim.h -I. -o fwdump fwdump.c
    ./fwdump /lib/firmware/intel/ipu3-fw.bin          # firmware Linux (2017)
    ./fwdump css_fw.bin                                # firmware del driver Dell (2015)

Por cada binario imprime nombre, id, modo (2 = foto/primary, 3 = vídeo) y los
flags `enable` (qué aceleradores usa). Hallazgo del 2026-09-03: ningún binario
activa `yuvp1_b0_acc` (Y_EE_NR, YDS, CHNR), todos activan `yuvp1_c0_acc`
(IEFD) y `yuvp2_acc` (TCC). Por eso el realce de bordes Y_EE_NR no responde y
el IEFD sí.
