"""Vector geometry utilities for filled, untransformed SVG wordmark paths.

No raster input or model calls: deterministic geometry only. Unsupported SVG features
are rejected, not silently thrown away. Algorithms are original implementations
of standard arc-length cubic fitting and line simplification.
"""
from __future__ import annotations
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from typing import Any
import numpy as np
from scipy.spatial import cKDTree

TOKEN = re.compile(r'[a-zA-Z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?')
ARITY = {'m':2, 'l':2, 'h':1, 'v':1, 'c':6, 's':4, 'q':4, 't':2, 'a':7, 'z':0}


def path_segments(d: str) -> list[dict]:
    tokens = TOKEN.findall(d); i=0;cmd=None
    p=np.zeros(2,float); start=p.copy();last_c2=None;last_q=None;last_command=None
    out=[]
    while i < len(tokens):
        if tokens[i].isalpha():cmd=tokens[i];i+=1
        if cmd is None or cmd.lower() not in ARITY:raise ValueError(f'Unsupported path command {cmd!r} at {i}')
        typ=cmd.lower()
        if typ=='z':
            out.append({'kind':'Z','p0':p.copy(),'p':start.copy()});p=start.copy();cmd=None
            last_c2=last_q=None;last_command='z';continue
        ar=ARITY[typ];vals=tokens[i:i+ar]
        if len(vals)!=ar or any(z.isalpha() for z in vals):raise ValueError(f'Invalid {cmd} arguments at {i}')
        v=np.array([float(z) for z in vals]);i+=ar;rel=cmd.islower()
        if typ=='m':
            new=(p+v if rel else v);out.append({'kind':'M','p':new.copy()});p=new;start=p.copy();cmd='l' if rel else 'L';last_c2=last_q=None
        elif typ=='l':
            new=p+v if rel else v;out.append({'kind':'L','p0':p.copy(),'p':new.copy()});p=new;last_c2=last_q=None
        elif typ in ('h','v'):
            new=p.copy();j=1 if typ=='v' else 0;new[j]=p[j]+v[0] if rel else v[0]
            out.append({'kind':'L','p0':p.copy(),'p':new.copy()});p=new;last_c2=last_q=None
        elif typ=='c':
            pts=v.reshape(3,2);pts=pts+p if rel else pts
            out.append({'kind':'C','p0':p.copy(),'p1':pts[0].copy(),'p2':pts[1].copy(),'p':pts[2].copy()});p=pts[2].copy();last_c2=pts[1].copy();last_q=None
        elif typ=='s':
            pts=v.reshape(2,2);pts=pts+p if rel else pts
            c1=2*p-last_c2 if last_command in ('c','s') and last_c2 is not None else p.copy()
            out.append({'kind':'C','p0':p.copy(),'p1':c1.copy(),'p2':pts[0].copy(),'p':pts[1].copy()});p=pts[1].copy();last_c2=pts[0].copy();last_q=None
        elif typ in ('q','t'):
            if typ=='q':
                q,new=v.reshape(2,2);q=q+p if rel else q;new=new+p if rel else new
            else:
                new=p+v if rel else v;q=2*p-last_q if last_command in ('q','t') and last_q is not None else p.copy()
            c1=p+(2/3)*(q-p);c2=new+(2/3)*(q-new)
            out.append({'kind':'C','p0':p.copy(),'p1':c1,'p2':c2,'p':new.copy()});p=new;last_q=q.copy();last_c2=None
        elif typ=='a':
            new=p+v[5:] if rel else v[5:]
            out.append({'kind':'A','p0':p.copy(),'p':new.copy(),'arc':v[:5].copy()});p=new;last_c2=last_q=None
        last_command=typ
    return out


def num(x:float,prec:int)->str:
    v=round(float(x),prec)
    if v==0:return '0'
    s=f'{v:.{prec}f}'.rstrip('0').rstrip('.') if prec else str(int(v))
    if s.startswith('0.'):s=s[1:]
    if s.startswith('-0.'):s='-'+s[2:]
    return s


def nums(vals,prec):
    a=[num(v,prec) for v in vals];out=''
    for k,v in enumerate(a):
        if k and not v.startswith('-'):out+=' '
        out+=v
    return out


def serial(segs:list[dict],precision:int=0)->str:
    p=np.zeros(2,float);old='';out=[];last_c2=None
    for s in segs:
        k=s['kind']
        if k=='M':
            choices=[('m',s['p']-p),('M',s['p'])]
            cmd,v=min(choices,key=lambda c:len(c[0]+nums(c[1],precision)));p=s['p'];last_c2=None
        elif k=='L':
            dv=s['p']-p
            if abs(dv[1])<1e-7:cmd='h';v=[dv[0]]
            elif abs(dv[0])<1e-7:cmd='v';v=[dv[1]]
            else:cmd='l';v=dv
            p=s['p'];last_c2=None
        elif k=='C':
            pts=np.r_[s['p1']-p,s['p2']-p,s['p']-p]
            if last_c2 is not None and np.linalg.norm(s['p1']-(2*p-last_c2))<1e-8:
                cmd='s';v=np.r_[s['p2']-p,s['p']-p]
            else:cmd='c';v=pts
            p=s['p'];last_c2=s['p2']
        elif k=='A':
            cmd='a';v=np.r_[s['arc'],s['p']-p];p=s['p'];last_c2=None
        elif k=='Z':cmd='z';v=[];p=s['p'];last_c2=None
        else:raise ValueError(k)
        if cmd=='z':out.append('z')
        else:
            stuff=nums(v,precision)
            if cmd==old and cmd not in ('m','M','a','A'):
                out.append(('' if stuff.startswith('-') else ' ')+stuff)
            else:out.append(cmd+stuff)
        old=cmd
    return ''.join(out)


def load_one_path(svg:str):
    root=ET.fromstring(svg)
    if root.tag.rsplit('}',1)[-1]!='svg':raise ValueError('Not an SVG document')
    children=list(root.iter())
    paths=[n for n in children if n.tag.rsplit('}',1)[-1]=='path']
    unsupported=[n.tag.rsplit('}',1)[-1] for n in children if n is not root and n.tag.rsplit('}',1)[-1] not in ('path',)]
    if unsupported or len(paths)!=1:raise ValueError('Refinement only supports one filled path without groups/clip/mask/text; use trace or edit in an SVG editor')
    path=paths[0]
    if root.get('transform') or path.get('transform') or root.get('style') or path.get('style') or path.get('stroke') or root.get('stroke'):
        raise ValueError('Refinement does not flatten transforms, inline styles or strokes')
    vb=root.get('viewBox')
    if not vb:raise ValueError('SVG viewBox is required')
    fill=path.get('fill',root.get('fill','#000'));rule=path.get('fill-rule',root.get('fill-rule','nonzero'))
    # Do not silently lose visual styling
    extra_root=set(root.attrib)-{'viewBox','fill','width','height','xmlns'}
    extra_path=set(path.attrib)-{'d','fill','fill-rule'}
    if extra_root or extra_path:raise ValueError('Unrecognized SVG styling attributes: '+str(sorted(extra_root|extra_path)))
    if not re.fullmatch(r'#[0-9a-fA-F]{3,8}|[a-zA-Z]+',fill):raise ValueError('Unsupported fill color')
    return path_segments(path.attrib['d']), {'viewBox':vb,'fill':fill,'fill-rule':rule}


def compact_svg(segs,info,precision=0):
    # Hard-coded single fill only. All geometry explicit; no embedded bitmap or font.
    vb=info['viewBox'];fill=info['fill'];rule=info['fill-rule']
    if rule not in ('evenodd','nonzero'):raise ValueError('Unsupported fill-rule')
    import html
    d=serial(segs,precision)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{html.escape(vb,quote=True)}" fill="{fill}"><path d="{d}"'+(' fill-rule="evenodd"' if rule=='evenodd' else '')+'/></svg>'


def draw_count(segs):
    c=Counter(z['kind'] for z in segs)
    return {'segments':sum(c[k] for k in ('L','C','A')),'lines':c['L'],'cubics':c['C'],'arcs':c['A'],'subpaths':c['M']}


def direction(s,at_start):
    if s['kind']=='L': v=s['p']-s['p0']
    elif s['kind']=='C':
        v=(s['p1']-s['p0']) if at_start else (s['p']-s['p2'])
        if np.linalg.norm(v)<1e-7:v=s['p']-s['p0']
    else:return None
    n=np.linalg.norm(v)
    return v/n if n>1e-8 else None


def angle(a,b):
    x=direction(a,False);y=direction(b,True)
    if x is None or y is None:return 180.
    return math.degrees(math.acos(float(np.clip(x@y,-1,1))))


def sample(s,n=32):
    t=np.linspace(0,1,n+1)[:,None]
    if s['kind']=='L':return s['p0']*(1-t)+s['p']*t
    if s['kind']=='C':return (1-t)**3*s['p0']+3*(1-t)**2*t*s['p1']+3*(1-t)*t*t*s['p2']+t**3*s['p']
    return None


def new_segment(group,max_err=1.4,max_join_angle=5):
    if len(group)<2 or len(group)>3 or any(s['kind'] not in ('C','L') for s in group):return None
    if any(angle(a,b)>max_join_angle for a,b in zip(group,group[1:])):return None
    if all(s['kind']=='L' for s in group):
        p0=group[0]['p0'];p3=group[-1]['p'];dv=p3-p0
        if np.linalg.norm(dv)<1e-5:return None
        err=max(np.linalg.norm(np.cross(dv,g['p']-p0))/np.linalg.norm(dv) for g in group[:-1])
        if err<=max_err:return {'kind':'L','p0':p0.copy(),'p':p3.copy()},float(err)
        return None
    arr=[sample(s,24) for s in group];S=np.concatenate([z if i==0 else z[1:] for i,z in enumerate(arr)])
    lens=np.linalg.norm(np.diff(S,axis=0),axis=1);length=lens.sum()
    if length<1e-6:return None
    t=np.r_[0,np.cumsum(lens)/length];u=3*(1-t)**2*t;v=3*(1-t)*t*t
    p0=S[0];p3=S[-1];d0=direction(group[0],True);d1=direction(group[-1],False)
    if d0 is None or d1 is None:return None
    # End-point directions constrained: exactly G1-continuous with neighboring segments.
    base=(1-t)[:,None]**3*p0+t[:,None]**3*p3+u[:,None]*p0+v[:,None]*p3
    A=np.column_stack([(u[:,None]*d0).reshape(-1),(-v[:,None]*d1).reshape(-1)])
    lam=np.linalg.lstsq(A,(S-base).reshape(-1),rcond=None)[0]
    if min(lam)<0.05:return None
    p1=p0+lam[0]*d0;p2=p3-lam[1]*d1
    new={'kind':'C','p0':p0.copy(),'p1':p1,'p2':p2,'p':p3.copy()}
    F=sample(new,90)
    err=max(float(cKDTree(F).query(S)[0].max()),float(cKDTree(S).query(F)[0].max()))
    if err<=max_err:return new,err
    return None


def simplify_options(segs, max_err=1.4, max_join_angle=5):
    for i in range(len(segs)-1):
        for span in (2,3):
            group=segs[i:i+span]
            if len(group)!=span:continue
            fitted=new_segment(group,max_err=max_err,max_join_angle=max_join_angle)
            if fitted:
                seg,err=fitted
                yield (i,i+span,seg,err)


def suspicious_joins(segs):
    # Only seams intended to be smooth; deliberate corners must be considered manually.
    return [(i,round(angle(a,b),2)) for i,(a,b) in enumerate(zip(segs,segs[1:])) if a['kind']=='C' and b['kind']=='C' and angle(a,b)>3 and angle(a,b)<60]


def seam_risks(segs, threshold=3.0, intentional_corner=70.0):
    """Detect likely accidental G1 discontinuities, not intentional sharp tips.

    Each report includes the join location. Z/M boundaries and SVG arcs cannot
    be judged with these cubic/line tangent vectors and require visual review.
    """
    issues=[]
    for i,(a,b) in enumerate(zip(segs,segs[1:])):
        if a['kind'] not in ('L','C') or b['kind'] not in ('L','C'):
            continue
        if np.linalg.norm(a['p']-b['p0'])>1e-5:
            continue
        deg=angle(a,b)
        if threshold<deg<intentional_corner:
            issues.append({'index':i,'x':float(a['p'][0]),'y':float(a['p'][1]),
                           'angle_deg':round(deg,3)})
    return issues


def new_kinks(before, after, spatial_tolerance=1.5, angle_tolerance=1.5):
    """Return only *new or worsened* non-sharp seams.

    Do not mistake pre-existing designer-intended corners for regression.
    A candidate must not turn a smooth join into a kink, including after
    SVG coordinate rounding/serializing. Compare actual parsed SVG paths.
    """
    old=seam_risks(before)
    problems=[]
    for issue in seam_risks(after):
        near=[x for x in old if math.hypot(x['x']-issue['x'],x['y']-issue['y'])<=spatial_tolerance]
        if not near or issue['angle_deg']>min(x['angle_deg'] for x in near)+angle_tolerance:
            problems.append(issue)
    return problems
