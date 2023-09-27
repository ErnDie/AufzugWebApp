import json
from datetime import datetime, timedelta
import string
import numpy as np


class Latency:

    def __init__(self):
        self.rtt_list = []

    def start(self):
        self.start_time_rtt = datetime.now()
        print(self.start_time_rtt)

    def calculateLatency(self):
        self.end_time_rtt = datetime.now()
        print(self.end_time_rtt)
        self.rtt = self._calculateRTT(self.end_time_rtt - self.start_time_rtt)
        self.rtt_list.append(self.rtt)
        print(len(self.rtt_list))

    def printLatency(self):
        print("RTT: " + str(self.rtt) + "s")

    def _string_to_timedelta(self, time_str):
        parts = time_str.split(':')
        seconds_part = parts[-1].split('.')

        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(seconds_part[0])
        microseconds = int(seconds_part[1])

        time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
        return time_delta

    def _calculateRTT(self, timeDelta: timedelta):
        print(timeDelta)
        # If you use timedelta.microseconds the 0 at the beginning will be cut
        microSecondsString = str(timeDelta).split('.')[1]
        rtt = float(str(timeDelta.seconds) + "." + microSecondsString)
        return rtt


    def calculateRTTMetrics(self):
        rtt_sorted = self.rtt_list.copy()
        rtt_sorted.sort()
        self.rtt_max = rtt_sorted[-1]
        self.rtt_min = rtt_sorted[0]
        self.rtt_mean_interval = round(float(np.mean(self.rtt_list)), 6)
        self.rtt_std_deviation = round(float(np.std(self.rtt_list)), 6)
        self.rtt_25_quantil = np.quantile(self.rtt_list, .25)
        self.rtt_75_quantil = np.quantile(self.rtt_list, .75)
        self.rtt_average = round(float(np.average(self.rtt_list)), 6)


    def calculateRTTJitter(self):
        self.jitter_intervals = [round(abs(self.rtt_list[i] - self.rtt_list[i - 1]), 6) for i in
                                 range(1, len(self.rtt_list))]
        self.jitter_mean_interval = round(float(np.mean(self.jitter_intervals)), 6)
        self.jitter_std_deviation = round(float(np.std(self.jitter_intervals)), 6)
        time_intervals_sorted = self.jitter_intervals.copy()
        time_intervals_sorted.sort()
        self.jitter_max = time_intervals_sorted[-1]
        self.jitter_min = time_intervals_sorted[0]
        self.jitter_25_quantil = np.quantile(self.jitter_intervals, .25)
        self.jitter_75_quantil = np.quantile(self.jitter_intervals, .75)
        self.jitter_average = round(float(np.average(self.jitter_intervals)), 6)

    def saveAsJSON(self):
        time = 30
        json_object = []
        for rtt in self.rtt_list:
            dic = {"seconds": time, "latency": rtt, "latency_type": "rtt"}
            json_object.append(dic)
            time = time + 30

        time = 60
        for jitter in self.jitter_intervals:
            dic = {"seconds": time, "latency": jitter, "latency_type": "jitter"}
            json_object.append(dic)
            time = time + 30


        with open("sample.json", "w") as outfile:
            json.dump(json_object, outfile)

    def saveMetricsAsTxt(self):
        result = "RTT-Ergebnisse: " + ','.join(map(str, self.rtt_list)) + "\n"
        result += "RTT-Min: " + str(self.rtt_min) + "\n"
        result += "RTT-Max: " + str(self.rtt_max) + "\n"
        result += "RTT-25%-Quartil: " + str(self.rtt_25_quantil) + "\n"
        result += "Mean: " + str(self.rtt_mean_interval) + "\n"
        result += "RTT-75%-Quartil: " + str(self.rtt_75_quantil) + "\n"
        result += "RTT-Durchschnitt: " + str(self.rtt_average) + "\n"
        result += "RTT-Standardabweichung: " + str(self.rtt_std_deviation) + "\n\n"

        result += "Jitter-Ergebnisse: " + ','.join(map(str, self.jitter_intervals)) + "\n"
        result += "Jitter-Min: " + str(self.jitter_min) + "\n"
        result += "Jitter-Max: " + str(self.jitter_max) + "\n"
        result += "Jitter-25%-Quartil: " + str(self.jitter_25_quantil) + "\n"
        result += "Jitter-Mean: " + str(self.jitter_mean_interval) + "\n"
        result += "Jitter-75%-Quartil: " + str(self.jitter_75_quantil) + "\n"
        result += "Jitter-Durchschnitt: " + str(self.jitter_average) + "\n"
        result += "Jitter-Standardabweichung: " + str(self.jitter_std_deviation) + "\n\n"

        with open("metrics.txt", "w") as outfile:
            outfile.write(result)

