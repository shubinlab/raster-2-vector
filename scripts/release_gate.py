"""Shared preflight for raster-2-vector CLI and ChatGPT plugin.

No resizing of individual foreground bounding boxes is ever permitted.
The SVG is rendered on the original source raster canvas exactly once.
"""
from __future__ import annotations
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from geometry import load_one_path,angle
from quality import foreground,mask_from_svg,qa


def source_canvas_check(svg: str, shape, tolerance: float=.005):
    root=ET.fromstring(svg)
    raw=root.get('viewBox')
    if raw is None:raise ValueError('SOURCE_SPACE_MISMATCH: SVG is missing viewBox')
    vals=[float(v) for v in re.split(r'[\s,]+',raw.strip())]
    if len(vals)!=4 or min(vals[2:])<=0:
        raise ValueError('SOURCE_SPACE_MISMATCH: malformed viewBox')
    h,w=shape
    ratio=(vals[2]/vals[3])/(w/h)
    if abs(ratio-1)>tolerance:
        raise ValueError('SOURCE_SPACE_MISMATCH: no independent x/y resizing for IoU')
    return ratio


def curvature(segment,at_end:bool):
    import numpy as np
    k=segment['kind']
    if k=='L':return 0.
    if k!='C':return None
    p0,p1,p2,p3=(segment[n] for n in ('p0','p1','p2','p'))
    if at_end:v=3*(p3-p2);a=6*(p3-2*p2+p1)
    else:v=3*(p1-p0);a=6*(p0-2*p1+p2)
    norm=float(np.linalg.norm(v))
    if norm<1e-7:return None
    return float(np.linalg.det(np.array([v,a]))/norm**3)


def seams(svg: str,curvature_limit=.08):
    import numpy as np
    seg,_=load_one_path(svg)
    issues=[]
    for i,(a,b) in enumerate(zip(seg,seg[1:])):
        if a['kind'] not in ('C','L') or b['kind'] not in ('C','L'):continue
        if np.linalg.norm(a['p']-b['p0'])>1e-5:continue
        degrees=angle(a,b)
        if 3<degrees<70:
            issues.append({'type':'G1','point':a['p'].tolist(),'angle':round(float(degrees),3)})
        elif degrees<=3:
            left=curvature(a,True);right=curvature(b,False)
            if left is not None and right is not None and abs(left-right)>curvature_limit:
                issues.append({'type':'G2','point':a['p'].tolist(),'jump':round(abs(left-right),4)})
    return issues


def new_seams(before:str,after:str,px_tolerance=1.5):
    old=seams(before);result=[]
    for issue in seams(after):
        close=[v for v in old if v['type']==issue['type'] and
               math.dist(v['point'],issue['point'])<=px_tolerance]
        metric='angle' if issue['type']=='G1' else 'jump'
        if not close or issue[metric]>min(x[metric] for x in close)+(1.5 if metric=='angle' else .01):
            result.append(issue)
    return result



def component_regressions(reference, baseline, candidate, tolerance=.008, min_area=25, pad=3):
    """Stable source-component windows, independent of runtime's quality version."""
    import cv2
    import numpy as np
    n, labels, stats, _=cv2.connectedComponentsWithStats(reference.astype('uint8'),8)
    h,w=reference.shape
    out=[]
    for k in range(1,n):
        x,y,ww,hh,area=map(int,stats[k])
        if area<min_area:continue
        x0=max(0,x-pad);x1=min(w,x+ww+pad)
        y0=max(0,y-pad);y1=min(h,y+hh+pad)
        r=reference[y0:y1,x0:x1]
        old=baseline[y0:y1,x0:x1];new=candidate[y0:y1,x0:x1]
        def score(v):
            union=int((r|v).sum())
            return int((r&v).sum())/union if union else 1.
        before,after=score(old),score(new)
        if after+tolerance<before:
            out.append({'component':k,'area':area,'before':round(before,6),'after':round(after,6)})
    return out

def gate(source,original_svg:str,candidate_svg:str,minimum=.95,feature_drop=.008):
    ref,_,_=foreground(source)
    source_canvas_check(candidate_svg,ref.shape)
    source_canvas_check(original_svg,ref.shape)
    before=mask_from_svg(original_svg,ref.shape)
    after=mask_from_svg(candidate_svg,ref.shape)
    a=qa(ref,before,False);b=qa(ref,after,True)
    regressions=component_regressions(ref,before,after,feature_drop)
    joins=new_seams(original_svg,candidate_svg)
    problems=[]
    if b['iou']<minimum:problems.append('global_iou_below_threshold')
    if not b['topology_preserved']:problems.append('broken_topology')
    if regressions:problems.append('small_feature_regression')
    if joins:problems.append('new_G1_or_G2_seam')
    return {'passes':not problems,'reasons':problems,'candidate':b,
            'baseline_iou':a['iou'],'feature_regressions':regressions,'new_seams':joins}


def safe_minify(source,svg:str,threshold=.95):
    """Scour is optional; accept only byte savings that preserve raster fidelity."""
    try:
        from scour.scour import scourString
    except ImportError:
        return svg,{'available':False,'kept':False}
    compact=scourString(svg)
    if isinstance(compact,bytes):compact=compact.decode('utf-8')
    if len(compact.encode())>=len(svg.encode()):return svg,{'available':True,'kept':False}
    report=gate(source,svg,compact,minimum=threshold)
    if not report['passes']:
        return svg,{'available':True,'kept':False,'blocked':report['reasons']}
    return compact,{'available':True,'kept':True,'saved_bytes':len(svg.encode())-len(compact.encode()),
                    'iou':report['candidate']['iou']}
