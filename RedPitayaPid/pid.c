#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

// Define the base address of the PID block
#define PID_BASE_ADDR 0x40300000

// Define offsets for PID11 parameters
#define PID11_SP_OFFSET  0x10 // Setpoint
#define PID11_KP_OFFSET  0x14 // Proportional gain
#define PID11_KI_OFFSET  0x18 // Integral gain
#define PID11_KD_OFFSET  0x1C // Derivative gain
#define PID_RESET_OFFSET 0x00 // Integrator reset control

// Define scaling factor for the PID coefficients
#define SCALING_FACTOR 16384  // 2^14

// Function to write a value to a register
void write_register(volatile unsigned *map_base, off_t offset, unsigned value) {
    *(map_base + offset / sizeof(unsigned)) = value;
}

// Function to read a value from a register (optional for verification)
unsigned read_register(volatile unsigned *map_base, off_t offset) {
    return *(map_base + offset / sizeof(unsigned));
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <Kp> <Ki> <Kd>\n", argv[0]);
        fprintf(stderr, "Each parameter must be a signed integer between -8196 and 8196.\n");
        return EXIT_FAILURE;
    }

    // Parse command-line arguments as signed integers
    int kp = atoi(argv[1]);
    int ki = atoi(argv[2]);
    int kd = atoi(argv[3]);

    // Validate the range of inputs
    if (kp < -8196 || kp > 8196 || ki < -8196 || ki > 8196 || kd < -8196 || kd > 8196) {
        fprintf(stderr, "Error: All parameters must be in the range -8196 to 8196.\n");
        return EXIT_FAILURE;
    }

    // Hardcoded setpoint
    const int setpoint = 1639; 

    int fd;
    volatile unsigned *map_base;

    // Open /dev/mem
    fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd == -1) {
        perror("Error opening /dev/mem");
        return EXIT_FAILURE;
    }

    // Map the PID module's address space
    map_base = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, PID_BASE_ADDR);
    if (map_base == MAP_FAILED) {
        perror("Error mapping memory");
        close(fd);
        return EXIT_FAILURE;
    }

    // Reset integrator
    write_register(map_base, PID_RESET_OFFSET, 0x1); // Set reset
    write_register(map_base, PID_RESET_OFFSET, 0x0); // Clear reset

    // Write PID parameters
    write_register(map_base, PID11_SP_OFFSET, setpoint);
    write_register(map_base, PID11_KP_OFFSET, (unsigned)kp);
    write_register(map_base, PID11_KI_OFFSET, (unsigned)ki);
    write_register(map_base, PID11_KD_OFFSET, (unsigned)kd);

    // Verify the written values (optional)
    //printf("\nWritten Values:\n");
    //printf("Setpoint: 0x%X\n", read_register(map_base, PID11_SP_OFFSET));
    //printf("Kp: 0x%X\n", read_register(map_base, PID11_KP_OFFSET));
    //printf("Ki: 0x%X\n", read_register(map_base, PID11_KI_OFFSET));
    //printf("Kd: 0x%X\n", read_register(map_base, PID11_KD_OFFSET));

    // Unmap memory and close /dev/mem
    if (munmap((void *)map_base, 4096) == -1) {
        perror("Error unmapping memory");
    }
    close(fd);

    return EXIT_SUCCESS;
}

