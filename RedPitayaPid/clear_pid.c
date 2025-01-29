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

    // Example values to set
    unsigned setpoint = 0x0000; 
    unsigned kp = 0x0000;       
    unsigned ki = 0x0000;       
    unsigned kd = 0x0000;       

    // Reset integrator
    write_register(map_base, PID_RESET_OFFSET, 0x1); // Set reset
    write_register(map_base, PID_RESET_OFFSET, 0x0); // Clear reset

    // Write PID11 parameters
    write_register(map_base, PID11_SP_OFFSET, setpoint);
    write_register(map_base, PID11_KP_OFFSET, kp);
    write_register(map_base, PID11_KI_OFFSET, ki);
    write_register(map_base, PID11_KD_OFFSET, kd);

    // Verify the written values (optional)
    printf("Setpoint: 0x%X\n", read_register(map_base, PID11_SP_OFFSET));
    printf("Kp: 0x%X\n", read_register(map_base, PID11_KP_OFFSET));
    printf("Ki: 0x%X\n", read_register(map_base, PID11_KI_OFFSET));
    printf("Kd: 0x%X\n", read_register(map_base, PID11_KD_OFFSET));

    // Unmap memory and close /dev/mem
    if (munmap((void *)map_base, 4096) == -1) {
        perror("Error unmapping memory");
    }
    close(fd);

    return EXIT_SUCCESS;
}

