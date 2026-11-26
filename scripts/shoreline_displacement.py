"""Horizontal shoreline displacement between 20 ka and today (PaleoMIST 1.0 minimal, 0.25 deg).
For each present-day coastal land cell, distance (great circle) to the nearest cell that was sea at 20 ka."""
import numpy as np
from netCDF4 import Dataset
d = Dataset('data/figure2_paleomist/PaleoMIST_east_asia_50ka.nc')
age = -np.asarray(d.variables['time'][:], float); lat = np.asarray(d.variables['lat'][:]); lon = np.asarray(d.variables['lon'][:])
z = np.asarray(d.variables['paleo_topography'][:])
z0 = z[np.argmin(age)]; k20 = int(np.argmin(abs(age - 20000)))
land0 = z0 > 0; sea20 = z[k20] <= 0
LON, LAT = np.meshgrid(lon, lat)
nb = np.zeros_like(land0)
for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
    nb |= np.roll(~land0, (dy, dx), (0, 1))
coast0 = land0 & nb
def gc(lo1, la1, lo2, la2):
    p1, p2 = np.radians(la1), np.radians(la2); dl = np.radians(lo2 - lo1)
    return 6371.0088 * np.arccos(np.clip(np.sin(p1)*np.sin(p2) + np.cos(p1)*np.cos(p2)*np.cos(dl), -1, 1))
slo, sla = LON[sea20], LAT[sea20]
def region(mask, name):
    best = (0, None)
    for lo, la in zip(LON[coast0 & mask], LAT[coast0 & mask]):
        dmin = gc(lo, la, slo, sla).min()
        if dmin > best[0]: best = (dmin, (lo, la))
    print(f'{name}: max displacement {best[0]:.0f} km at present coast {best[1]}')
west = (LON >= 117) & (LON <= 126.8) & (LAT >= 30) & (LAT <= 41.25)
kor_w = (LON >= 124.5) & (LON <= 127.2) & (LAT >= 34.3) & (LAT <= 38.5)
kor_e = (LON >= 128.8) & (LON <= 130) & (LAT >= 35.3) & (LAT <= 38.5)
region(west, 'Bohai-Yellow Sea coasts')
region(kor_w, 'Korean west coast')
region(kor_e, 'Korean east coast')
