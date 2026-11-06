"""Adversarial regression cases for true-raster-space verification.

Fixtures are synthetic: keep the user's original AEROID raster files private.
Local benchmarks against those two originals are recorded separately.
"""
import sys
import tempfile
import unittest
from pathlib import Path
import cairosvg
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from release_gate import source_canvas_check,new_seams,gate,safe_minify
from quality import foreground,mask_from_svg,qa
from r2v import save_three


def svg(d, width=240,height=160):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<path d="{d}"/></svg>')


class StrictGeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def raster(self,svg_text,name='source.png'):
        p=self.root/name
        cairosvg.svg2png(bytestring=svg_text.encode(),write_to=str(p),
                         background_color='white')
        return p

    def test_source_space_does_not_stretch_foreground_bboxes(self):
        shape=(160,240)
        self.assertAlmostEqual(source_canvas_check(svg('M1 1H20V20H1Z'),shape),1.)
        with self.assertRaisesRegex(ValueError,'SOURCE_SPACE_MISMATCH'):
            source_canvas_check(svg('M0 0H240V10H0Z',999,10),shape)

    def test_small_wing_hidden_by_large_letter_is_rejected(self):
        original=svg('M8 8H170V150H8ZM186 23H217V35H186Z')
        corrupted=svg('M8 8H170V150H8ZM201 23H232V35H201Z')
        source=self.raster(original)
        ref,_,_=foreground(source)
        self.assertGreater(qa(ref,mask_from_svg(corrupted,ref.shape),False)['iou'],.95)
        self.assertFalse(gate(source,original,corrupted)['passes'])
        self.assertIn('small_feature_regression',gate(source,original,corrupted)['reasons'])

    def test_new_G1_kink_rejected_at_same_endpoint(self):
        old=svg('M10 40C20 40 30 40 40 40C50 40 60 40 70 40L70 100H10Z')
        new=svg('M10 40C20 40 30 40 40 40C50 49 60 40 70 40L70 100H10Z')
        issues=new_seams(old,new)
        self.assertTrue(any(x['type']=='G1' for x in issues))

    def test_new_G2_curvature_jump_rejected(self):
        old=svg('M10 40C20 40 30 40 40 40C50 40 60 40 70 40L70 100H10Z')
        new=svg('M10 40C20 40 30 40 40 40C50 40 60 90 70 40L70 100H10Z')
        issues=new_seams(old,new)
        self.assertTrue(any(x['type']=='G2' for x in issues))

    def test_verified_minifier_never_changes_topology(self):
        original=svg('M12 12C32 12 42 12 62 12L140 12L140 145L12 145Z')
        source=self.raster(original)
        compact,meta=safe_minify(source,original)
        self.assertTrue(gate(source,original,compact)['passes'])
        self.assertLessEqual(len(compact),len(original))

    def test_exactly_three_outputs_and_source_alignment(self):
        original=svg('M10 10H200V130H10Z')
        source=self.raster(original)
        dest=self.root/'vector.svg'
        result=save_three(original,source,dest,min_iou=.95)
        self.assertTrue(result['passes_iou'])
        for name in ('vector.svg','vector.png','vector_overlay.png'):
            self.assertTrue((self.root/name).is_file(),name)
        self.assertEqual(result['source_mask']['method'],'luminance')


if __name__=='__main__':
    unittest.main()
