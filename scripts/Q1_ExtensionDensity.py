""" GEOG41160 Assignment 2, Question 1: Extension density by ED
Team: 6
"""

### Importing libraries
from pathlib import Path
import duckdb

# For parts 4 and 5
import geopandas as gpd
import matplotlib.pyplot as plt


### Setting Paths
ROOT = Path(__file__).resolve().parents[1]
# ROOT = Path.cwd().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "Outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

PLANNING = DATA / "planning" / "planning_applications_national.gpkg"
EDS = DATA/ "boundaries" / "eds_national.gpkg"

DATABASE = OUTPUT / "extensions.duckdb"  #only a variable name so far

# Checking paths
print("Working folder:", Path.cwd())
print("Repository:", ROOT)
print("Planning data exists:", PLANNING.exists())
print("ED boundaries exist:", EDS.exists())
print("Output folder:", OUTPUTS)


                    ### PART 1 ###
""" Creates a DuckDB spatial database file, outputs/extensions.duckdb.
    Imports Planning applications (as 'planning_national') and Electoral Divisions (as 'eds_national') into the DuckDB.
    Filters and creates a new table 'eds' for the EDs of Dublin City. 
    Filters and creates a new table 'planning' for the Planning Applications received by Dublin City Council in the complete calendar years 2019–2025,
     where DevelopmentDescription contains the word “extension”, regardless of capitalisation.
    Length of 'eds ': 162 rows.
    Length of 'planning': 9914 rows.
"""
### Create the database
con = duckdb.connect(DATABASE)

con.install_extension("spatial")   # downloads spatial function first time only
con.load_extension("spatial")      # switches it on for the session


### Loading data into DB
# Planning data
con.sql(f"CREATE OR REPLACE TABLE planning_national AS SELECT * FROM ST_Read('{PLANNING}')")

# EDS data
con.sql(f"CREATE OR REPLACE TABLE eds_national AS SELECT * FROM ST_Read('{EDS}')")

print(con.sql("SHOW TABLES")) 


### Filtering:
# eds: the EDs of Dublin City
con.sql("""
    CREATE OR REPLACE TABLE eds AS
    SELECT *
    FROM eds_national
    WHERE COUNTY_ENGLISH = 'DUBLIN CITY'
""")
print("Dublin City EDs:")
print(con.sql("SELECT COUNT(*) FROM eds"))

# extensions: planning applications in Dublin City Council 2019-2025
con.sql("""
    CREATE OR REPLACE TABLE planning AS
    SELECT*
    FROM planning_national
    WHERE year(ReceivedDate) BETWEEN 2019 AND 2025
          AND PlanningAuthority = 'Dublin City Council'
          AND DevelopmentDescription ILIKE '%extension%'
""")

print("Dublin City Council extension applications:")
print(con.sql("SELECT COUNT(*) FROM planning"))


                    ### PART 2 ###
""" 'eds': CRS = EPSG:2157, number of features = 162,  geometry type = MULTIPOLYGON. 
    'planning': CRS = EPSG:EPSG:3857, number of features = 9914,  geometry type = POINT. 
    Reprojects the 'planning' to the 'eds' coordinate system (EPSG:2157 - ITM) in SQL.
    The analysis needs ITM, as it is specifically designed for Ireland and uses metres as its units,
     making it suitable for spatial analysis and accurate area and distance calculations.
"""
### Print CRS, number of features and geometry type
# EDS
print("---EDS---")
print("Number of features:")
print(con.sql("SELECT COUNT(*) FROM eds"))
print("Columns and CRS:")
print(con.sql("DESCRIBE eds"))
print("Geometry Type:")
print(con.sql("SELECT DISTINCT ST_GeometryType(SHAPE) FROM eds").fetchall())

# Planning
print("---Planning---")
print("Number of features:")
print(con.sql("SELECT COUNT(*) FROM planning"))
print("Columns and CRS:")
print(con.sql("DESCRIBE planning"))
print("Geometry Type:")
print(con.sql("SELECT DISTINCT ST_GeometryType(SHAPE) FROM planning").fetchall())

### Reprojecting Planning to ED's CRS
con.sql("""
    CREATE OR REPLACE TABLE planning_itm AS
    SELECT * EXCLUDE (SHAPE),
           ST_Transform(SHAPE, 'EPSG:3857', 'EPSG:2157', always_xy := true) AS SHAPE
    FROM planning
""")


                    ### PART 3 ###
""" Spatially joins 'planning' to the 'eds' in SQL and counts the applications in each ED. 
    The highest number of Applications is in CLONTARF EAST B with 304 extension applications.
    14 extension applications fall outside every ED. 
    This may be because 'ST_Within' returns True only when strictly inside the boundary, and the points can:
     - be located exactly on the ED boundary,
     - fall outside all the ED boundaries after reprojection.
"""
### Spatial Join of Applications and EDs
con.sql("""
    CREATE OR REPLACE TABLE ed_counts AS
    SELECT eds.ED_ENGLISH, eds.SHAPE,
           COUNT(p.ApplicationNumber) AS applications
    FROM eds AS eds
    LEFT JOIN planning_itm AS p ON ST_Within(p.SHAPE, eds.SHAPE)
    GROUP BY eds.ED_ENGLISH, eds.SHAPE 
""")

print(con.sql("SELECT ED_ENGLISH, applications FROM ed_counts ORDER BY applications DESC LIMIT 5"))

# Applications outside all EDS
print(con.sql("""
    SELECT COUNT(*) AS applications_outside_eds
    FROM planning_itm AS p
    WHERE NOT EXISTS (
        SELECT 1
        FROM eds
        WHERE ST_Within(p.SHAPE, eds.SHAPE)
    )
"""))


                    ### PART 4 ###
""" Calculates the density of applications in each ED (applications per km2).
    ROYAL EXCHANGE B has 171.6 applications per km2.
    Saves the result as DublinED_ExtensionDensity.gpkg.
"""
### Density of Applications in each ED
df = con.sql("""
    SELECT ED_ENGLISH, applications, ST_AsWKB(SHAPE) AS wkb
    FROM ed_counts
""").df()
eds_map = gpd.GeoDataFrame(df.drop(columns="wkb"),
                          geometry=gpd.GeoSeries.from_wkb(df["wkb"].apply(bytes)),
                          crs="EPSG:2157")
eds_map["per_km2"] = eds_map["applications"] / (eds_map.geometry.area / 1e6)
eds_map.to_file(OUTPUT / "DublinED_ExtensionDensity.gpkg")
print(gpd.read_file(OUTPUT / "DublinED_ExtensionDensity.gpkg").head())


                    ### PART 5 ###
""" Maps the density of Extension Applications in Dublin City.
    1 to 408 applications per km2, highest in Dublin South.
    Saves the map as ExtensionDensity_DublinED.png.
"""
### Mapping the Density
ax = eds_map.plot(column="per_km2", scheme="Quantiles", k=5, cmap="YlOrRd",
                 edgecolor="grey", linewidth=0.3, figsize=(7, 6), legend=True,
                 legend_kwds={"title": "per_km2", "fmt": "{:.0f}",
                             "loc": "lower right"})
ax.set_title("Extension Planning applications per km2, Dublin City EDs, 2019-2025")
ax.set_axis_off()
plt.savefig(OUTPUT / "ExtensionDensity_DublinED.png", dpi=180, bbox_inches="tight")
plt.show()