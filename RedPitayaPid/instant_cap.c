/* Red Pitaya C API example of Instantly acquiring a signal on a specific channel */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "rp.h"

int main(int argc, char **argv){

    /* Print error, if rp_Init() function failed */
    if(rp_Init() != RP_OK){
        fprintf(stderr, "Rp api init failed!\n");
    }

    rp_AcqReset();
    // Open a CSV file for writing
    FILE *csv_file = fopen("acquisition_data.csv", "w");
    if (!csv_file) {
        fprintf(stderr, "Failed to open CSV file for writing\n");
        rp_Release();
        return EXIT_FAILURE;
    }
 
    /* Acquisition */
    uint32_t buff_size = 16384;
    float *buff = (float *)malloc(buff_size * sizeof(float));

    rp_AcqSetDecimation(RP_DEC_1);
    rp_AcqSetTriggerLevel(RP_CH_1, 0.5);         // Trig level is set in Volts while in SCPI
    rp_AcqSetTriggerDelay(0);

    // There is an option to select coupling when using SIGNALlab 250-12
    // rp_AcqSetAC_DC(RP_CH_1, RP_AC);           // enables AC coupling on Channel 1

    // By default LV level gain is selected
    rp_AcqSetGain(RP_CH_1, RP_LOW);              // user can switch gain using this command

    rp_AcqStart();

    /* After the acquisition is started some time delay is needed to acquire fresh samples into buffer
    Here we have used a time delay of one second but you can calculate the exact value taking into account buffer
    length and sampling rate */

    sleep(1);
    rp_AcqSetTriggerSrc(RP_TRIG_SRC_NOW);
    rp_acq_trig_state_t state = RP_TRIG_STATE_TRIGGERED;

    while(1){
        rp_AcqGetTriggerState(&state);
        if(state == RP_TRIG_STATE_TRIGGERED){
            break;
        }
    }

    bool fillState = false;
    while(!fillState){
        rp_AcqGetBufferFillState(&fillState);
    }

    rp_AcqGetOldestDataV(RP_CH_1, &buff_size, buff);
    int i;
    for(i = 0; i < buff_size; i++){
        fprintf(csv_file, "%f\n", buff[i]);
    }

    /* Releasing resources */
    free(buff);
    rp_Release();
    return 0;
}
