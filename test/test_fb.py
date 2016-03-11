import unittest
import os
from ..unformatted import FortranBinary
import numpy as np

class TestFortranBinary(unittest.TestCase):

    def setUp(self):
        self.tdir, _ = os.path.split(__file__)

    def test_1(self):
        """Read int, float

          integer, parameter :: n = 3
          double precision x(n)
          x = (/ 1.0D0, 2.0D0, 3.0D0 /)
          open(1, file='fort.1', status='new', form='unformatted')
          write(1) n
          write(1) x
          close(1)
          end
        """
        ffile = os.path.join(self.tdir, 'fort.1')
        fb = FortranBinary(ffile)
        # first record is int 3
        next(fb)
        n = fb.readbuf(1, 'i')[0]
        self.assertEqual(n, 3)

        # first record is float 1. 2. 3.
        next(fb)
        xref = (1., 2., 3.)
        x = fb.readbuf(n, 'd')
        np.testing.assert_allclose(x, xref)

    def test_2(self):
        """Find and read label

          character*5 lab
          integer n
          lab = 'LABEL'
          n = 0
          open(1, file='fort.2', status='new', form='unformatted')
          write(1) n
          write(1) lab
          close(1)
          end
        """
        ffile = os.path.join(self.tdir, 'fort.2')
        fb = FortranBinary(ffile)
        rec  = fb.find(b'LABEL')

        self.assertEqual(rec.data, b'LABEL')

    def test_2b(self):
        """Handle label not found

          character*5 lab
          integer n
          lab = 'LABEL'
          n = 0
          open(1, file='fort.2', status='new', form='unformatted')
          write(1) n
          write(1) lab
          close(1)
          end
        """
        ffile = os.path.join(self.tdir, 'fort.2')
        fb = FortranBinary(ffile)
        rec  = fb.find(b'NOLABEL')

        self.assertEqual(rec, None)

    def test_3a(self):
        """Integer*8 dimensions

          integer*8, parameter :: nx = 3, ny=3
          double precision x(nx), y(ny)
          x = (/ 1.0D0, 2.0D0, 3.0D0 /)
          y = (/ 5.0D0, 6.0D0, 7.0D0 /)
          open(3, file='fort.3', status='new', form='unformatted')
          write(3) nx, ny
          write(3) x
          write(3) y
          close(3)
          end

        """
        ffile = os.path.join(self.tdir, 'fort.3')
        fb = FortranBinary(ffile)
        # first record is int 3, 3
        nx, ny = fb.next().read('q', 2)
        np.testing.assert_allclose((nx, ny), (3, 3))

    def test_3b(self):
        """Read vecs

          integer, parameter :: nx = 3, ny=3
          double precision x(nx), y(ny)
          x = (/ 1.0D0, 2.0D0, 3.0D0 /)
          y = (/ 5.0D0, 6.0D0, 7.0D0 /)
          open(3, file='fort.3', status='new', form='unformatted')
          write(3) nx, ny
          write(3) x
          write(3) y
          close(3)
          end

        """
        ffile = os.path.join(self.tdir, 'fort.3')
        fb = FortranBinary(ffile)
        # first record is int 3
        fb.next()
        x=[]
        for rec in fb:
            x += list(fb.readbuf(3, 'd'))
        xref = (1., 2., 3.,  5., 6., 7.)
        np.testing.assert_allclose(x, xref)

    def test_4(self):
        """Read string"""
        ffile = os.path.join(self.tdir, 'fort.4')
        fb = FortranBinary(ffile)
        rec = fb.find('ABC')
        self.assertIn(b'ABC', rec)

    def test_4b(self):
        """Read string"""
        ffile = os.path.join(self.tdir, 'fort.4')
        fb = FortranBinary(ffile)
        rec = fb.find(b'ABC')
        self.assertIn(b'ABC', rec)

    def test_4c(self):
        """Read string"""
        ffile = os.path.join(self.tdir, 'fort.4')
        fb = FortranBinary(ffile)
        with self.assertRaises(ValueError):
            rec = fb.find(1.0)


    def test_count_records_and_lengths(self):
        ffile = os.path.join(self.tdir, 'fort.3')
        fb = FortranBinary(ffile)
        self.assertTupleEqual(fb.record_byte_lengths(), (16, 24, 24))


if __name__ == "__main__":
    unittest.main()
