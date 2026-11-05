"""Run: python -m unittest discover -s tests -v (from skill root)."""
import sys,unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geometry import path_segments,compact_svg,load_one_path,draw_count,new_segment,angle,seam_risks,new_kinks
from quality import mask_from_svg,qa,topology,foreground,render,component_ious,component_regressions
from r2v import simplify_document

class GeometryTests(unittest.TestCase):
    def test_h_v_roundtrip(self):
        # Regression: no boolean indexing on x/y for horizontal/vertical SVG path commands.
        s='<svg xmlns="http://www.w3.org/2000/svg" fill="#fff" viewBox="0 0 100 100"><path d="M10 10H40V40H10Z"/></svg>'
        segments,meta=load_one_path(s)
        rebuilt=compact_svg(segments,meta,0)
        self.assertTrue(np.array_equal(mask_from_svg(s,(100,100)),mask_from_svg(rebuilt,(100,100))))
        self.assertEqual(draw_count(segments)['lines'],3)
    def test_quadratic_bezier_roundtrip(self):
        s='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="#fff" d="M10 10Q35 60 60 10L70 60Z"/></svg>'
        seg,info=load_one_path(s)
        v=compact_svg(seg,info,2)
        self.assertGreater(qa(mask_from_svg(s,(100,100)),mask_from_svg(v,(100,100)),False)['iou'],.99)
    def test_reject_image_and_fonts(self):
        with self.assertRaises(ValueError):
            render('<svg xmlns="http://www.w3.org/2000/svg"><image href="file:///private.png"/></svg>',100,100)
    def test_smooth_join_locked(self):
        s1={'kind':'L','p0':np.array([0.,0.]),'p':np.array([10.,0.])}
        s2={'kind':'C','p0':np.array([10.,0.]),'p1':np.array([15.,0.]),'p2':np.array([20.,10.]),'p':np.array([20.,15.])}
        fit=new_segment([s1,s2],max_err=8,max_join_angle=2)
        self.assertIsNotNone(fit)
        new,err=fit
        self.assertAlmostEqual(angle(s1,new),0,places=4)
    def test_never_smooth_purposeful_corner(self):
        a={'kind':'L','p0':np.array([0.,0.]),'p':np.array([10.,0.])}
        b={'kind':'L','p0':np.array([10.,0.]),'p':np.array([10.,10.])}
        self.assertIsNone(new_segment([a,b],max_join_angle=5))
    def test_do_not_break_counters(self):
        svg='<svg xmlns="http://www.w3.org/2000/svg" fill="#fff" viewBox="0 0 120 120"><path fill-rule="evenodd" d="M10 10H110V110H10ZM40 40V80H80V40Z"/></svg>'
        source=mask_from_svg(svg,(120,120))
        v,report=simplify_document(svg,source,min_iou=.995)
        out=mask_from_svg(v,(120,120))
        self.assertEqual(topology(out),topology(source))
        self.assertGreater(qa(source,out,False)['iou'],.995)
    def test_low_iou_rejected(self):
        svg='<svg xmlns="http://www.w3.org/2000/svg" fill="#fff" viewBox="0 0 100 100"><path d="M2 2H10V10H2Z"/></svg>'
        ref=np.ones((100,100),dtype=bool)
        with self.assertRaises(ValueError):simplify_document(svg,ref,min_iou=.95)


class SmoothnessRegressionTests(unittest.TestCase):
    def test_new_kink_is_rejected_even_when_shape_is_similar(self):
        # Short wing junction: a tiny area difference can hide a large tangent jump.
        a={'kind':'C','p0':np.array([0.,0.]),'p1':np.array([3.,0.]),
           'p2':np.array([7.,0.]),'p':np.array([10.,0.])}
        b={'kind':'C','p0':np.array([10.,0.]),'p1':np.array([13.,0.]),
           'p2':np.array([17.,1.]),'p':np.array([20.,2.])}
        damaged=dict(b,p1=np.array([12.,2.]))
        self.assertEqual(seam_risks([a,b]),[])
        self.assertTrue(new_kinks([a,b],[a,damaged]))
        self.assertFalse(new_kinks([a,b],[a,b]))

    def test_small_wing_cannot_hide_behind_large_letter_iou(self):
        # The large letter dominates global mask IoU but must not conceal wing loss.
        good='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 180"><path d="M8 8H160V168H8ZM177 20H205V30H177Z"/></svg>'
        moved='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 180"><path d="M8 8H160V168H8ZM187 20H215V30H187Z"/></svg>'
        ref=mask_from_svg(good,(180,240))
        out=mask_from_svg(moved,(180,240))
        self.assertGreater(qa(ref,out,False)['iou'],.95)
        self.assertEqual(topology(ref),topology(out))
        self.assertTrue(component_regressions(ref,ref,out))
        self.assertLess(min(x['iou'] for x in component_ious(ref,out)),.8)

    def test_nearly_reflected_handle_does_not_become_shorthand_s(self):
        # Prior 0.49px tolerance silently replaced a genuine C control with S.
        svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50"><path d="M1 1C4 1 8 1 10 1C12.3 1 18 1 21 1Z"/></svg>'
        seg,info=load_one_path(svg)
        out=compact_svg(seg,info,1)
        path=out.split('d="',1)[1].split('"',1)[0]
        self.assertNotIn('s',path)
        self.assertEqual(len(new_kinks(seg,load_one_path(out)[0])),0)


if __name__=='__main__':unittest.main()
