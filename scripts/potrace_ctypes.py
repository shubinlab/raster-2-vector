"""Minimal native libpotrace bridge (requires system libpotrace); produces editable SVG path geometries."""
import ctypes as C
import ctypes.util
import numpy as np
from xml.sax.saxutils import escape

class Point(C.Structure):
    _fields_=[('x',C.c_double),('y',C.c_double)]
class Curve(C.Structure):
    _fields_=[('n',C.c_int),('tag',C.POINTER(C.c_int)),('c',C.POINTER(Point*3))]
class Path(C.Structure): pass
Path._fields_=[('area',C.c_int),('sign',C.c_int),('curve',Curve),('next',C.POINTER(Path)),('childlist',C.POINTER(Path)),('sibling',C.POINTER(Path)),('priv',C.c_void_p)]
class State(C.Structure):
    _fields_=[('status',C.c_int),('plist',C.POINTER(Path)),('priv',C.c_void_p)]
class Bitmap(C.Structure):
    _fields_=[('w',C.c_int),('h',C.c_int),('dy',C.c_int),('map',C.POINTER(C.c_ulong))]
class Progress(C.Structure):
    _fields_=[('callback',C.c_void_p),('data',C.c_void_p),('min',C.c_double),('max',C.c_double),('epsilon',C.c_double)]
class Param(C.Structure):
    _fields_=[('turdsize',C.c_int),('turnpolicy',C.c_int),('alphamax',C.c_double),('opticurve',C.c_int),('opttolerance',C.c_double),('progress',Progress)]
# Look for the native library on Linux, Apple Silicon/Intel macOS, or a user-specified path.
import os
_CANDIDATES=[
    os.environ.get('POTRACE_LIB_PATH'),
    ctypes.util.find_library('potrace'),
    '/opt/homebrew/lib/libpotrace.dylib',
    '/usr/local/lib/libpotrace.dylib',
    '/usr/lib/x86_64-linux-gnu/libpotrace.so.0',
    '/usr/lib/aarch64-linux-gnu/libpotrace.so.0',
    'libpotrace.so.0',
    'libpotrace.dylib',
]
lib=None
for _candidate in _CANDIDATES:
    if not _candidate:continue
    try:
        lib=C.CDLL(_candidate)
        break
    except OSError:pass
if lib is None:
    raise RuntimeError('Native libpotrace is missing. Install it or set POTRACE_LIB_PATH; use Docker on Windows.')
lib.potrace_param_default.restype=C.POINTER(Param)
lib.potrace_param_free.argtypes=[C.POINTER(Param)]
lib.potrace_trace.argtypes=[C.POINTER(Param),C.POINTER(Bitmap)]
lib.potrace_trace.restype=C.POINTER(State)
lib.potrace_state_free.argtypes=[C.POINTER(State)]
lib.potrace_version.restype=C.c_char_p

def trace(mask,alphamax=1.0,opttolerance=0.2,turdsize=1,opticurve=True,precision=2):
    """Return SVG path data string and counts. mask TRUE=ink."""
    mask=np.asarray(mask,dtype=bool)
    h,w=mask.shape
    nb=C.sizeof(C.c_ulong)*8
    dy=(w+nb-1)//nb
    words=(C.c_ulong*(dy*h))()
    ys,xs=np.where(mask)
    for y,x in zip(ys.tolist(),xs.tolist()):
        words[y*dy+x//nb] |= 1<<(nb-1-x%nb)
    bmp=Bitmap(w,h,dy,words)
    p=lib.potrace_param_default()
    p.contents.alphamax=alphamax
    p.contents.opttolerance=opttolerance
    p.contents.opticurve=int(opticurve)
    p.contents.turdsize=turdsize
    st=lib.potrace_trace(p,C.byref(bmp))
    if not st: raise RuntimeError('null native Potrace state')
    if st.contents.status != 0: raise RuntimeError('Potrace status '+str(st.contents.status))
    result=[]; curves=0; lines=0; paths=0
    ptr=st.contents.plist
    fmt=lambda p:f'{p.x:.{precision}f},{p.y:.{precision}f}'
    while bool(ptr):
        curve=ptr.contents.curve; n=curve.n
        if n<1 or n>50000: raise ValueError('Unreasonable curve segments '+str(n))
        segs=['M'+fmt(curve.c[n-1][2])]
        for i in range(n):
            if curve.tag[i]==1:
                segs.append('C'+fmt(curve.c[i][0])+' '+fmt(curve.c[i][1])+' '+fmt(curve.c[i][2]));curves+=1
            elif curve.tag[i]==2:
                segs.append('L'+fmt(curve.c[i][1])+' '+fmt(curve.c[i][2]));lines+=2
            else: raise ValueError('Unrecognized segment tag '+str(curve.tag[i]))
        segs.append('Z'); result.append(' '.join(segs));paths+=1
        ptr=ptr.contents.next
    lib.potrace_state_free(st);lib.potrace_param_free(p)
    return ' '.join(result),{'paths':paths,'curves':curves,'lines':lines,'commands':curves+lines}

def make_svg(mask,**kwargs):
    h,w=mask.shape
    path,counts=trace(mask,**kwargs)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><path fill="black" fill-rule="evenodd" d="{path}"/></svg>'
    return svg,counts
if __name__=='__main__':
    print('native Potrace:',lib.potrace_version().decode())
    from PIL import Image,ImageDraw
    import cairosvg
    import io
    a=np.zeros((75,130),bool);a[4:22,4:26]=1;a[33:65,70:108]=1;a[40:52,80:98]=0
    s,c=make_svg(a)
    print('counts',c,'svg bytes',len(s))
    r=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode()))).convert('RGBA'))
    bm=(r[:,:,:3].mean(axis=2)<128)&(r[:,:,3]>127)
    print('Input pixels',a.sum(),'render pixels',bm.sum(),'IOU',(a&bm).sum()/float((a|bm).sum()))
    open('/mnt/data/vector_skill_lab/test_potrace.svg','w').write(s)
