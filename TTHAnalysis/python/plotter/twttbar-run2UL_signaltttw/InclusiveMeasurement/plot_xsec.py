import matplotlib.pyplot as plt
import numpy as np

# Data
variables = [
    "dR_ll", "jet2_eta", "lep1_eta", "mindr_lep1_jet25", "njets", "jet2_pt", "lep2_pt",
    "jet1_pt", "mll", "nbjets", "njets_7bins", "jet1_eta", "sum_2lss_pt", 
    "nbjets_medium", "deta_llss", "HT"
]
xsec_values = [21.05, 17.78, 21.87, 22.90, 20.93, 21.55, 22.88, 23.67, 21.01, 24.00, 22.08, 19.94, 24.11, 28.34, 22.92, 21.25]
xsec_errors = [3.72, 5.29, 3.35, 3.95, 6.28, 3.55, 2.74, 2.77, 4.13, 1.43, 13.60, 4.27, 2.89, 32.22, 3.63, 3.54]

# Remove "nbjets" and "nbjets_medium" from the data
exclude_indices = [variables.index(var) for var in ["nbjets", "nbjets_medium", "njets_7bins"]]
variables_excluded = [var for i, var in enumerate(variables) if i not in exclude_indices]
xsec_values_excluded = [val for i, val in enumerate(xsec_values) if i not in exclude_indices]
xsec_errors_excluded = [err for i, err in enumerate(xsec_errors) if i not in exclude_indices]

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.errorbar(variables_excluded, xsec_values_excluded, yerr=xsec_errors_excluded, fmt='o', color='blue', ecolor='red', capsize=5, label="xsec ± total uncertainty")

# Customize plot
plt.ylim(5,35)
ax.set_title("Inclusive signal strength (tight method)", fontsize=14)
ax.set_xlabel("Variable", fontsize=12)
ax.set_ylabel("xsec (fb)", fontsize=12)
ax.set_xticks(range(len(variables_excluded)))
ax.set_xticklabels(variables_excluded, rotation=45, ha='right', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend()

plt.tight_layout()
fig.savefig("xsec")
