# recommended test runner: py.test

from unittest import TestCase
import os
import numpy as np
file_dir = os.path.dirname(__file__)


class TestSIFFile(TestCase):
    @staticmethod
    def load_asc_file(path):
        import numpy as np
        array = np.genfromtxt(path, skip_footer=38)
        return array[:, 0], array[:, 1:]

    def test_SIFFile_image(self):
        from sifreader.sifreader import SIFFile
        sif_file = SIFFile(os.path.join(file_dir, 'test_image.sif'))
        sif_content = sif_file.read_block(0)
        x_axis, asc_content = self.load_asc_file(os.path.join(file_dir, 'test_image.asc'))
        asc_content = asc_content.T
        assert sif_content.shape == asc_content.shape
        assert (sif_content == asc_content).all()
        assert (x_axis == sif_file.x_axis.astype('uint16')).all()

    def test_SIFFile_spectrum(self):
        from sifreader.sifreader import SIFFile
        sif_file = SIFFile(os.path.join(file_dir, 'test_spectrum.sif'))
        sif_content = sif_file.read_block(0)
        x_axis, asc_content = self.load_asc_file(os.path.join(file_dir, 'test_spectrum.asc'))
        asc_content = asc_content.T
        assert sif_content.shape == asc_content.shape
        assert (sif_content == asc_content).all()
        assert (np.abs(x_axis - sif_file.x_axis) < 1e-5).all()

    def test_SIFFile_sequence(self):
        from sifreader.sifreader import SIFFile
        sif_file = SIFFile(os.path.join(file_dir, 'test_sequence.sif'))
        sif_content = sif_file.read_all()
        assert sif_content.shape[0] == 3
        x_axis, asc_content = self.load_asc_file(os.path.join(file_dir, 'test_sequence.asc'))
        x_axis = x_axis[0:151]
        asc_content = asc_content.reshape((3, 151, 51)).transpose(0, 2, 1)
        assert sif_content.shape == asc_content.shape
        assert (sif_content == asc_content).all()
        assert (np.abs(x_axis - sif_file.x_axis) < 1e-5).all()

    def test_xarray_export_image(self):
        from sifreader.sifreader import SIFFile
        sif_file = SIFFile(os.path.join(file_dir, 'test_image.sif'))
        array = sif_file.as_xarray()
        assert tuple(['x', 'y']) == array.dims
        x_axis, asc_content = self.load_asc_file(os.path.join(file_dir, 'test_image.asc'))
        x_axis = x_axis[0:151]
        assert (np.abs(x_axis - array.x.values) < 1e-5).all()
        assert asc_content.shape == array.values.shape
        assert (array.values == asc_content).all()

    def test_xarray_export_spectrum(self):
        from sifreader.sifreader import SIFFile
        sif_file = SIFFile(os.path.join(file_dir, 'test_spectrum.sif'))
        array = sif_file.as_xarray()
        assert tuple(['wavelength', 'y']) == array.dims
        x_axis, asc_content = self.load_asc_file(os.path.join(file_dir, 'test_spectrum.asc'))
        x_axis = x_axis[0:151]
        assert (np.abs(x_axis - array.wavelength.values) < 1e-5).all()
        assert (array.values == asc_content).all()
        array = sif_file.as_xarray('photon_energy')
        assert tuple(['photon_energy', 'y']) == array.dims
        assert (np.abs(1239.84 / x_axis[::-1] - array.photon_energy.values) < 1e-5).all()
        array = sif_file.as_xarray('wavenumber')
        assert tuple(['wavenumber', 'y']) == array.dims
        assert (np.abs(1e7 / x_axis[::-1] - array.wavenumber.values) < 1e-4).all()

    def test_xarray_export_sequence(self):
        from sifreader.sifreader import SIFFile
        sif_file = SIFFile(os.path.join(file_dir, 'test_sequence.sif'))
        array = sif_file.as_xarray()
        assert tuple(['x', 'y', 'frames']) == array.dims
        x_axis, asc_content = self.load_asc_file(os.path.join(file_dir, 'test_sequence.asc'))
        x_axis = x_axis[0:151]
        assert (np.abs(x_axis - array.x.values) < 1e-5).all()
        asc_content = asc_content.reshape((3, 151, 51)).transpose(1, 2, 0)
        assert (array.values == asc_content).all()
