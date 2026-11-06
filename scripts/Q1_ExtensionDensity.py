""" GEOG41160 Assignment 2, Question 1: Extension density by ED
Team: 6

"""

### Importing libraries
from pathlib import Path
import duckdb


### Setting Paths
ROOT = Path(__file__).resolve().parents[1]
# ROOT = Path.cwd().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "Outputs"

PLANNING = DATA / "planning" / "planning_applications_national.gpkg"
EDS = DATA/ "boundaries" / "eds_national.gpkg"

DATABASE = OUTPUT / "extensions.duckdb"  #only a variable name so far

# # Checking paths
# print("Repository:", ROOT)
# print("Planning data exists:", PLANNING.exists())
# print("ED boundaries exist:", EDS.exists())
# print("Output folder:", OUTPUTS)


                    ###PART1###
### Create the database
con = duckdb.connect(DATABASE)

con.install_extension("spatial")   # downloads spatial function first time only
con.load_extension("spatial")      # switches it on for the session


### Loading data into DB
# Planning data
con.sql(f"CREATE OR REPLACE TABLE planning AS SELECT * FROM ST_Read('{PLANNING}')")
print("Planning")
print(con.sql("SELECT COUNT(*) FROM planning"))
print(con.sql("DESCRIBE planning"))

# EDS data
con.sql(f"CREATE OR REPLACE TABLE eds AS SELECT * FROM ST_Read('{EDS}')")
print("EDS")
print(con.sql("SELECT COUNT(*) FROM eds"))
print(con.sql("DESCRIBE eds"))

print(con.sql("SHOW TABLES")) 


### Filtering:
# eds: the EDs of Dublin City
print(con.sql("""SELECT COUNT (*) FROM eds
    WHERE COUNTY_ENGLISH = 'DUBLIN CITY'
"""))

# extensions: planning applications in Dublin City Council 2019-2025
print(con.sql("""
    SELECT year(ReceivedDate) AS year,
           COUNT(*) AS applications
    FROM planning
    WHERE year(ReceivedDate) BETWEEN 2019 AND 2025
          AND PlanningAuthority = 'Dublin City Council'
          AND DevelopmentDescription ILIKE '%extension%'
    GROUP BY year
    ORDER BY year
"""))


                    ###PART2###
### Print CRS