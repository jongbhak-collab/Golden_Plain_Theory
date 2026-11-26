"""Fill Russia (no WorldPop national file downloaded) with GPW v4.11 2020 density tiles, north of 41N only."""
import numpy as np, math
from scipy import ndimage
G=np.load('/tmp/wp_mosaic.npy'); D=np.load('/tmp/gpw_mosaic.npy')
N=2**6*512; X0T,Y0T=49*512,22*512
Dn=np.nan_to_num(D,nan=0.0)
hi=(Dn>=1500).astype(int); nb=ndimage.convolve(hi,np.ones((5,5),int),mode='constant')
Dn[(Dn<1500)&(nb>=8)]=4200.0
ny,nx=G.shape
lat=46.5-(np.arange(ny)+0.5)/120; lon=98+(np.arange(nx)+0.5)/120
gx=((lon+180)/360*N).astype(int)-X0T
my=np.log(np.tan(np.pi/4+np.radians(lat)/2)); gy=((1-my/np.pi)/2*N).astype(int)-Y0T
print(D.shape,gx.min(),gx.max(),gy.min(),gy.max())
ok=(gy>=0)&(gy<D.shape[0])
R=np.zeros_like(G); R[np.ix_(ok,np.ones(nx,bool))]=Dn[np.ix_(gy[ok],np.clip(gx,0,D.shape[1]-1))]
fill=np.load('/tmp/ru_mask.npy')&(R>0)&(~(G>0))
G2=G.copy(); G2[fill]=R[fill]
np.save('/tmp/wp_mosaic_ru.npy',G2); np.save('/tmp/ru_fill_mask.npy',fill)
area=(111.32/120)**2*np.cos(np.radians(lat))
print('filled cells',fill.sum(),'pop M',(R*fill*area[:,None]).sum()/1e6)
