import numpy as np 
import rp
import time
def capture_signal(num_buffers=1, buffer_size=16384, decimation=rp.RP_DEC_16384, trigger_level=0.5):
    try:
        # Initialize the Red Pitaya API
        rp.rp_Init()

        # Configure acquisition settings
        rp.rp_AcqReset()
        rp.rp_AcqSetDecimation(decimation)
        rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trigger_level)
        rp.rp_AcqSetTriggerDelay(0)  # Set trigger delay
        rp.rp_AcqSetGain(rp.RP_CH_1, rp.RP_LOW)  # Set channel gain
        rp.rp_AcqStart()  # Start acquisition

        # Allocate space for all data
        all_data = np.zeros(num_buffers * buffer_size, dtype=float)

        for buffer_index in range(num_buffers):
            # Trigger the acquisition
            #rp.rp_AcqReset()
            #rp.rp_AcqSetDecimation(decimation)
            #rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trigger_level)
            #rp.rp_AcqSetTriggerDelay(0)  # Set trigger delay
            ##rp.rp_AcqSetGain(rp.RP_CH_1, rp.RP_LOW)  # Set channel gain
            rp.rp_AcqStart()  # Start continuous acquisition
            #rp.rp_AcqSetTriggerSrc(rp.RP_TRIG_SRC_NOW)

            # Wait for the trigger
            while True:
                trig_state = rp.rp_AcqGetTriggerState()[1]
                if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
                    break

            # Wait for the buffer to be filled
            while True:
                if rp.rp_AcqGetBufferFillState()[1]:
                    break

            # Read data into the corresponding part of the array
            temp_buffer = rp.fBuffer(buffer_size)
            rp.rp_AcqGetDataV(rp.RP_CH_1, 0, buffer_size, temp_buffer)

            # Copy data into the larger array
            start_idx = buffer_index * buffer_size
            end_idx = start_idx + buffer_size
            all_data[start_idx:end_idx] = [temp_buffer[i] for i in range(buffer_size)]
        with open("acquisition_data.csv", "w") as file:
            for val in all_data:
                file.write(f"{val}\n")
        return all_data

    except Exception as e:
        print(f"Error during acquisition: {e}")
        return None

    finally:
        # Release the Red Pitaya resources
        rp.rp_Release()


def continuous_capture(num_buffers=10, buffer_size=16384, decimation=rp.RP_DEC_8192):
    try:
        # Initialize Red Pitaya API
        rp.rp_Init()

        # Configure acquisition settings
        rp.rp_AcqReset()
        rp.rp_AcqSetDecimation(decimation)
        #rp.rp_AcqSetTriggerSrc(rp.RP_TRIG_SRC_DISABLED)  # No triggering
        rp.rp_AcqStart()  # Start continuous acquisition

        # Allocate space for all data
        all_data = np.zeros(num_buffers * buffer_size, dtype=float)

        for buffer_index in range(num_buffers):
            # Read data from the buffer
            print("a)")
            time.sleep(buffer_size/125e6 * 8192)
            
            temp_buffer = rp.fBuffer(buffer_size)
            rp.rp_AcqGetDataV(rp.RP_CH_1, 0, buffer_size, temp_buffer)

            # Copy data into the larger array
            start_idx = buffer_index * buffer_size
            end_idx = start_idx + buffer_size
            all_data[start_idx:end_idx] = [temp_buffer[i] for i in range(buffer_size)]

            # Optional: Add a delay to sync with the sampling rate

        # Save data to file
        with open("acquisition_data.csv", "w") as file:
            for val in all_data:
                file.write(f"{val}\n")
        return all_data

    except Exception as e:
        print(f"Error during acquisition: {e}")
        return None

    finally:
        rp.rp_Release()  # Ensure resources are released
continuous_capture()
#capture_signal()
