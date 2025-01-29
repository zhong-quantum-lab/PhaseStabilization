/* Red Pitaya C API example Acquiring a signal from a buffer
 * This application acquires a signal on a specific channel and writes it to a CSV file. */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include "rp.h"

#define DATA_SIZE 64

int main(int argc, char **argv)
{
    int dsize = DATA_SIZE;
    uint32_t dec = 1;

    if (argc >= 3){
        dsize = atoi(argv[1]);
        dec = atoi(argv[2]);
    }

    /* Print error, if rp_Init() function failed */
    if (rp_InitReset(false) != RP_OK) {
        fprintf(stderr, "Rp api init failed!\n");
        return -1;
    }

    uint32_t g_adc_axi_start, g_adc_axi_size;
    rp_AcqAxiGetMemoryRegion(&g_adc_axi_start, &g_adc_axi_size);

    printf("Reserved memory start 0x%X size 0x%X\n", g_adc_axi_start, g_adc_axi_size);

    if (rp_AcqAxiSetDecimationFactor(dec) != RP_OK) {
        fprintf(stderr, "rp_AcqAxiSetDecimationFactor failed!\n");
        return -1;
    }
    if (rp_AcqAxiSetTriggerDelay(RP_CH_1, dsize) != RP_OK) {
        fprintf(stderr, "rp_AcqAxiSetTriggerDelay RP_CH_1 failed!\n");
        return -1;
    }
    if (rp_AcqAxiSetBufferSamples(RP_CH_1, g_adc_axi_start, dsize) != RP_OK) {
        fprintf(stderr, "rp_AcqAxiSetBuffer RP_CH_1 failed!\n");
        return -1;
    }
    if (rp_AcqAxiEnable(RP_CH_1, true) != RP_OK) {
        fprintf(stderr, "rp_AcqAxiEnable RP_CH_1 failed!\n");
        return -1;
    }

    //rp_AcqSetTriggerLevel(RP_T_CH_1, 0.25);

    if (rp_AcqStart() != RP_OK) {
        fprintf(stderr, "rp_AcqStart failed!\n");
        return -1;
    }

    //rp_AcqSetTriggerSrc(RP_TRIG_SRC_CHA_PE);
    rp_AcqSetTriggerSrc(RP_TRIG_SRC_NOW);
    rp_acq_trig_state_t state = RP_TRIG_STATE_TRIGGERED;

    while(1){
        rp_AcqGetTriggerState(&state);
        if(state == RP_TRIG_STATE_TRIGGERED){
            sleep(1);
            break;
        }
    }

    bool fillState = false;
    while (!fillState) {
        if (rp_AcqAxiGetBufferFillState(RP_CH_1, &fillState) != RP_OK) {
            fprintf(stderr, "rp_AcqAxiGetBufferFillState RP_CH_1 failed!\n");
            return -1;
        }
    }
    rp_AcqStop();

    uint32_t posChA;
    rp_AcqAxiGetWritePointerAtTrig(RP_CH_1, &posChA);

    fprintf(stderr, "Tr pos1: 0x%X\n", posChA);

    int16_t *buff1 = (int16_t *)malloc(dsize * sizeof(int16_t));

    uint32_t size1 = dsize;
    rp_AcqAxiGetDataRaw(RP_CH_1, posChA, &size1, buff1);

    /* Write data with timestamps to CSV */
    FILE *csv_file = fopen("acquisition_data.csv", "w");
    if (!csv_file) {
        fprintf(stderr, "Failed to open CSV file for writing!\n");
        rp_AcqAxiEnable(RP_CH_1, false);
        rp_Release();
        free(buff1);
        return -1;
    }

    double sampling_interval = (1.0 / 125000000.0) * dec; // Effective sampling interval in seconds
    for (int i = 0; i < dsize; i++) {
        double timestamp = i * sampling_interval; // Time for each sample
        fprintf(csv_file, "%.9f, %d\n", timestamp, buff1[i]); // Write time and value
    }

    fclose(csv_file);
    printf("Data with timestamps written to acquisition_data.csv\n");




    /* Releasing resources */
    rp_AcqAxiEnable(RP_CH_1, false);
    rp_Release();
    free(buff1);
    return 0;
}

