import numpy as np

# TODO
# calculate metrics as ratio (scalar), histogram of absolute value, or histogram (ratio)

def summed_listmode_local(indeces, values, time):
    # idk if this is the best way but its easy
    # combine values and find non zero values
    vec = np.array(np.zeros(time.size))
    for i, v in zip(indeces, values):
        vec[i] += v

    new_indeces = np.where(vec)[0]
    new_values = vec[new_indeces]
    return new_indeces, new_values


def coincident_pct(indeces_list, volts_list, time):
    """
    Pct of photons that are coincident with another over all
    """
    new_indeces, _ = summed_listmode_local(indeces_list, volts_list, time)
    coincident_photons_pct = (indeces_list.size - new_indeces.size) / indeces_list.size

    index_count = {}
    index_energy = {}
    for i, v in zip(indeces_list, volts_list):
        if i in index_count.keys():
            index_count[i] += 1
            index_energy[i] += v
        else:
            index_count[i] = 1
            index_energy[i] = v

    coincident_voltage = 0
    # print(index_count)
    # print(index_energy)
    for index in index_count.keys():
        if index_count[index] > 1:
            # print(index_count[index])
            # print(index_energy[index])
            coincident_voltage += index_energy[index]
    total_voltage = np.sum(volts_list)
    coincident_voltage_pct = coincident_voltage / total_voltage

    return coincident_photons_pct, coincident_voltage_pct

def coincident_pct_per_v(indeces_list, volts_list):
    """
    Pct of photons that are coincident
    """

    volts_x_indeces = np.zeros((indeces_list.size, volts_list.size))
    volts_x_indeces[indeces_list, volts_list] += 1
    p_per_index = np.sum(volts_x_indeces, axis=0)
    pct_per_index_per_volt = volts_x_indeces / p_per_index[:, None]  # TODO these dim might be off
    #TODO also divide by zero issues...
    return np.mean(pct_per_index_per_volt, axis=1)

def coincident_energy_per_v(indeces_list, volts_list):
    """
    Pct of photons that are coincident
    """
    volts_x_indeces = np.zeros((indeces_list.size, volts_list.size))
    volts_x_indeces[indeces_list, volts_list] += 1
    p_per_index = np.sum(volts_x_indeces, axis=0)
    pct_per_index_per_volt = volts_x_indeces / p_per_index[:, None]  # TODO these dim might be off
    return np.mean(pct_per_index_per_volt, axis=1)

def volts_counted_pct(volts_list, true_volts_list):
    return np.sum(volts_list) / np.sum(true_volts_list)

def events_counted(volts_list, true_volts_list):
    assert true_volts_list.size > 0 # we should never fail this...
    return volts_list.size /  true_volts_list.size

def volts_counted_hist(true_volts_list, volts_list, bins, range_=None):
    original_counts, original_values = np.histogram(true_volts_list, bins=bins, range=range_)
    counted_counts, counted_values = np.histogram(volts_list, bins=bins, range=range_)
    # return np.divide(counted_hist, hist)
    # TODO divide by zero isues if try to return ratio due ot sparsity...

    return original_counts, original_values, counted_counts, counted_values
