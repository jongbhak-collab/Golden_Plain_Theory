"""Download the ETOPO 2022 subset used for Figure 3 (Golden River routing and map).

Region 116-139 E, 25-42 N, 30 arc-second surface elevation (NOAA NCEI ETOPO 2022,
doi:10.25921/fd45-gt74, public domain). Writes
data/etopo/ETOPO2022_30s_116E25N_139E42N.tif (2760 x 2040 cells, north-up, EPSG:4326),
the file name the routing scripts expect.

Source 1: NOAA ERDDAP griddap subset (dataset ETOPO_2022_v1_30s, variable z).
Source 2 (fallback): NCEI THREDDS OPeNDAP, global 30 arc-second netCDF.
Usage: python3 scripts/download_etopo2022_subset.py
"""
import os, sys, urllib.request
import numpy as np
import xarray as xr
import rasterio
from rasterio.transform import from_origin

W, E, S, N = 116.0, 139.0, 25.0, 42.0
OUT = 'data/etopo/ETOPO2022_30s_116E25N_139E42N.tif'
ERDDAP = ('https://oceanwatch.pfeg.noaa.gov/noaa_wide/erddap/griddap/ETOPO_2022_v1_30s.nc'
          f'?z%5B({S}):1:({N})%5D%5B({W}):1:({E})%5D')
OPENDAP = ('https://www.ngdc.noaa.gov/thredds/dodsC/global/ETOPO2022/30s/30s_surface_elev_netcdf/'
           'ETOPO_2022_v1_30s_N90W180_surface.nc')

def load():
    tmp = 'data/etopo/_erddap_subset.nc'
    try:
        print('ERDDAP:', ERDDAP)
        urllib.request.urlretrieve(ERDDAP, tmp)
        ds = xr.open_dataset(tmp)
    except Exception as e:
        print('ERDDAP failed (%s); trying OPeNDAP' % e)
        ds = xr.open_dataset(OPENDAP)
    lat = 'latitude' if 'latitude' in ds.coords else 'lat'
    lon = 'longitude' if 'longitude' in ds.coords else 'lon'
    da = ds['z'].sel({lat: slice(S, N), lon: slice(W, E)}).load()
    return da, lat, lon

os.makedirs('data/etopo', exist_ok=True)
da, lat, lon = load()
la, lo = da[lat].values, da[lon].values
# keep cells whose centres fall strictly inside the box (2040 rows x 2760 columns at 1/120 degree)
mlat = (la > S) & (la < N); mlon = (lo > W) & (lo < E)
z = da.values[np.ix_(mlat, mlon)]
la, lo = la[mlat], lo[mlon]
if la[0] < la[-1]:
    z, la = z[::-1], la[::-1]                 # north-up
dx = float(np.median(np.diff(lo))); dy = float(np.median(np.abs(np.diff(la))))
tr = from_origin(lo[0] - dx / 2, la[0] + dy / 2, dx, dy)
with rasterio.open(OUT, 'w', driver='GTiff', height=z.shape[0], width=z.shape[1], count=1,
                   dtype='float32', crs='EPSG:4326', transform=tr, compress='deflate') as dst:
    dst.write(z.astype('float32'), 1)
print('wrote', OUT, z.shape, 'origin', (lo[0] - dx / 2, la[0] + dy / 2), 'cell', dx)
if z.shape != (2040, 2760):
    print('warning: expected 2040 x 2760 cells; check the returned grid', file=sys.stderr)
