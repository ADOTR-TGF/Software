import json
import os

def lm_to_lists(data_file):
    energies = []
    times = []
    short_sums = []
    e_histo = [0]*4096
    try:
        with open(data_file, 'r') as fin:
            for line in fin:
                data = json.loads(line)
                energies += data["energies"]
                times += data["times"]
                if "short_sums" in data:
                    short_sums += data["short_sums"]
            for e in energies:
                e_histo[int(e)] += 1
    except:
        print("Data file {} not found.".format(data_file))
        energies = [0,1]
        times = [0,1]
        short_sums = [0,1]

    if len(energies) == 0:
        print("Empty data file")
        energies = [0,1]
        times = [0,1]
        short_sums = [0,1]
    return energies, times, short_sums, e_histo

