import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks # Import find_peaks
import json
from lmfit.models import BreitWignerModel, LinearModel


class SweepSegment:
    def __init__(self, cavity_segment, ramp_segment, frequency_segment, time_segment):
        self.ramp = ramp_segment
        self.cavity = cavity_segment
        self.frequency = frequency_segment
        self.time = time_segment
        self.mean_time = np.mean(time_segment)
        self.reversed = False
        self.quality_factor = 0
        self.result = None
        self.center = self.frequency[np.argmin(self.cavity)]
        if self.ramp[0] > self.ramp[-1]:
            self.frequency = self.frequency[::-1]
            #self.cavity = self.cavity[::-1]
            self.reversed = True

    def fit_fano(self, plot=False):
        model = BreitWignerModel() + LinearModel()
        #self.cavity = self.cavity[250:]
        #self.frequency = self.frequency[250:]
        x_arr = self.frequency - self.frequency[0]
        self.result = model.fit(self.cavity, x=x_arr,
                            center=x_arr[np.argmin(self.cavity)],
                            amplitude=np.max(self.cavity) - np.min(self.cavity), q=0.05, sigma=1, intercept=3, slope=.01)

        self.fit_report = self.result.fit_report()
        self.best_values = self.result.best_values
        if plot:
            print(self.fit_report)
            #plt.plot(self.frequency, self.cavity, label='Cavity', color='cornflowerblue')
            plt.plot(x_arr, self.cavity, label='Cavity', color='cornflowerblue')
            plt.plot( x_arr, self.result.best_fit, 'k--', label='Fit')
            #plt.plot( self.frequency, self.result.best_fit, 'k--', label='Fit')
            plt.xlabel("Freq")
            plt.ylabel("Intensity (a.u.)")
            plt.legend()
            plt.tight_layout()
            plt.show()

    def calculate_quality_factor(self):
        self.quality_factor = self.frequency[np.argmin(self.cavity)]/self.best_values["sigma"]
        #self.quality_factor = self.best_values["center"]/self.best_values["q"]


class ResonanceAnalyzer:
    def __init__(self, path, sweep_width, start_freq=0.0):
        self.sweep_width = sweep_width
        self.start_freq = start_freq
        self.path = path
        self.data, self.samplerate = sf.read(self.path)
        self.cavity = self.data[:, 0]
        self.ramp = self.data[:, 1]
        self.time = np.arange(len(self.data)) / self.samplerate  # Compute time axis\
        self.frequency = np.linspace(start_freq, start_freq+sweep_width, num=len(self.cavity))
        self.segments = []
        self.fit_arrays = dict()

        print(f"Capture was {self.time[-1]} seconds long")
        print(f"Center freq of {np.mean(self.frequency)} GHz")

    def convert_to_voltage(self):
        self.cavity = self.cavity * 20
        self.ramp = self.ramp * 200

    def segment_capture_data(self, plot_segments=[], distance=300, window_size=100):
        kernel = np.ones(int(window_size/8)) / window_size
        ramp = np.convolve(self.ramp, kernel, mode='valid')
        peak_indices, _ = find_peaks(ramp, distance=distance/8) # distance=1 means strict local maxima
        valley_indices, _ = find_peaks(-ramp, distance=distance/8) # distance=1 means strict local minima

        turning_point_indices = np.union1d(peak_indices, valley_indices)
        turning_point_indices = np.union1d(turning_point_indices, [0, len(ramp) - 1])
        turning_point_indices = np.sort(turning_point_indices).astype(int)

        for i in range(len(turning_point_indices) - 1):
            start_idx = turning_point_indices[i]
            end_idx = turning_point_indices[i+1]
            ramp_segment = ramp[start_idx : end_idx + 1].tolist()
            cavity_segment = self.cavity[start_idx: end_idx + 1].tolist()
            frequency_segment = np.linspace(self.start_freq, self.start_freq + self.sweep_width,
                                            num=len(cavity_segment))
            time_segment = self.time[start_idx: end_idx +1].tolist()
            if np.max(ramp_segment) - np.min(ramp_segment) > 2.5 and ramp_segment[0] < ramp_segment[-1]:
                self.segments.append(SweepSegment(cavity_segment, ramp_segment, frequency_segment, time_segment))

        for i in plot_segments:
            plt.plot(self.segments[i].ramp)
            plt.plot(self.segments[i].cavity)
            plt.show()

    def fit_fano(self, fit_segments=[], plot=False):
        for segment_idx in fit_segments:
            segment = self.segments[segment_idx]
            segment.fit_fano(plot=plot)

    def construct_fit_array(self, collect_segments=[]):
        #self.fit_arrays["c"] = []
        self.fit_arrays["amplitude"] = []
        self.fit_arrays["center"] = []
        self.fit_arrays["sigma"] = []
        self.fit_arrays["q"] = []
        self.fit_arrays["segments"] = collect_segments
        for collect_idx in collect_segments:
            segment = self.segments[collect_idx]
            #self.fit_arrays["c"].append(segment.best_values["c"])
            self.fit_arrays["amplitude"].append(segment.best_values["amplitude"])
            self.fit_arrays["center"].append(segment.best_values["center"] + segment.frequency[0])
            self.fit_arrays["sigma"].append(segment.best_values["sigma"])
            self.fit_arrays["q"].append(segment.best_values["q"])

    def construct_r_squared_array(self, collect_segments=[]):
        self.r_squareds = []
        for segment_idx in collect_segments:
            segment = self.segments[segment_idx]
            self.r_squareds.append(segment.result.rsquared)

    def construct_quality_factor_array(self, collect_segments=[]):
        self.quality_factors = []
        for segment_idx in collect_segments:
            segment = self.segments[segment_idx]
            segment.calculate_quality_factor()
            self.quality_factors.append(segment.quality_factor)

    def construct_mean_time_array(self, collect_segments=[]):
        self.mean_times = []
        for segment_idx in collect_segments:
            segment = self.segments[segment_idx]
            self.mean_times.append(segment.mean_time)

    def construct_center_array(self, collect_segments=[]):
        self.centers = []
        for segment_idx in collect_segments:
            segment = self.segments[segment_idx]
            self.centers.append(segment.center)

    #def plot_c(self):
    #    plt.figure()
    #    plt.plot(self.mean_times, self.fit_arrays["c"])
    #    plt.title("c for each segment")
    #    plt.xlabel("Segment Number")
    #    plt.ylabel("Best fit c value")

    def plot_amplitude(self):
        plt.figure()
        plt.plot(self.mean_times, self.fit_arrays["amplitude"])
        plt.title("Amplitude for each segment")
        plt.xlabel("Segment Number")
        plt.ylabel("Best fit amplitude value")

    def plot_fit_center(self):
        plt.figure()
        plt.plot(self.mean_times, self.fit_arrays["center"])
        plt.title("Center over time")
        plt.xlabel("Seconds")
        plt.ylabel("Best fit center value")

    def plot_center(self):
        plt.figure()
        plt.plot(self.mean_times, self.fit_arrays["center"])
        plt.title("Center over time")
        plt.xlabel("Seconds")
        plt.ylabel("Center Freq")

    def plot_sigma(self):
        plt.figure()
        plt.plot(self.mean_times, self.fit_arrays["sigma"])
        plt.title("Sigma over time")
        plt.xlabel("Seconds")
        plt.ylabel("Best fit sigma value")

    def plot_q(self):
        plt.figure()
        plt.plot(self.mean_times, self.fit_arrays["q"])
        plt.title("Q over time")
        plt.xlabel("Seconds")
        plt.ylabel("Best fit q value")

    def plot_r_squared(self):
        plt.figure()
        plt.plot(self.r_squareds)
        plt.ylabel("Fit r-squared")
        plt.title("Quality of fit over time")
        plt.xlabel("Time")

    def plot_quality_factor(self):
        plt.figure()
        plt.plot(self.mean_times, self.quality_factors)
        plt.title("Quality factor over time")
        plt.xlabel("Seconds")
        plt.ylabel("Quality Factor")

    def run_analysis(self, target_segments=None, plot_segment=False, plot_fit=False):
        self.convert_to_voltage()
        self.segment_capture_data()
        print(f"{len(self.segments)} segments found")
        if target_segments is None:
            target_segments = [i for i in range(len(self.segments))]

        if plot_segment:
            analyzer.segment_capture_data(plot_segments=target_segments)
        self.fit_fano(fit_segments=target_segments, plot=plot_fit)
        self.construct_fit_array(collect_segments=target_segments)
        self.construct_quality_factor_array(collect_segments=target_segments)
        self.construct_mean_time_array(collect_segments=target_segments)
        self.construct_r_squared_array(collect_segments=target_segments)
        self.construct_center_array(collect_segments=target_segments)

#analyzer = ResonanceAnalyzer("ResonanceCaptures/Saves/Capture4.wav", 30, start_freq=209.6e3)
sigmas = []
with open("ResonanceCaptures/Saves/metadata.json") as f:
    data = json.load(f)
for target_file in ["8"]:
    target_data = data[target_file]
    analyzer = ResonanceAnalyzer(f"ResonanceCaptures/Saves/{target_file}.wav", target_data["stop_freq"]-target_data["start_freq"],
                                 start_freq=target_data["start_freq"])
    #target_segments = [i for i in range(0, 15)]
    target_segments=None
    analyzer.run_analysis(target_segments, plot_fit=False)

    ## Plotting
    #analyzer.plot_c()
    # The fano-ness of it. positive -> left side lower
    #analyzer.plot_q()
    #analyzer.plot_amplitude()
    analyzer.plot_center()
    analyzer.plot_quality_factor()
    analyzer.plot_r_squared()
    #FWHM
    analyzer.plot_sigma()
    sigmas.append(np.mean(analyzer.fit_arrays["sigma"]))
    plt.show()


