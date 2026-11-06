#!/usr/bin/env python3
"""Portable two-source release benchmark; private raster files never leave host.

python scripts/benchmark_release.py source1.png source2.png --out /tmp/r2v_bench
"""
from __future__ import annotations
import argparse, json, hashlib, inspect, time
from pathlib import Path
import numpy as np
from quality import foreground, mask_from_svg, qa, previews
from release_gate import safe_minify, source_canvas_check
from potrace_ctypes import trace


def component_minimum(ref, cand):
    import cv2
    n,lab,stats,_=cv2.connectedComponentsWithStats(ref.astype("uint8"),8)
    h,w=ref.shape
    vals=[]
    for i in range(1,n):
        x,y,ww,hh,area=map(int,stats[i])
        if area<25:
            continue
        x0=max(0,x-3);y0=max(0,y-3)
        x1=min(w,x+ww+3);y1=min(h,y+hh+3)
        a=ref[y0:y1,x0:x1];b=cand[y0:y1,x0:x1]
        un=int((a|b).sum());inter=int((a&b).sum())
        vals.append(inter/un if un else 1.)
    return min(vals) if vals else 1.


def run(source:Path,out:Path,min_iou=.95):
    t0=time.monotonic()
    ref,srcinfo,_=foreground(source)
    h,w=ref.shape
    # Settings selected by explicit raster-source benchmarking on two AEROID logos.
    settings=[(1.,.2),(1.,.8),(1.,1.8),(1.,2.5),(1.15,.6)]
    eligible=[];all_stats=[]
    color='#fff' if srcinfo['polarity']=='light' else '#000'
    for alpha,tolerance in settings:
        d,info=trace(ref,alphamax=alpha,opttolerance=tolerance,turdsize=1,precision=1)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><path fill="{color}" fill-rule="evenodd" d="{d}"/></svg>'
        checked,optimization=safe_minify(source,svg,min_iou)
        source_canvas_check(checked,ref.shape)
        candidate=mask_from_svg(checked,ref.shape)
        stat=qa(ref,candidate,True)
        local_min=component_minimum(ref,candidate)
        row={'alpha':alpha,'tolerance':tolerance,'bytes':len(checked.encode()),
             'iou':stat['iou'],'min_component_iou':round(local_min,6),
             'topology_preserved':stat['topology_preserved'],
             'segments':info['commands']}
        all_stats.append(row)
        if stat['iou']>=min_iou and local_min>=min_iou and stat['topology_preserved']:
            eligible.append((checked,row))
    if not eligible:
        return {'source':str(source),'status':'rejected','candidates':all_stats}
    svg,best=min(eligible,key=lambda x:(x[1]['bytes'],-x[1]['iou']))
    out.mkdir(parents=True,exist_ok=True)
    svg_path=out/(source.stem+'.svg')
    svg_path.write_text(svg,encoding='utf8')
    png=svg_path.with_suffix('.png')
    overlay=out/(source.stem+'_overlay.png')
    # Verify exact saved bytes, not the string used before writing.
    final=svg_path.read_text(encoding='utf8')
    final_mask=mask_from_svg(final,ref.shape)
    final_qa=qa(ref,final_mask,True)
    assert final_qa['iou']>=min_iou and final_qa['topology_preserved']
    assert component_minimum(ref,final_mask)>=min_iou
    previews(final,source,png,overlay)
    assert all(f.exists() and f.stat().st_size>0 for f in (svg_path,png,overlay))
    return {'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'status':'passed','best':best,'candidates':all_stats,'time_s':round(time.monotonic()-t0,3),
            'files':[str(svg_path),str(png),str(overlay)]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('sources',type=Path,nargs='+')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--min-iou',type=float,default=.95)
    a=p.parse_args()
    results=[run(x,a.out,a.min_iou) for x in a.sources]
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(json.dumps(results,ensure_ascii=False,indent=2))
    return 0 if all(x['status']=='passed' for x in results) else 2


if __name__=='__main__':raise SystemExit(main())
