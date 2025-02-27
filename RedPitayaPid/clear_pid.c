#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

// Define the base address of the PID block
#define PID_BASE_ADDR 0x40300000

// Define offsets for PID parameters
#define PID_SP_OFFSET  0x10 // Setpoint
#define PID_KP_OFFSET  0x14 // Proportional gain
#define PID_KI_OFFSET  0x18 // Integral gain
#define PID_KD_OFFSET  0x1C // Derivative gain
#define PID_RESET_OFFSET 0x00 // Integrator reset control

// Function to write a value to a register
void write_register(volatile unsigned *map_base, off_t offset, unsigned value) {
    *(map_base + offset / sizeof(unsigned)) = value;
}

// Function to read a value from a register (optional for verification)
unsigned read_register(volatile unsigned *map_base, off_t offset) {
    return *(map_base + offset / sizeof(unsigned));
}

int main() {
    int fd;
    volatile unsigned *map_base;
    unsigned setpoint = 0x0000;
    unsigned kp = 0x0000;
    unsigned ki = 0x0000;
    unsigned kd = 0x0000;

    // Open /dev/mem
    fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd == -1) {
        perror("Error opening /dev/mem");
        return EXIT_FAILURE;
    }

    // Iterate over the four PID controllers
    for (int i = 1; i <= 4; i++) {
        off_t pid_addr = PID_BASE_ADDR + (i * 0x10000); // Map PID11 to PID14

        // Map the PID module's address space
        map_base = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, pid_addr);
        if (map_base == MAP_FAILED) {
            perror("Error mapping memory");
            close(fd);
            return EXIT_FAILURE;
        }

        // Reset integrator
        write_register(map_base, PID_RESET_OFFSET, 0x1); // Set reset
        write_register(map_base, PID_RESET_OFFSET, 0x0); // Clear reset

        // Write PID parameters
        write_register(map_base, PID_SP_OFFSET, setpoint);
        write_register(map_base, PID_KP_OFFSET, kp);
        write_register(map_base, PID_KI_OFFSET, ki);
        write_register(map_base, PID_KD_OFFSET, kd);

        // Verify the written values (optional)
        printf("PID%d Setpoint: 0x%X\n", i, read_register(map_base, PID_SP_OFFSET));
        printf("PID%d Kp: 0x%X\n", i, read_register(map_base, PID_KP_OFFSET));
        printf("PID%d Ki: 0x%X\n", i, read_register(map_base, PID_KI_OFFSET));
        printf("PID%d Kd: 0x%X\n", i, read_register(map_base, PID_KD_OFFSET));

        // Unmap memory
        if (munmap((void *)map_base, 4096) == -1) {
            perror("Error unmapping memory");
        }
    }

    // Close /dev/mem
    close(fd);
    return EXIT_SUCCESS;
}
