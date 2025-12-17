import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from load_trial_data_from_pid import load_trial_data_for_pid
from scipy import signal

participants = ["IR97", "IR99", "BJH008", "OS57", "BJH010", "BJH016", 
               "SLCH002", "BJH017", "BJH018", "OS63", "SLCH006", "BJH021"] 
OUTCOMES = ['nmb', 'nma', 'hit', 'fm']


def load_all_participants(band, region):
    big_dict = { outcome: {} for outcome in OUTCOMES }
    for pid in participants:
        data = load_trial_data_for_pid(pid, band, region)
        for outcome, elec_dict in data.items():
            for elec, arr in elec_dict.items():
                new_key = f"{pid}_{elec}"
                mean_arr = arr.mean(axis = 0)
                filtered_arr = signal.savgol_filter(mean_arr, 61, 1)
                final_arr = filtered_arr[2500:5001]
                big_dict[outcome][new_key] = final_arr
    return big_dict

        
def averaging_electrodes(band, region):
    averaged_outcomes = { outcome: {} for outcome in OUTCOMES} # keys are outcomes, values are an array with shape (n_tps,)
    big_dict = load_all_participants(band, region)

    for outcome, elec_dict in big_dict.items():
        averaged_trials = [] # list of arrays (shape = n_tps) for each electrode
        for array in elec_dict.values():
            averaged_trials.append(array)
        averaged_trials = np.stack(averaged_trials, axis = 0) # convert list to array 
        print(averaged_trials.shape) # check, should be 2D with shape as (# of electrodes, # tps)
        averaged_outcomes[outcome] = averaged_trials.mean(axis=0) # average across electrodes

    return averaged_outcomes

def extracting_pvalues(region):
    pvalues_df = pd.read_csv(f'/home/knight/jharrell/hfa_per_outcome_csvs/pvalues/{region}_pvalues.csv')
    mask = pvalues_df['fdr'] < 0.05
    sig_per_tp = np.repeat(mask.values, 5)[:2501]

    return sig_per_tp


def plotting(band, region):
    colors = ['yellow', 'purple', 'red', 'green']
    condition_data = averaging_electrodes(band, region)
    sig_tps = extracting_pvalues(region)
    n_times = len(next(iter(condition_data.values())))
    time = np.linspace(-3, 2, n_times)
    
    plt.figure(figsize=(10, 5))

    for (outcome, values), color in zip(condition_data.items(), colors):
        plt.plot(time, values, label=outcome, color=color, linewidth=2)

    ymin, ymax = plt.ylim()

    plt.fill_between(
        time,
        ymin,
        ymax,
        where=sig_tps,   
        color='black',
        alpha=0.15,         
        linewidth=0)


    plt.axvline(0, color='black', linestyle='--', linewidth=1)
    plt.xlabel("Time (s)")
    plt.title(f"HFA in {region} per outcome")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"/home/knight/jharrell/scripts/hfa_outcome_significance_{region}.png")
