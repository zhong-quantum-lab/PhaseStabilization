deltaL = 10 #M
c = 3e8 #M/s
center_freq = c/1550e-9 #Hz
freq_shift = 1e3 #Hz
dPhi = ((center_freq + freq_shift)* deltaL/c)% (2 * 3.1415)
print(dPhi)