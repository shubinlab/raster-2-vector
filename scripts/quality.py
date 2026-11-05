"""Raster/vector comparison: one source mask, immutable coordinates, true vector render."""
from __future__ import annotations
import hashlib,io
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
import cairosvg


def foreground(source,threshold=None,polarity='auto'):
    im=np.asarray(Image.open(source).convert('RGBA'))
    rgb=im[:,:,:3];alpha=im[:,:,3]
    h,w=alpha.shape
    if np.count_nonzero(alpha<248)>0.1*h*w:
        mask=alpha>127
        return mask,{'method':'alpha','threshold':127,'polarity':'opaque','background':[11,19,31]},rgb
    corners=np.concatenate([rgb[:max(4,h//20),:max(4,w//20)].reshape(-1,3),rgb[:max(4,h//20),-max(4,w//20):].reshape(-1,3),rgb[-max(4,h//20):,:max(4,w//20)].reshape(-1,3),rgb[-max(4,h//20):,-max(4,w//20):].reshape(-1,3)])
    bg=np.median(corners,axis=0).astype(np.uint8)
    lum=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    if polarity=='auto':polarity='light' if np.median(bg)<127 else 'dark'
    if threshold is None:
        # Pixel threshold is a parameter, not a proof of vector-quality change.
        threshold=int((float(np.percentile(lum,99)) + float(np.median(bg)))/2) if polarity=='light' else int((float(np.percentile(lum,1))+float(np.median(bg)))/2)
    if polarity=='light':mask=lum>threshold
    elif polarity=='dark':mask=lum<threshold
    else:raise ValueError('polarity must be auto, light or dark')
    return mask,{'method':'luminance','threshold':int(threshold),'polarity':polarity,'background':bg.tolist()},rgb


def render(svg,w,h):
    # no external resources / embedded rasters are accepted in the skill
    import xml.etree.ElementTree as ET
    if any(z in svg.lower() for z in ('<!doctype','<!entity','url(', 'file://','data:')):
        raise ValueError('External resources, doctypes and URL-valued fills are forbidden')
    root=ET.fromstring(svg)
    for el in root.iter():
        tag=el.tag.rsplit('}',1)[-1]
        if tag not in ('svg','path','circle','ellipse','rect','g'):raise ValueError(f'SVG tag {tag} is unsupported in vector-only mode')
        if any('href' in k or k=='style' for k in el.attrib):raise ValueError('External references and styles forbidden')
    out=cairosvg.svg2png(bytestring=svg.encode(),output_width=w,output_height=h)
    return np.asarray(Image.open(io.BytesIO(out)).convert('RGBA'))


def mask_from_svg(svg,shape):
    h,w=shape
    return render(svg,w,h)[:,:,3]>127


def iou(ref,out):
    union=int(np.count_nonzero(ref|out));same=int(np.count_nonzero(ref&out))
    return same/union if union else 1.0


def topology(mask,small=10):
    # Count significant filled components and dark counter regions enclosed by them.
    fg=np.asarray(mask,dtype=np.uint8)
    n,labels,stats,_=cv2.connectedComponentsWithStats(fg,8)
    components=int(sum(stats[k,cv2.CC_STAT_AREA]>=small for k in range(1,n)))
    contours,hier=cv2.findContours(fg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    holes=0
    if hier is not None:
        # Every depth-odd contour describes a hole; do not confuse with background.
        hi=hier[0]
        for i,c in enumerate(contours):
            depth=0;parent=int(hi[i,3])
            while parent!=-1:depth+=1;parent=int(hi[parent,3])
            if depth%2 and abs(cv2.contourArea(c))>=small:holes+=1
    return {'components':components,'holes':holes}


def qa(ref,out,with_boundary=True,regions=None):
    ans={'iou':round(iou(ref,out),6),'missing_pixels':int(np.count_nonzero(ref & ~out)),
         'extra_pixels':int(np.count_nonzero(out & ~ref)),
         'different_pixels':int(np.count_nonzero(ref^out)),
         'reference_foreground_pixels':int(np.count_nonzero(ref)),
         'svg_foreground_pixels':int(np.count_nonzero(out))}
    ans['reference_topology']=topology(ref);ans['svg_topology']=topology(out)
    ans['topology_preserved']=(ans['reference_topology']==ans['svg_topology'])
    if with_boundary:
        kr=np.ones((3,3),np.uint8)
        e1=(ref&~cv2.erode(ref.astype('uint8'),kr).astype(bool))
        e2=(out&~cv2.erode(out.astype('uint8'),kr).astype(bool))
        if e1.any() and e2.any():
            d=np.r_[distance_transform_edt(~e2)[e1],distance_transform_edt(~e1)[e2]]
            ans['boundary_p95_px']=round(float(np.quantile(d,.95)),3)
            ans['boundary_max_px']=round(float(d.max()),3)
    if regions:
        ans['regions']={name:round(iou(ref[y0:y1,x0:x1],out[y0:y1,x0:x1]),6)
                 for name,(x0,y0,x1,y1) in regions.items()}
    return ans


def previews(svg,source,preview_path,overlay_path,threshold=None,polarity='auto'):
    ref,srcinfo,rgb=foreground(source,threshold,polarity)
    h,w=ref.shape
    rendered=render(svg,w,h)
    mask=rendered[:,:,3]>127
    # Composite vector over background derived from actual source, not over source art.
    bg=np.asarray(srcinfo['background'],dtype=float)
    a=rendered[:,:,3:4].astype(float)/255.
    png=np.uint8(np.clip(rendered[:,:,:3]*a+(1-a)*bg,0,255))
    Image.fromarray(png).save(preview_path,optimize=True)
    # A single comparison image: original, generated, mismatch + enlarged crops when available.
    diff=np.zeros((h,w,3),np.uint8);diff[:]=[8,16,27]
    diff[ref&mask]=[245,245,245];diff[ref&~mask]=[255,78,100];diff[mask&~ref]=[38,215,234]
    scale=min(1.0,1600/w);pw=int(round(w*scale));ph=int(round(h*scale))
    pad=20;rowpad=52
    canvas=Image.new('RGB',(pw+pad*2,3*(ph+rowpad)+pad*2),(8,16,27))
    draw=ImageDraw.Draw(canvas)
    for idx,(name,arr) in enumerate([('01  ORIGINAL RASTER',rgb),('02  NEW SVG RENDER',png),('03  OVERLAY: WHITE=COMMON  RED=MISSING  CYAN=EXTRA',diff)]):
        y=pad+idx*(ph+rowpad)
        draw.text((pad,y+9),name,fill=(225,232,240))
        im=Image.fromarray(arr).resize((pw,ph),Image.Resampling.LANCZOS if idx<2 else Image.Resampling.NEAREST)
        canvas.paste(im,(pad,y+rowpad-10))
    canvas.save(overlay_path,optimize=True)
    return qa(ref,mask,True),srcinfo
