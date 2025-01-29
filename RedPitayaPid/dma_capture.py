#!/usr/bin/python3
"""DMA acquisition script for continuous capture of raw data."""

import time
import rp
import csv

# Constants
BUFFER_SIZE = 16384        # Number of samples per buffer
NUM_BUFFERS = 3          # Number of buffers to acquire
DECIMATION = rp.RP_DEC_32 # Decimation factor
TRIGGER_LEVEL = 0.2       # Trigger level in volts

# Initialize the interface
rp.rp_Init()

# Setting up DMA
memory_region = rp.rp_AcqAxiGetMemoryRegion()
g_adc_axi_start = memory_region[1]
g_adc_axi_size = memory_region[2]
print(f"Reserved memory Start: {g_adc_axi_start:x} Size: {g_adc_axi_size:x}\n")

rp.rp_AcqAxiSetDecimationFactor(DECIMATION)
rp.rp_AcqAxiSetTriggerDelay(rp.RP_CH_1, BUFFER_SIZE)

# Configure buffer for Channel 1
rp.rp_AcqAxiSetBufferSamples(rp.RP_CH_1, g_adc_axi_start, BUFFER_SIZE)

# Enable DMA on Channel 1
rp.rp_AcqAxiEnable(rp.RP_CH_1, True)
print("DMA enabled for Channel 1.\n")

# Set trigger
rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, TRIGGER_LEVEL)
rp.rp_AcqSetTriggerSrc(rp.RP_TRIG_SRC_CHA_PE)

# Open CSV file for writing
with open("acquisition_data.csv", "w", newline="", encoding="ascii") as csvfile:
    csv_writer = csv.writer(csvfile)

    # Allocate memory for the raw data
    buff_ch1 = rp.i16Buffer(BUFFER_SIZE)

    # Start acquisition
    rp.rp_AcqStart()
    print("Acquisition started.\n")

    read_position = g_adc_axi_start  # Start reading from the beginning of the buffer

    for buffer_idx in range(NUM_BUFFERS):
        # Wait for buffer to fill
        while not rp.rp_AcqAxiGetBufferFillState(rp.RP_CH_1)[1]:
            pass

        # Acquire raw data
        rp.rp_AcqAxiGetDataRaw(rp.RP_CH_1, read_position, BUFFER_SIZE, buff_ch1.cast())

        # Write raw data to CSV
        for i in range(BUFFER_SIZE):
            csv_writer.writerow([buff_ch1[i]])

        print(f"Captured buffer {buffer_idx + 1}/{NUM_BUFFERS}.\n")

        # Increment the read position to the next buffer
        read_position += BUFFER_SIZE * 2  # Multiply by 2 because samples are 16-bit (2 bytes each)
        if read_position >= (g_adc_axi_start + g_adc_axi_size):
            read_position = g_adc_axi_start  # Wrap around if exceeding the allocated memory

    print(f"Saved data to acquisition_data.csv.\n")

# Stop acquisition
rp.rp_AcqStop()
print("DMA acquisition stopped.\n")

# Release resources
print("\nReleasing resources\n")
rp.rp_AcqAxiEnable(rp.RP_CH_1, False)
rp.rp_Release()

