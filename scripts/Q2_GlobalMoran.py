""" GEOG41160 Assignment 2, Question 2: Global spatial autocorrelation
Team: 6

"""

### Importing libraries
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import os

from scipy.stats import skew
from libpysal.weights import Queen
from esda import Moran 
import libpysal

print(os.getcwd())

### Loading the Q1 output GeoPackage
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "Outputs" / "DublinED_ExtensionDensity.gpkg"


gdf = gpd.read_file(INPUT)
print("Working folder:", Path.cwd())
print("Repository:", ROOT)
print("Dublin Extension Application Ddensity exist:", gdf.exists())
print("Output folder:", OUTPUT)
print(gdf.head())


                ###PART1: Distribution of extension density ###
"""
General interpretation: skewness < 0.5 is symmetrical, between 0.5 - 1.0 is moderately skewed and > 1.0 is considerably skewed which is seen in this result  1.38. This is  considerably right skewed. Therefore, it is reasonable to consider a transformation. The absolute skewness decreased from 1.38 to -1.13 which still is considerably skewed to the left. Since transformation did not produce a near symmetrical distribution, it is difficult to clime the transformation produced a more symmetrical distribution. 
"""


###Creating the log_density column  
gdf["log_density"] = np.log1p(gdf["per_km2"])

###Calculating skewness  
print("Skewness, raw: %.2f, log: %.2f" % (skew(gdf["per_km2"]),
skew(gdf["log_density"])))

###Plotting histograms  
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
axes[0].hist(gdf["per_km2"], bins=30, color="#4a7c3a")
axes[0].set_title("Applications per km2")
axes[0].set_xlabel("Extension applications per km²")
axes[0].set_ylabel("Number of EDs")
axes[1].hist(gdf["log_density"], bins=30, color="#4a7c3a")
axes[1].set_title("log(1 + Applications per km2)")
axes[1].set_xlabel("Log(1 + extension applications per km²)")
axes[1].set_ylabel("Number of EDs")
plt.tight_layout()
plt.savefig(ROOT / "Outputs" / "Q2_Histogram.png", dpi=180, bbox_inches="tight")
plt.show()

                ###PART 2: Creating spatial weights ###

"""
Queen contiguity is used because two EDs are considered neighbors if they share either a boundary edge or a corner point. It is suitable because it captures more geographical connections than Rook contiguity, which requires a shared edge.

Row standardisation (w.transform = "r") is applied after identifying the neighbors.  It adjusts the spatial weights so that the weights assigned to the neighbors of each ED sum to 1. This helps make the weights comparable across EDs with different numbers of neighbors.

Output information: minimum: 2, mean: 5.7, max: 11 number of neighbors and zero islands []. Here [] means no islands. 
"""

w = libpysal.weights.Queen.from_dataframe(gdf, use_index=True)
neighbor_counts = [len(neighbors) for neighbors in w.neighbors.values()]


print("Neighbors: min", min(neighbor_counts), 
      "mean", round(np.mean(neighbor_counts), 1), 
      "max", max(neighbor_counts))


print("Islands:", w.islands)

w.transform = "r"

                ### Part 3: Compute Global Moran’s I ###
            
"""
Two variables 
1.	Raw density: gdf["per_km2"]
2.	Log-transformed density: gdf["log_density"] are analysed. 
The fixed random seed = 42
The number of permutations = 999

Raw density: Morans I = 0.332, p = 0.001
Log-transformed density: Morans I =  0.373, p = 0.001
"""             
            
np.random.seed(42)
moran = Moran(gdf["per_km2"], w, permutations=999)
print("Moran's I: %.3f | expected under spatial randomness: %.3f" % (moran.I, moran.EI))
            
print("Permutation p-value:", moran.p_sim)
            
np.random.seed(42)
moran = Moran(gdf["log_density"], w, permutations=999)
print("Moran's I: %.3f | expected under spatial randomness: %.3f" % (moran.I, moran.EI))
            
print("Permutation p-value:", moran.p_sim)

                         ### Part 4: Conclusion ###

"""
Both variables (Raw density: Morans I = 0.332, Log-transformed density: Morans I =  0.373) show positive spatial autocorrelation. This indicates a clustered pattern: EDs with similar extension densities tend to be located near one another.

Log transformation slightly increases Morans I from 0.332 to 0.373, but both values remain positive and statistically significant (p = 0.001). Therefore, the transformation does not change the overall conclusion.
"""
