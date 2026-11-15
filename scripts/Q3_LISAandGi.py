""" GEOG41160 Assignment 2, Question 3: LISA and Gi*
Team: 6
"""
#Imports
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import libpysal
import esda 
from pathlib import Path
from matplotlib.patches import Patch
from esda.getisord import G_Local
from scipy.stats import norm

#Path Assignments
ROOT = Path.cwd().parent
OUTPUT = ROOT / "Outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)
INPUT = ROOT / "Outputs" / "DublinED_ExtensionDensity.gpkg"

eds = gpd.read_file(INPUT)
eds.head(10)

#Checking Paths
print("Working folder:", Path.cwd())
print("Repository:", ROOT)
print("Dublin Extension Application Density exists:", eds.exists)
print("Output folder:", OUTPUT)


#Assign initial variables
eds["log_density"] = np.log1p(eds["per_km2"]) 
x = eds["log_density"].values 
w = libpysal.weights.Queen.from_dataframe(eds, use_index=True) 
w.transform = "r"
np.random.seed(42)

###Part 1###
#Calculate LISA
"""1: LISA finds 112 insignificant EDs, 23 low-low clusters, 20 high-high clusters, 5 low-high outliers, and 2 high-low outliers."""
lisa = esda.Moran_Local(x, w, permutations=9999, seed=42)

quadrants = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
classes = pd.Series(lisa.q).map(quadrants)
eds["lisa_class"] = np.where(lisa.p_sim <= 0.05, classes, "Not significant")
print(eds["lisa_class"].value_counts())

###Part 2###
#Apply False Discovery Rate correction
"""2:  After the False Discovery Rate threshold, 2 EDs remain significant."""
threshold = esda.fdr(lisa.p_sim, 0.05)
print("FDR Threshold:", round(threshold, 5), "| smallest p:", lisa.p_sim.min())
print("Significant after FDR:", (lisa.p_sim <= threshold).sum())

### Part 3###
#Map LISA classes
"""3: LISA classes saved as 'LISA_ExtensionDensity_DublinED.png'"""
colours = {"High-High": "#d7191c", "Low-High": "#abd9e9", "Low-Low": "#2c7bb6", "High-Low": "#fdae61", "Not significant": "#eeeeee"}
fig, ax = plt.subplots(figsize=(7, 6))
eds.plot(color=eds["lisa_class"].map(colours), edgecolor="grey", linewidth=0.3,
         ax=ax)
ax.legend(handles=[Patch(color=c, label=f"{k}({(eds['lisa_class'] == k).sum()})") for k, c in colours.items()], loc="lower right", fontsize=8)

ax.set_title("LISA of Extension Applications, Dublin")
ax.set_axis_off()
plt.savefig(OUTPUT / "LISA_ExtensionDensity_DublinED.png", dpi=180, bbox_inches="tight")
plt.show()

###Part 4###
#Getis-Ord Gi* setup
w_bin = libpysal.weights.Queen.from_dataframe(eds, use_index=True)
gi = G_Local(x, w_bin, transform="B", star=1.0, permutations=999, seed=42) 

#Compute Gi* and find two-sided p values
eds["gi_z"] = gi.Zs
eds["gi_p"] = 2 * norm.sf(np.abs(gi.Zs))
print("Hotspots:", (eds["gi_z"] > 1.96).sum(), "| Coldspots:", (eds["gi_z"] < -1.96).sum())

#Apply FDR to two-sided p value
"""4: Getis-Ord Gi* finds 15 hotspots and 25 coldspots.  After FDR correction, 4 EDs are still significant."""
threshold = esda.fdr(eds["gi_p"].values, 0.05)
print(eds.loc[eds["gi_p"] <= threshold, ["ED_ENGLISH", "gi_z"]])
print("Significant after FDR:", (lisa.p_sim <= threshold).sum())

###Part 5###
#Define the function to fix colorbar heights as used in class
def fix_colorbar_height(fig, ax):
    cbar = fig.axes[-1] # the color bar: last axes added
    pos = ax.get_position() # map box: x0, y0, width, height
    cbar_pos = cbar.get_position()
    cbar.set_position([cbar_pos.x0, pos.y0, cbar_pos.width, pos.height])

#Map hotspots and coldspots of Gi*
"""5: Getis-Ord Gi* map saved as 'GiStar_ExtensionDensity_DublinED'."""
lim = np.abs(eds["gi_z"]).max()
fig, ax = plt.subplots(figsize=(7, 6))
eds.plot(column="gi_z",  cmap="RdBu_r", vmin=-lim, vmax=lim, legend=True, edgecolor="grey", linewidth=0.3, ax = ax,
         legend_kwds={"label": "Gi* Z-score"})
eds[eds["gi_p"] <= threshold].boundary.plot(ax=ax, color="black", linewidth=2)
ax.set_title("Getis-Ord Gi* Z-scores (outlined: significant after FDR)")
ax.set_axis_off()
fix_colorbar_height(fig, ax)
plt.savefig(OUTPUT / "GiStar_ExtensionDensity_DublinED.png", dpi=180, bbox_inches="tight")
plt.show()

###Part 6###
#Compare Gi and LISA
"""6:  When looked at in quadrants, Gi* finds 19 Hotspots compared to LISA's 20, and 15 coldspots compared to LISA's 23.
Observation of the maps shows several EDs in the Gi* which lean towards being coldspots, such as in Dublin 11, but have a Z-score too close to 0
to be counted as proper coldspots, though they count as Low-Low quadrants according to LISA."""
quadrants = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
classes = pd.Series(lisa.q).map(quadrants)
psim = 0.05
eds["gi_quad"] = np.where(
    gi.p_sim <= (psim / 2),      
    np.where(gi.Zs > 0, 1, 3),     # 1 if positive Z-score (hotspot), 3 if negative (coldspot), 0 if insignificant
    0)
print(eds["gi_quad"].value_counts(), eds["lisa_class"].value_counts())
