# import matplotlib as plt
import matplotlib.pyplot as plt 
import numpy as np
reward = [100.86770226012172, 100.868, -5575.914645548616, 4630.44710351378, -7421.436763020219, 2792.647571528817, -1393.564, -640.5747190486701, -2564.102503491026, -1602.339, -7808.563186148895, -7800.225588276536, 6297.894719607774, -5240.71668895827, -3637.903, -1547.488952145644, -4663.777789566785, -3105.633, 782.0011874281523, -1096.6943980969436, -157.347, 4326.123567533084, 2660.3925708794695, 3493.258, -2748.0009410223056, -4834.324248517661, -2293.013020925636, -3291.779,
            4441.86507646778, 712.1030402096517, 2576.984, -5788.871182506552, -7994.289927301427, -6891.581, -4630.886768539453, -8431.570989289014, -968.1875146498639, -4676.882, -2848.4301420063416, -2859.478711645183, -2853.954, -7845.344800232706, -5164.708236835864, -6505.027, -2981.1853952278925, 936.9697388423102, -1022.108, -5107.122265609277, -17243.989322594676, -14550.018469177954, -12300.377, 2791.069968791857, 9450.124598188859, 6400.5323273147305, -5700.98201113508, 3235.186,
            -13920.286620412173, -6864.220270601203, 9573.9660367179, -3736.847, 3224.7073443704494]

meanq = [755.965, 917.614, 783.258, 477.811, 442.281, 440.022, 446.133, 460.746, 468.599, 448.821, 446.392, 368.691, 368.832, 343.411, 321.541, 307.700, 317.487]

meanq2 = [220.048, 912.534, 1005.201, 970.794, 848.333, 746.988, 738.895, 795.413, 820.254, 831.510, 750.946, 737.483, 741.147, 768.219, 794.175, 781.133, 775.574, 924.133, 951.194, 996.900, 974.589, 981.699, 930.616, 913.996, 831.955, 739.034, 705.053, 670.695, 689.278, 712.620, 674.930, 649.260, 687.700, 687.225, 699.392, 765.399, 867.028, 959.375, 966.659, 980.818, 993.678, 1012.047, 1004.440, 847.503, 687.122, 680.428, 677.982, 671.808, 634.522, 615.759, 622.820, 624.372, 607.852, 593.438, 555.667, 549.750, 572.587, 550.692, 566.773, 551.659]

print(len(meanq2))

plt.figure(figsize=(10, 5))
plt.plot(reward, label="Episode Reward", color="b")
plt.xlabel("Episode")
plt.ylabel("Total Reward")
plt.title("Reward Progression Over Training")
plt.legend()
plt.grid()

# Save the reward progression figure
graph_path = "reward_progression.png"
plt.savefig(graph_path, dpi=300)
plt.close()  # Close the figure to avoid overlap with the next one

# Plotting the mean Q-value progression
plt.figure(figsize=(10, 5))
plt.plot(meanq, label="Episode Mean Q Value", color="b")
plt.xlabel("Intervals (10000 steps performed)")
plt.ylabel("Mean Q Value")
plt.title("Mean Q Progression Over Training")
plt.legend()
plt.grid()

# Save the mean Q-value progression figure
graph_path = "mean_q_progression.png"
plt.savefig(graph_path, dpi=300)
plt.close()  # Close the figure after saving

# Plotting the mean Q-value progression
plt.figure(figsize=(10, 5))
plt.plot(meanq2, label="Episode Mean Q Value", color="b")
plt.xlabel("Intervals (10000 steps performed)")
plt.ylabel("Mean Q Value")
plt.title("Mean Q Progression Over Training")
plt.legend()
plt.grid()

# Save the mean Q-value progression figure
graph_path = "mean_q_progression_exp1.png"
plt.savefig(graph_path, dpi=300)
plt.close()  # Close the figure after saving

# Optionally, show the plots (this will open the saved figures)
plt.show()