#!/usr/bin/env python3
"""raster-2-vector: fast, typography-aware vector workflow.

Commands:
  doctor
  refine existing.svg --source logo.png --out new.svg
  trace logo.png --out new.svg
  audit logo.png logo.svg [--out new.svg]

Only one source raster is the ground truth. Default output exactly three files:
editable SVG, PNG render, and raster-overlay PNG. JSON goes to stdout.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import sys
import time
from pathlib import Path
from typing import Any
from geometry import compact_svg,draw_count,load_one_path,simplify_options,suspicious_joins,seam_risks,new_kinks
from quality import foreground,mask_from_svg,iou,qa,previews,component_regressions,component_ious


def verify_candidate(svg,source_mask,target_iou,strict_topology=True):
    out=mask_from_svg(svg,source_mask.shape)
    score=iou(source_mask,out)
    if score+1e-8<target_iou:return False,score
    if strict_topology:
        from quality import topology
        if topology(out)!=topology(source_mask):return False,score
    return True,score


def simplify_document(input_svg,source_mask,min_iou=.95,max_err=.8,max_join_angle=3,
                      passes=5,per_pass=12,allow_topology_change=False):
    """Minimize a path without introducing new wing/lettering defects.

    The quality baseline is the actual input SVG versus the ORIGINAL raster.
    Both whole-mask and per-connected-component comparisons are enforced.
    Tangent checks run on parsed *serialized* SVG, not idealized floats.
    """
    initial_segments,info=load_one_path(input_svg)
    original_mask=mask_from_svg(input_svg,source_mask.shape)
    candidates=[(input_svg,'unchanged')]
    for precision in (0,1,2):
        svg=compact_svg(initial_segments,info,precision)
        if svg!=input_svg:candidates.append((svg,f'canonical_p{precision}'))
    scored=[];valid=[]
    for svg,reason in candidates:
        ok,score=verify_candidate(svg,source_mask,min_iou,not allow_topology_change)
        if ok:
            cand_mask=mask_from_svg(svg,source_mask.shape)
            regress=component_regressions(source_mask,original_mask,cand_mask)
            kinks=new_kinks(initial_segments,load_one_path(svg)[0])
            ok=not regress and not kinks
        else:
            regress=[];kinks=[]
        scored.append({'reason':reason,'bytes':len(svg.encode()),'iou':score,
                       'passes':ok,'wing_detail_regressions':regress,'new_kinks':kinks})
        if ok:valid.append((svg,reason))
    if not valid:
        raise ValueError('Original SVG fails raster/topology/smoothness gate. '
                         'Do not simplify; improve the input geometry and audit it.')
    active,reason=min(valid,key=lambda a:len(a[0].encode()))
    seg=load_one_path(active)[0]
    history=[]
    for iteration in range(passes):
        base_bytes=len(active.encode());options=[]
        for i,j,repl,err in simplify_options(seg,max_err,max_join_angle):
            sample=seg[:i]+[repl]+seg[j:]
            svg=compact_svg(sample,info,precision=0)
            saved=base_bytes-len(svg.encode())
            if saved<=0:continue
            # IMPORTANT: a quantized file may have different tangents from the
            # in-memory cubic. Refuse newly introduced visible joins.
            candidate_segments=load_one_path(svg)[0]
            if new_kinks(seg,candidate_segments):continue
            if new_kinks(initial_segments,candidate_segments):continue
            options.append((saved,err,i,j,candidate_segments,svg))
        options.sort(key=lambda a:(-a[0],a[1]))
        best=None
        for saved,err,i,j,cseg,csvg in options[:per_pass]:
            ok,score=verify_candidate(csvg,source_mask,min_iou,not allow_topology_change)
            if not ok:continue
            cand_mask=mask_from_svg(csvg,source_mask.shape)
            if component_regressions(source_mask,original_mask,cand_mask):
                continue
            # Fewer kinks are preferable to a few bytes. Never allow new ones.
            quality_key=(len(seam_risks(cseg)),len(csvg.encode()),-score,err)
            if best is None or quality_key<best[0]:
                best=(quality_key,cseg,csvg,saved,err,score,i,j)
        if best is None:break
        _,seg,active,saved,err,score,i,j=best
        history.append({'pass':iteration+1,'removed':j-i-1,'bytes_saved':saved,
                        'max_curve_error_px':round(err,3),'iou':round(score,6)})
    final_mask=mask_from_svg(active,source_mask.shape)
    return active,{'attempts':len(candidates),'initial_candidates':scored,
                   'simplification':history,'geometry':draw_count(seg),
                   'suspicious_curve_joins':suspicious_joins(seg),
                   'smoothness_risks':seam_risks(seg),
                   'component_ious':component_ious(source_mask,final_mask),
                   'protected_reference':'original raster and original SVG',
                   'gate':'no newly introduced tangent kinks or feature IoU regression'}



def ellipse_hybrid(mask, fill):
    """Try conics for actual near-elliptical components, not every curve.
    Uses one Potrace pass per nonellipse component only when at least one conic fits.
    Returns None if no analytic primitive improves the representation.
    """
    import cv2
    import numpy as np
    from geometry import path_segments, compact_svg
    from potrace_ctypes import trace
    from quality import mask_from_svg, iou
    n,labels,stats,_=cv2.connectedComponentsWithStats(mask.astype('uint8'),8)
    parts=[];ellipses=0
    for j in range(1,n):
        x,y,w,h,area=map(int,stats[j])
        if area<8:continue
        comp=np.pad((labels[y:y+h,x:x+w]==j),2)
        contours,hi=cv2.findContours(comp.astype('uint8'),cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        d_ellipse=[]
        if hi is not None and len(contours) in (1,2) and all(len(c)>=12 and cv2.contourArea(c)>35 for c in contours):
            for k,c in enumerate(contours):
                (cx,cy),(ww,hh),rot=cv2.fitEllipse(c)
                cx+=.5;cy+=.5
                delta=.45 if hi[0][k][3]<0 else -.48
                rx=ww/2+delta;ry=hh/2+delta
                a=np.deg2rad(rot);dx=rx*np.cos(a);dy=rx*np.sin(a)
                if min(rx,ry)<=2:break
                x0=cx+dx;y0=cy+dy;x1=cx-dx;y1=cy-dy
                d_ellipse.append(f'M{x0:.2f},{y0:.2f}A{rx:.2f},{ry:.2f} {rot:.2f} 0 1 {x1:.2f},{y1:.2f}A{rx:.2f},{ry:.2f} {rot:.2f} 0 1 {x0:.2f},{y0:.2f}Z')
        if d_ellipse and len(d_ellipse)==len(contours):
            local_svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w+4} {h+4}"><path fill="black" fill-rule="evenodd" d="{" ".join(d_ellipse)}"/></svg>'
            if iou(comp,mask_from_svg(local_svg,comp.shape))>=.989:
                local=' '.join(d_ellipse);ellipses+=1
            else:local=None
        else:local=None
        parts.append((x,y,comp,local))
    if ellipses==0:return None
    full=[]
    for x,y,comp,local in parts:
        if local is None: local,_=trace(comp,alphamax=1.,opttolerance=.55,turdsize=0,precision=2)
        seg=path_segments(local)
        offset=np.array([x-2.,y-2.])
        for s in seg:
            for key in ('p0','p','p1','p2'):
                if key in s:s[key]+=offset
        full.extend(seg)
    h,w=mask.shape
    svg=compact_svg(full,{'viewBox':f'0 0 {w} {h}','fill':fill,'fill-rule':'evenodd'},1)
    return svg,ellipses

def trace_document(src_mask,foreground_color='#fff',mode='fast',goal='balanced'):
    from potrace_ctypes import trace
    h,w=src_mask.shape
    presets=[(1.,.5),(1.,1.2),(1.,.2)]
    # Long smooth curves for compact geometry; accept only after source-raster QA.
    # Increasing opttolerance is optional and never relaxes the 95% / topology gates.
    if goal in ('balanced','size'):presets += [(1.,1.8),(1.,2.5)]
    if mode=='quality':presets += [(0.65,.3),(1.25,.3),(1.25,.8),(0.65,1.2)]
    results=[]
    info={'viewBox':f'0 0 {w} {h}','fill':foreground_color,'fill-rule':'evenodd'}
    from geometry import path_segments,compact_svg
    for a,opt in presets:
        d,_=trace(src_mask,alphamax=a,opttolerance=opt,turdsize=0,precision=1)
        seg=path_segments(d)
        # Native renderer can be fairly compact after relative command rewriting.
        svg=compact_svg(seg,info,precision=1)
        mask=mask_from_svg(svg,src_mask.shape)
        results.append((svg,{'alpha':a,'opttolerance':opt,'iou':iou(src_mask,mask),'bytes':len(svg.encode()),'segments':draw_count(seg)['segments']}))
    hybrid=ellipse_hybrid(src_mask,foreground_color)
    if hybrid:
        svg,ell=hybrid; mask=mask_from_svg(svg,src_mask.shape)
        results.append((svg,{'kind':'analytic_hybrid','fitted_elliptic_components':ell,'iou':iou(src_mask,mask),'bytes':len(svg.encode()),'segments':None}))
    return results


def save_three(svg,source,out,threshold=None,polarity='auto',min_iou=.95,allow_topology_change=False,aesthetic_override=False,details=None):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    ref,ref_info,_=foreground(source,threshold,polarity)
    from release_gate import source_canvas_check,safe_minify
    # Strict source coordinates: never rescale vector foreground to match the bitmap.
    source_canvas_check(svg,ref.shape)
    svg,optimized=safe_minify(source,svg,threshold=min_iou)
    cand=mask_from_svg(svg,ref.shape)
    stat=qa(ref,cand,True)
    pass_iou=stat['iou']>=min_iou
    pass_topo=stat['topology_preserved'] or allow_topology_change
    if not pass_iou and not aesthetic_override:raise ValueError(f'IoU {stat["iou"]:.4f} below {min_iou:.4f}; keep existing SVG. Set --aesthetic-override only for a visually approved typography tradeoff.')
    if not pass_topo and not aesthetic_override:raise ValueError('Contour topology changed unexpectedly. No output written.')
    # Never overwrite a source SVG, even if caller mistakenly chooses same name.
    if Path(source).resolve()==out.resolve():raise ValueError('Do not overwrite original raster')
    out.write_text(svg,encoding='utf8')
    png=out.with_suffix('.png')
    overlay=out.with_name(out.stem+'_overlay.png')
    stat,ref_info=previews(svg,source,png,overlay,threshold,polarity)
    stat.update({'bytes':len(svg.encode()),'sha256':hashlib.sha256(svg.encode()).hexdigest(),
                 'passes_iou':pass_iou,'passes_topology':pass_topo,
                 'aesthetic_override':bool(aesthetic_override and (not pass_iou or not pass_topo)),
                 'source_mask':ref_info,'files':{'svg':str(out),'png':str(png),'overlay':str(overlay)},
                 'notes':'IoU is raster silhouette agreement, not a typography aesthetics rating'})
    try:
        segments,_=load_one_path(svg)
        stat['smoothness_risks']=seam_risks(segments)
        stat['manual_join_review_recommended']=bool(stat['smoothness_risks'])
    except ValueError:
        stat['smoothness_risks']='unsupported SVG structure; review manually'
        stat['manual_join_review_recommended']=True
    stat['verified_minification']=optimized
    if details:stat['process']=details
    return stat


def doctor():
    import importlib.util,shutil,ctypes.util
    mods={n:bool(importlib.util.find_spec(n)) for n in ['PIL','numpy','cv2','scipy','cairosvg']}
    import ctypes,os
    candidates=[os.environ.get('POTRACE_LIB_PATH'),ctypes.util.find_library('potrace'),
                '/opt/homebrew/lib/libpotrace.dylib','/usr/local/lib/libpotrace.dylib',
                '/usr/lib/x86_64-linux-gnu/libpotrace.so.0',
                '/usr/lib/aarch64-linux-gnu/libpotrace.so.0']
    library=None
    for candidate in candidates:
        if not candidate:continue
        try:
            ctypes.CDLL(candidate)
            library=candidate
            break
        except OSError:pass
    return {'python':sys.version.split()[0],'dependencies':mods,
            'libpotrace':library or 'missing (trace unavailable)',
            'scour':shutil.which('scour'),'inkscape':shutil.which('inkscape'),
            'ready_refine':all(mods.values()),'ready_trace':all(mods.values()) and bool(library)}


def main(argv=None):
    p=argparse.ArgumentParser(prog='r2v.py',description='Typography-aware raster->vector with SVG and visual QA')
    cmd=p.add_subparsers(dest='command',required=True)
    cmd.add_parser('doctor')
    for name in ['trace','refine','audit']:
        c=cmd.add_parser(name)
        if name=='trace':c.add_argument('source')
        elif name=='refine':c.add_argument('svg');c.add_argument('--source',required=True)
        else:c.add_argument('source');c.add_argument('svg')
        c.add_argument('--out',required=True)
        c.add_argument('--threshold',type=int,default=None)
        c.add_argument('--polarity',choices=['auto','light','dark'],default='auto')
        c.add_argument('--min-iou',type=float,default=.95)
        c.add_argument('--aesthetic-override',action='store_true',help='Permit below min-iou ONLY after a human approves the design')
        c.add_argument('--allow-topology-change',action='store_true')
        if name=='trace':
            c.add_argument('--mode',choices=['fast','quality'],default='fast')
            c.add_argument('--goal',choices=['size','balanced','fidelity'],default='balanced')
        if name=='refine':
            c.add_argument('--max-curve-error',type=float,default=.8)
            c.add_argument('--max-join-angle',type=float,default=3.0)
            c.add_argument('--passes',type=int,default=5)
            c.add_argument('--per-pass',type=int,default=12)
    args=p.parse_args(argv)
    t0=time.perf_counter()
    if args.command=='doctor':print(json.dumps(doctor(),ensure_ascii=False,indent=2));return 0
    if not 0<args.min_iou<=1:raise ValueError('--min-iou must be between 0 and 1')
    if args.aesthetic_override and args.min_iou>=.95:
        # user must intentionally document an allowed deviation by setting lower threshold
        print('NOTE: aesthetic override requires explicit typography review before delivery.',file=sys.stderr)
    source=Path(args.source)
    mask,sourceinfo,rgb=foreground(source,args.threshold,args.polarity)
    if args.command=='trace':
        color='#fff' if sourceinfo['polarity']=='light' else '#000'
        options=trace_document(mask,color,args.mode,args.goal)
        from quality import topology
        source_topology=topology(mask)
        eligible=[]
        for item in options:
            candidate_mask=mask_from_svg(item[0],mask.shape)
            if args.allow_topology_change or topology(candidate_mask)==source_topology:
                eligible.append(item)
        if not eligible:raise ValueError('No tracing candidate preserved the original component/counter topology')
        options=eligible
        accepted=[p for p in options if p[1]['iou']>=args.min_iou]
        scored=accepted or options
        best_quality=max(p[1]['iou'] for p in scored)
        if args.goal=='balanced' and accepted:
            scored=[p for p in scored if p[1]['iou']>=best_quality-.005]
        if args.goal=='fidelity' or not accepted:
            svg,meta=max(scored,key=lambda p:(p[1]['iou'],-p[1]['bytes']))
        else:
            svg,meta=min(scored,key=lambda p:(p[1]['bytes'],-p[1]['iou']))
        details={'trace_candidates':len(options),'goal':args.goal,'chosen':meta,'all': [z[1] for z in options]}
    elif args.command=='refine':
        if Path(args.svg).resolve()==Path(args.out).resolve():raise ValueError('Do not overwrite the source SVG; use a new --out path')
        prior=Path(args.svg).read_text(encoding='utf8')
        svg,details=simplify_document(prior,mask,args.min_iou,args.max_curve_error,args.max_join_angle,
                     max(0,args.passes),max(1,args.per_pass),args.allow_topology_change)
    else:
        if Path(args.svg).resolve()==Path(args.out).resolve():raise ValueError('Do not overwrite the source SVG; use a new --out path')
        svg=Path(args.svg).read_text(encoding='utf8');details={'mode':'audit only','input_file':str(args.svg)}
    stat=save_three(svg,source,args.out,args.threshold,args.polarity,args.min_iou,args.allow_topology_change,args.aesthetic_override,details)
    stat['runtime_sec']=round(time.perf_counter()-t0,3)
    print(json.dumps(stat,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        print(json.dumps({'error':str(exc),'status':'failed_no_claim'}),file=sys.stderr)
        sys.exit(2)
