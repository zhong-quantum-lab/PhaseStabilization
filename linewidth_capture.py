from remote_streaming import RP_Streamer
import matplotlib.pyplot as plt
stream = RP_Streamer("10.120.12.198", save_directory="./ResonanceCaptures")
captures = 800000
data, sample_rate = stream.capture_signal(captures)
plt.plot(data)
plt.show()

print("Done!")