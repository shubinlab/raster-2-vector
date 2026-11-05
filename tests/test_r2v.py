"""Run: python -m unittest discover -s tests -v (from skill root)."""
import sys,unittest,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from geometry import path_segments,compact_svg,load_one_path,draw_count,new_segment,angle
from quality import mask_from_svg,qa,topology,foreground,render
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

if __name__=='__main__':unittest.main()
