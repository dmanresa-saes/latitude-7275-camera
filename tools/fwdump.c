#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ipu3-abi.h"
#include "ipu3-css-fw.h"
#define F(x) if (e->enable.x) printf(" %s", #x);
int main(int argc, char **argv)
{
	FILE *f = fopen(argv[1], "rb"); if (!f) return 1;
	fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
	unsigned char *d = malloc(sz); fread(d, 1, sz, f); fclose(f);
	struct imgu_fw_header *h = (void *)d;
	printf("version %s, binarios %d, h_size %u (sizeof %zu), sizeof(fw_info) %zu\n", h->file_header.version, h->file_header.binary_nr, h->file_header.h_size, sizeof(h->file_header), sizeof(struct imgu_fw_info));
	for (int i = 0; i < h->file_header.binary_nr; i++) {
		struct imgu_fw_info *bi = &h->binary_header[i];
		const char *name = bi->blob.prog_name_offset < sz ? (const char *)d + bi->blob.prog_name_offset : "?";
		printf("#%2d type %u name %-28s size %u", i, bi->type, name, bi->blob.size);
		if (bi->type == IMGU_FW_ISP_FIRMWARE) {
			struct imgu_abi_binary_info *e = &bi->info.isp.sp;
			printf("\n    id %u mode %u  enable:", e->id, e->pipeline.mode);
			F(bds_acc) F(shd_acc) F(shd_ff) F(stats_3a_raw_buffer) F(acc_bayer_denoise) F(bnr_ff) F(awb_acc) F(awb_fr_acc) F(anr_acc) F(rgbpp_acc) F(rgbpp_ff) F(demosaic_acc) F(demosaic_ff) F(dvs_stats) F(lace_stats) F(yuvp1_b0_acc) F(yuvp1_c0_acc) F(yuvp2_acc) F(ae) F(af) F(dergb) F(rgb2yuv) F(high_quality) F(kerneltest) F(routing_shd_to_bnr) F(routing_bnr_to_anr) F(routing_anr_to_de) F(routing_rgb_to_yuvp1) F(routing_yuvp1_to_yuvp2) F(luma_only) F(input_yuv) F(input_raw) F(reduced_pipe) F(vf_veceven) F(dis) F(dvs_envelope) F(uds) F(dvs_6axis) F(block_output) F(streaming_dma) F(ds) F(bayer_fir_6db) F(raw_binning) F(continuous) F(s3a) F(fpnr) F(sc) F(macc) F(output) F(ref_frame) F(tnr) F(xnr) F(params) F(ca_gdc) F(isp_addresses) F(in_frame) F(out_frame) F(high_speed) F(dpc)
		}
		printf("\n");
	}
	return 0;
}
