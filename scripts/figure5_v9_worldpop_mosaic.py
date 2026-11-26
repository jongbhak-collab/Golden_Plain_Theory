import rasterio, glob, numpy as np, math
from rasterio.windows import from_bounds
SRC="/mnt/user-data/uploads/1_Golden_Plain_theory_of_Korean_origin/PopulationDensity"
LON0,LON1,LAT0,LAT1=98.0,147.0,8.0,46.5
R=1/120
W=int(round((LON1-LON0)/R)); H=int(round((LAT1-LAT0)/R))
M=np.full((H,W),np.nan,np.float32)
tot={}
for f in sorted(glob.glob(SRC+'/*.tif')):
    iso=f.split('/')[-1][:3].upper()
    with rasterio.open(f) as s:
        a=s.read(1).astype(np.float64); a[a==s.nodata]=np.nan
        # totals over the whole country
        rows=np.arange(s.height); lat=s.bounds.top-(rows+0.5)*s.res[1]
        area=(111.32*s.res[0])*(110.57*s.res[1])*np.cos(np.radians(lat))  # km2 per cell (approx)
        tot[iso]=np.nansum(a*area[:,None])/1e6
        # place into mosaic
        c0=int(round((s.bounds.left-LON0)/R)); r0=int(round((LAT1-s.bounds.top)/R))
        rs=max(0,-r0); cs=max(0,-c0); re=min(s.height,H-r0); ce=min(s.width,W-c0)
        if re<=rs or ce<=cs: continue
        sub=a[rs:re,cs:ce].astype(np.float32); tgt=M[r0+rs:r0+re,c0+cs:c0+ce]
        m=~np.isnan(sub); tgt[m]=sub[m]
np.save('/tmp/wp_mosaic.npy',M)
for k,v in tot.items(): print(k, round(v,2),'M')
print(M.shape, np.nanmax(M))
