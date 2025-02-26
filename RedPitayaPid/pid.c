#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

// Base address of the PID block
#define PID_BASE_ADDR 0x40300000

// Offsets for PID11 parameters
#define PID11_SP_OFFSET  0x10 // Setpoint
#define PID11_KP_OFFSET  0x14 // Proportional gain
#define PID11_KI_OFFSET  0x18 // Integral gain
#define PID11_KD_OFFSET  0x1C // Derivative gain
#define PID11_RESET_OFFSET 0x00 // Integrator reset control

// Offsets for PID12 parameters
#define PID12_SP_OFFSET  0x20 // Setpoint
#define PID12_KP_OFFSET  0x24 // Proportional gain
#define PID12_KI_OFFSET  0x28 // Integral gain
#define PID12_KD_OFFSET  0x2C // Derivative gain
#define PID12_RESET_OFFSET 0x01 // Integrator reset control

// Offsets for PID21 parameters
#define PID21_SP_OFFSET  0x30 // Setpoint
#define PID21_KP_OFFSET  0x34 // Proportional gain
#define PID21_KI_OFFSET  0x38 // Integral gain
#define PID21_KD_OFFSET  0x3C // Derivative gain
#define PID21_RESET_OFFSET 0x02 // Integrator reset control

// Offsets for PID22 parameters
#define PID22_SP_OFFSET  0x40 // Setpoint
#define PID22_KP_OFFSET  0x44 // Proportional gain
#define PID22_KI_OFFSET  0x48 // Integral gain
#define PID22_KD_OFFSET  0x4C // Derivative gain
#define PID22_RESET_OFFSET 0x03 // Integrator reset control

// Function to write a value to a register
void write_register(volatile unsigned *map_base, off_t offset, unsigned value) {
    *(map_base + offset / sizeof(unsigned)) = value;
}

void display_help(const char *prog_name) {
    printf("Usage: %s <channel> <Kp> <Ki> <Kd> <Setpoint>\n", prog_name);
    printf("  <channel>  : PID channel (11, 12, 21, or 22)\n");
    printf("  <Kp>       : Proportional gain (signed integer between -8192 and 8192)\n");
    printf("  <Ki>       : Integral gain (signed integer between -8192 and 8192)\n");
    printf("  <Kd>       : Derivative gain (signed integer between -8192 and 8192)\n");
    printf("  <Setpoint> : Setpoint value (signed integer between -8192 and 8192)\n");
    printf("Each parameter corresponds to a voltage range of -1V to 1V.\n");
}

int main(int argc, char *argv[]) {
    if (argc == 2 && strcmp(argv[1], "-help") == 0) {
        display_help(argv[0]);
        return EXIT_SUCCESS;
    }

    if (argc != 6) {
        fprintf(stderr, "Error: Incorrect number of arguments.\n");
        display_help(argv[0]);
        return EXIT_FAILURE;
    }

    // Parse the channel argument
    int channel = atoi(argv[1]);
    off_t sp_offset, kp_offset, ki_offset, kd_offset, reset_offset;

    switch (channel) {
        case 11:
            sp_offset = PID11_SP_OFFSET;
            kp_offset = PID11_KP_OFFSET;
            ki_offset = PID11_KI_OFFSET;
            kd_offset = PID11_KD_OFFSET;
            reset_offset = PID11_RESET_OFFSET;
            break;
        case 12:
            sp_offset = PID12_SP_OFFSET;
            kp_offset = PID12_KP_OFFSET;
            ki_offset = PID12_KI_OFFSET;
            kd_offset = PID12_KD_OFFSET;
            reset_offset = PID12_RESET_OFFSET;
            break;
        case 21:
            sp_offset = PID21_SP_OFFSET;
            kp_offset = PID21_KP_OFFSET;
            ki_offset = PID21_KI_OFFSET;
            kd_offset = PID21_KD_OFFSET;
            reset_offset = PID21_RESET_OFFSET;
            break;
        case 22:
            sp_offset = PID22_SP_OFFSET;
            kp_offset = PID22_KP_OFFSET;
            ki_offset = PID22_KI_OFFSET;
            kd_offset = PID22_KD_OFFSET;
            reset_offset = PID22_RESET_OFFSET;
            break;
        default:
            fprintf(stderr, "Error: Invalid channel. Choose from 11, 12, 21, or 22.\n");
            return EXIT_FAILURE;
    }

    // Parse PID parameters as signed integers
    int kp = atoi(argv[2]);
    int ki = atoi(argv[3]);
    int kd = atoi(argv[4]);
    int setpoint = atoi(argv[5]);

    if (kp < -8196 || kp > 8196 || ki < -8196 || ki > 8196 || kd < -8196 || kd > 8196) {
        fprintf(stderr, "Error: Kp, Ki, and Kd must be in the range -8196 to 8196.\n");
        return EXIT_FAILURE;
    }

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
    write_register(map_base, reset_offset, 0x1); // Set reset
    write_register(map_base, reset_offset, 0x0); // Clear reset

    // Write PID parameters
    write_register(map_base, sp_offset, (unsigned)setpoint);
    write_register(map_base, kp_offset, (unsigned)kp);
    write_register(map_base, ki_offset, (unsigned)ki);
    write_register(map_base, kd_offset, (unsigned)kd);

    // Unmap memory and close /dev/mem
    if (munmap((void *)map_base, 4096) == -1) {
        perror("Error unmapping memory");
    }
    close(fd);
    return EXIT_SUCCESS;
}