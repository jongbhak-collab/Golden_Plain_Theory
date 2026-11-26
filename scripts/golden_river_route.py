"""Paleo-drainage routing on ETOPO 2022 bathymetry for the Yellow Sea / ECS shelf.

Method
  1. Read DEM (WGS84, 30 arc-second).
  2. Optional Gaussian low-pass (sigma in km) to suppress tidal sand ridges / Holocene mud bumps.
  3. For a chosen sea level SL (m): cells <= SL become ocean (set to a deep sink), cells > SL are land.
  4. Priority-flood depression filling (pysheds), flat resolution, D8 flow direction, flow accumulation.
  5. Save accumulation, flow direction, filled DEM as npy for plotting; extract main trunk polylines.
"""
import sys, json, numpy as np, rasterio
from scipy.ndimage import gaussian_filter
from pysheds.grid import Grid
from pysheds.sview import Raster, ViewFinder

src_path = sys.argv[1]
out_prefix = sys.argv[2]
SL = float(sys.argv[3])
sigma_km = float(sys.argv[4])

with rasterio.open(src_path) as src:
    dem = src.read(1).astype('float64')
    tr = src.transform
    H, W = dem.shape

# degrees per cell and km per cell (lat-dependent)
dlon = tr.a; dlat = -tr.e
lat_c = tr.f + dlat * (-0.5) - dlat * np.arange(H)  # cell center lats
lon_c = tr.c + dlon * 0.5 + dlon * np.arange(W)
km_per_deg_lat = 111.2
km_per_deg_lon = 111.2 * np.cos(np.deg2rad(34.0))

z = dem.copy()
if sigma_km > 0:
    sig_px = sigma_km / (km_per_deg_lat * dlat)  # pixels (lat); lon slightly different, ignore
    # smooth only the submarine part; keep land as is
    zs = gaussian_filter(z, sigma=sig_px)
    z = np.where(dem < 0, zs, dem)

# ocean at this sea level -> deep sink
from scipy import ndimage
sea0 = z <= SL
lab, n = ndimage.label(sea0)
pac = lab[int((30 - tr.f)/tr.e), int((135 - tr.c)/tr.a)]   # open Pacific seed
sea = lab == pac                                             # only ocean connected to the Pacific
land = ~sea                                                  # enclosed deep pockets stay as land (lakes), get filled and overflow
z2 = np.where(land, z, SL - 2000.0)

# pysheds grid
vf = ViewFinder(affine=tr, shape=z2.shape, crs=rasterio.crs.CRS.from_epsg(4326), nodata=-32768)
grid = Grid(viewfinder=vf)
rast = Raster(z2.astype('float64'), viewfinder=vf)

pits = grid.fill_pits(rast)
flooded = grid.fill_depressions(pits)
inflated = grid.resolve_flats(flooded)
dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
fdir = grid.flowdir(inflated, dirmap=dirmap)
acc = grid.accumulation(fdir, dirmap=dirmap)
acc = np.asarray(acc, dtype='float64')
fdir = np.asarray(fdir, dtype='int32')
filled = np.asarray(inflated, dtype='float64')

np.save(out_prefix + '_acc.npy', acc.astype('float32'))
np.save(out_prefix + '_fdir.npy', fdir)
np.save(out_prefix + '_fill.npy', filled.astype('float32'))
np.save(out_prefix + '_land.npy', land)
print('done', out_prefix, 'land cells', int(land.sum()), 'max acc', float(np.nanmax(np.where(land, acc, 0))))
