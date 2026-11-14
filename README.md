# dublin-extensions-spatial-analysis
Repository for GEOG41160 Assignment 2

This workflow analyses where people in Dublin City extend their buildings based on the density of planning applications for extensions by Electoral Division (ED),
performs global spatial autocorrelation, and analyses local clusters and hotspots.

## Folders
### data: 
Contains the downloaded data for use in project; downloaded 05/11/2026 from Department of Housing, Local Government and Heritage and Tailte Éireann.



### scripts: 
Contains scripts, to be run in following order: Q1_ExtensionDensity.py, Q2_GlobalMoran.py, Q3_LISAandGi.py

### outputs: 
Contains output files such as map images or geopackages.
#### From Q1:
DublinED_ExtensionDensity.gpkg: Density of extension applications in Dublin city by ED, saved as a geopackage.
ExtensionDensity_DublinED.png: Density of extension applications in Dublin city by ED, represented in a map which is saved as a png.

#### From Q2: 
Q2_Histogram.png: Histogram of extension application density, saved as a png.

#### From Q3: 
LISA_ExtensionDensity_DublinED.png: Local Moran's I of extension applications by ED in Dublin, saved as a png.
GiStar_ExtensionDensity_DublinED.png: Getis-Ord Gi* of extension applications by ED in Dublin, saved as a png.

## Workflow
### Q1 short description

### Q2 Global Spatial Autocorrelation:
Part 1: Examined the distribution of extension density and applied a log transformation. 

Part 2: Created spatial weights using Queen contiguity. 

Part 3: Computed Global Morans I using a fixed random seed and 999 permutations, reporting the I statistic and p-value for both raw and transformed density. 

Part 4: Interpreted the results and explained the effect of the transformation.

### Q3 LISA and Gi*:
Part 1: Calculated LISA of extension density using same spatial weights as Q2.

Part 2: Applied FDR to LISA to find significant results.

Part 3: Mapped LISA results.

Part 4: Computed Getis-Ord Gi* with double-sided p-values to find hotspots and coldspots.

Part 5: Mapped results of Getis-Ord Gi*.

Part 6: Compared results of LISA to Getis-Ord Gi*.

## Sprint logs
### Sprint 0 
02/11/2026: GitHub organization and repository created. Each member created 1 folder. Roles for the project decided. 
Next: download the data, clean data and create DB. 

### Sprint 1 
07/11/2026 (end date): Data downloaded and placed in the data folder. Created Script 'Q1_ExtensionDensity' and answered question 1 of the assignment.

### Sprint 2
09/11/2026 (end date): Downloaded data folder and script of Q1_ExtensionDensity. Then created Script 'Q2_GlobalMoran' and answered question 3 of the assignment. Committed in GitHub. 

### Sprint 3 
12/11/2026:  Created Script 'Q3_LISAandGi' and answered question 3 of assignment.  Checked scripts to ensure cohesion of formatting.
