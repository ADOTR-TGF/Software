import math


def trace_summary(trace, x_limits, adc_sr=1.0):
    """
    Analayse a trace within x_limits and return pulse shape data and baseline noise data
    :param trace: ADC samples
    :param x_limits: [x0, x1] in ADC sample number
    :param adc_sr: ADC sampling rate
    :return:
    """
    analysis = {'pulse_found': '-1'}
    trace = trace[int(x_limits[0]): int(x_limits[1])]
    thr = 10
    b_thr = 3
    dc_val = trace[0]
    n0 = 0
    n1 = 0
    n_trig = n0
    for n0, t in enumerate(trace[1:]):
        if abs(t - dc_val) < b_thr:
            dc_val = 7 / 8 * dc_val + t / 8
        elif (t - dc_val) > thr:
            n_trig = n0+1
            break
    else:  # no pulse found
        tlen = len(trace)
        avg = sum(trace) / tlen
        std_dev = math.sqrt(sum([(t - avg) ** 2 for t in trace]) / (tlen - 1))
        mini = min(trace)
        maxi = max(trace)
        analysis = {'pulse_found': 0, 'mini': mini, 'maxi': maxi, 'std_dev': std_dev, "avg": avg}
        return analysis

    if n0 > 3:
        avg = sum(trace[1:n0-1]) / (n0-2)
        std_dev = math.sqrt(sum([(t - avg) ** 2 / (n0-3) for t in trace[1:n0-1]]))
    else:
        std_dev = 0
            
    energy = 0
    for n1, t in enumerate(trace[n0:]):
        energy += t
        if n1 > 2 and t - dc_val < b_thr:
            break

    pulse = [t-dc_val for t in trace]
    ymax = max(pulse)
    xmax = pulse.index(ymax)

    n_max = len(trace)
    cut_off = b_thr
    y10 = max(0.1 * ymax, cut_off)
    y50 = max(0.5 * ymax, cut_off)
    y90 = max(0.9 * ymax, cut_off)
    x90_left = 0
    x50_left = 0
    x10_left = 0
    xb_left = 0
    x90_right = n_max
    x50_right = n_max
    x10_right = n_max
    xb_right = n_max

    for n in range(xmax, 0, -1):
        if pulse[n] <= y90:
            x90_left = n
            break
    for n in range(xmax, 0, -1):
        if pulse[n] <= y50:
            x50_left = n
            break
    for n in range(xmax, 0, -1):
        if pulse[n] <= y10:
            x10_left = n
            break
    for n in range(xmax, 0, -1):
        if pulse[n] <= cut_off:
            xb_left = n
            break

    for n in range(xmax, n_max):
        if pulse[n] <= y90:
            x90_right = n
            break
    for n in range(xmax, n_max):
        if pulse[n] <= y50:
            x50_right = n
            break
    for n in range(xmax, n_max):
        if pulse[n] <= y10:
            x10_right = n
            break
    for n in range(xmax, n_max):
        if pulse[n] <= cut_off:
            xb_right = n
            break
    # print(x90_left, x50_left, x10_left, xb_left, x90_right, x50_right, x10_right, xb_right, y10, y50, y90)
    rise_time = (x90_left - x10_left - 1) / adc_sr
    fall_time = (x10_right - x90_right - 1) / adc_sr
    peaking_time = (xmax - xb_left) / adc_sr
    fwhm = (x50_right - x50_left) / adc_sr

    # For now we remove 'mca_bin': mca_bin, from the analysis output
    analysis = {'pulse_found': 1, 'xtrig': (n_trig+int(x_limits[0]))/adc_sr,
                'amplitude': ymax, 'rise_time': rise_time,
                'peaking_time': peaking_time, 'fall_time': fall_time,
                'fwhm': fwhm, 'dc_val': dc_val, 'std_dev': std_dev}

    return analysis
