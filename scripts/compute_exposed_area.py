"""Exposed area of the Golden Plain through time (Table 2 and Figure 2 of the paper).

Input : data/figure2_paleomist/PaleoMIST_east_asia_50ka.nc
        (subset of PaleoMIST 1.0, Gowan et al. 2021, minimal scenario, 0.25 degree; CC BY 4.0)
Output: data/figure2_paleomist/exposed_area_timeseries.csv

Rule: a 0.25-degree cell counts as exposed shelf at time t when it is sea today
(present elevation <= 0 m) and land at time t (paleo_topography > 0 m).
Analysis box: 117-129.5 E, 27-41.25 N, minus the East Sea (north of 35 N and east of 128.9 E).
'Bohai-Yellow Sea' = box cells centred at or north of 31.5 N and at or west of 127 E; 'northern East China Sea' = the rest.
Cell areas are spherical (R = 6371.0088 km). Relative sea level is read at 123.5 E, 36 N.
Usage: python3 scripts/compute_exposed_area.py
"""
import csv
import numpy as np
from netCDF4 import Dataset

SRC = 'data/figure2_paleomist/PaleoMIST_east_asia_50ka.nc'
OUT = 'data/figure2_paleomist/exposed_area_timeseries.csv'
d = Dataset(SRC)
age = -np.asarray(d.variables['time'][:], dtype=float)
lat = np.asarray(d.variables['lat'][:]); lon = np.asarray(d.variables['lon'][:])
z = np.asarray(d.variables['paleo_topography'][:]); sl = np.asarray(d.variables['sea_level'][:])
R = 6371.0088; dl = np.deg2rad(0.25)
LON, LAT = np.meshgrid(lon, lat)
cell = R**2 * dl * (np.sin(np.deg2rad(LAT + 0.125)) - np.sin(np.deg2rad(LAT - 0.125)))
box = (LON >= 117) & (LON <= 129.5) & (LAT >= 27) & (LAT <= 41.25) & ~((LAT > 35.0) & (LON > 128.9))
z0 = z[np.argmin(age)]
sea_today = (z0 <= 0) & box
ys = (LAT >= 31.5) & (LON <= 127)
ic, jc = int(np.argmin(abs(lat - 36.0))), int(np.argmin(abs(lon - 123.5)))
rows = []
for k in np.argsort(-age):
    exp = sea_today & (z[k] > 0)
    tot, a_ys = cell[exp].sum(), cell[exp & ys].sum()
    rows.append({'age_years_BP': int(age[k]), 'rsl_central_yellow_sea_m': round(float(sl[k, ic, jc]), 1),
                 'exposed_total_km2': round(float(tot)), 'exposed_bohai_yellow_sea_km2': round(float(a_ys)),
                 'exposed_northern_east_china_sea_km2': round(float(tot - a_ys))})
with open(OUT, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
