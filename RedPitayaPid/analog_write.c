#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdlib.h>

#define DAC_BASE_ADDR   0x40100000  // DAC streaming base address
#define MAP_SIZE        0x1000      // Memory map size (4 KB)

// DAC register offsets based on your documentation
#define DAC_CONF_OFFSET         0x0  // Configuration register
#define DAC_CH_A_SCALE_OFFSET   0x4  // Channel A scale and offset
#define DAC_CH_B_SCALE_OFFSET   0x10 // Channel B scale and offset

// Function prototypes
void *map_registers(off_t base_address);
void unmap_registers(void *mapped_addr);
void set_dac_value(volatile uint32_t *dac_reg, char channel, uint16_t scale, uint16_t offset);

int main() {
    // Open /dev/mem
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("Error opening /dev/mem");
        return -1;
    }

    // Map DAC registers
    volatile uint32_t *dac_reg = (volatile uint32_t *)map_registers(DAC_BASE_ADDR);
    if (dac_reg == NULL) {
        close(fd);
        return -1;
    }
   
    dac_reg[4] = 0xAABBCCDD; // Write to the next register
    if (dac_reg[1] == 0xAABBCCDD) {
        printf("Write to another register succeeded.\n");
    } else {
        printf("Write to another register failed.\n");
    }

    while (1) {
        // Ask the user for an analog value between -1 and 1
        float analog_value;
        printf("Enter an analog value between -1 and 1 for DAC Channel A (Ctrl+C to exit): ");
        if (scanf("%f", &analog_value) != 1) {
            fprintf(stderr, "Invalid input. Please enter a number.\n");
            continue;
        }

        // Clamp the input value between -1 and 1
        if (analog_value < -1.0) {
            analog_value = -1.0;
        } else if (analog_value > 1.0) {
            analog_value = 1.0;
        }

        // Convert the input to scale and offset
        // Assume the DAC range is 16-bit signed (-32768 to 32767)
        int16_t dac_value = (int16_t)(analog_value * 32767);
        uint16_t scale = abs(dac_value); // Scale is the magnitude
        uint16_t offset = (dac_value < 0) ? 0xFFFF : 0x0000; // Offset for sign handling

        // Write the value to DAC Channel A
        set_dac_value(dac_reg, 'A', scale, offset);
    }

    // Unmap registers and close file descriptor
    unmap_registers((void *)dac_reg);
    close(fd);

    return 0;
}


// Maps memory-mapped registers
void *map_registers(off_t base_address) {
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("Error opening /dev/mem");
        return NULL;
    }

    void *mapped_addr = mmap(NULL, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, base_address);
    if (mapped_addr == MAP_FAILED) {
        perror("Error mapping memory");
        close(fd);
        return NULL;
    }

    close(fd);  // File descriptor no longer needed after mmap
    return mapped_addr;
}

// Unmaps memory-mapped registers
void unmap_registers(void *mapped_addr) {
    if (munmap(mapped_addr, MAP_SIZE) < 0) {
        perror("Error unmapping memory");
    }
}

// Sets DAC channel value
void set_dac_value(volatile uint32_t *dac_reg, char channel, uint16_t scale, uint16_t offset) {
    uint32_t value = (((uint32_t)offset << 16) | scale) & 0x3FFF; // Combine scale and offset
    switch (channel) {
        case 'A': // Write to Channel A scale and offset register
            dac_reg[DAC_CH_A_SCALE_OFFSET / 4] = value;
            printf("DAC Channel A set: Scale=0x%X, Offset=0x%X\n", scale, offset);
            break;
        case 'B': // Write to Channel B scale and offset register
            dac_reg[DAC_CH_B_SCALE_OFFSET / 4] = value;
            printf("DAC Channel B set: Scale=0x%X, Offset=0x%X\n", scale, offset);
            break;
        default:
            fprintf(stderr, "Invalid DAC channel specified. Use 'A' or 'B'.\n");
            break;
    }
}

