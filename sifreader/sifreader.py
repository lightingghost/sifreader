#!/usr/bin/python
# Zhenpeng Zhou <zhenp3ngzhou cir{a} gmail dot com>
# Fri Nov 17 2017


import os
import time
import numpy as np


class SIFFile(object):
    """
    A class that reads the contents and metadata of an Andor .sif file. Compatible with images as well as spectra.
    Exports data as numpy array or xarray.DataArray.

    Example: SIFFile('my_spectrum.sif').read_all()

    In addition to the raw data, SIFFile objects provide a number of meta data variables:
    :ivar x_axis: the horizontal axis (can be pixel numbers or wavelength in nm)
    :ivar original_filename: the original file name of the .sif file
    :ivar date: the date the file was recorded
    :ivar model: camera model
    :ivar temperature: sensor temperature in degrees Celsius
    :ivar exposuretime: exposure time in seconds
    :ivar cycletime: cycle time in seconds
    :ivar accumulations: number of accumulations
    :ivar readout: pixel readout rate in MHz
    :ivar xres: horizontal resolution
    :ivar yres: vertical resolution
    :ivar width: image width
    :ivar height: image height
    :ivar xbin: horizontal binning
    :ivar ybin: vertical binning
    :ivar gain: EM gain level
    :ivar vertical_shift_speed: vertical shift speed
    :ivar pre_amp_gain: pre-amplifier gain
    :ivar stacksize: number of frames
    :ivar filesize: size of the file in bytes
    :ivar m_offset: offset in the .sif file to the actual data
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self._read_header(filepath)

    def __repr__(self):
        info = (('Original Filename', self.original_filename),
                ('Date', self.date),
                ('Camera Model', self.model),
                ('Temperature (deg.C)', '{:f}'.format(self.temperature)),
                ('Exposure Time', '{:f}'.format(self.exposuretime)),
                ('Cycle Time', '{:f}'.format(self.cycletime)),
                ('Number of accumulations', '{:d}'.format(self.accumulations)),
                ('Pixel Readout Rate (MHz)', '{:f}'.format(self.readout)),
                ("Horizontal Camera Resolution", '{:d}'.format(self.xres)),
                ("Vertical Camera Resolution", '{:d}'.format(self.yres)),
                ("Image width", '{:d}'.format(self.width)),
                ("Image Height", '{:d}'.format(self.height)),
                ("Horizontal Binning", '{:d}'.format(self.xbin)),
                ("Vertical Binning", '{:d}'.format(self.ybin)),
                ("EM Gain level", '{:f}'.format(self.gain)),
                ("Vertical Shift Speed", '{:f}'.format(self.vertical_shift_speed)),
                ("Pre-Amplifier Gain", '{:f}'.format(self.pre_amp_gain)),
                ("Stacksize", '{:d}'.format(self.stacksize)),
                ("Filesize", '{:d}'.format(self.filesize)),
                ("Offset to Image Data", '{:f}'.format(self.m_offset)))
        desc_len = max([len(d) for d in list(zip(*info))[0]]) + 3
        res = ''
        for description, value in info:
            res += ('{:' + str(desc_len) + '}{}\n').format(description + ': ', value)

        res = super().__repr__() + '\n' + res
        return res

    def _read_header(self, filepath):
        f = open(filepath, 'rb')
        headerlen = 32
        spool = 0
        i = 0
        while i < headerlen + spool:
            line = f.readline().strip()
            if i == 0:
                if line != b'Andor Technology Multi-Channel File':
                    f.close()
                    raise Exception('{} is not an Andor SIF file'.format(filepath))
            elif i == 2:
                tokens = line.split()
                self.temperature = float(tokens[5])
                self.date = time.strftime('%c', time.localtime(float(tokens[4])))
                self.exposuretime = float(tokens[12])
                self.cycletime = float(tokens[13])
                self.accumulations = int(tokens[15])
                self.readout = 1 / float(tokens[18]) / 1e6
                self.gain = float(tokens[21])
                self.vertical_shift_speed = float(tokens[41])
                self.pre_amp_gain = float(tokens[43])
            elif i == 3:
                self.model = line.decode('utf-8')
            elif i == 5:
                self.original_filename = line.decode('utf-8')
            elif i == 7:
                tokens = line.split()
                if len(tokens) >= 1 and tokens[0] == 'Spooled':
                    spool = 1
            if i == 9:
                wavelength_info = line.split()
                self.center_wavelength = float(wavelength_info[3])
                self.grating = float(wavelength_info[6])
                self.grating_blaze = float(wavelength_info[7])
            if i == 19:
                self.wavelength_coefficients = [float(num) for num in line.split()][::-1]
            if 7 < i < headerlen - 12:
                if len(line) == 17 and line[0:6] == b'65539 ':
                    # and line[7] == b'x01' and line[8] == b'x20' \
                    # and line[9] == b'x00':
                    headerlen = i + 12
            if i == headerlen - 2:
                if line[:12] == b'Pixel number':
                    line = line[12:]
                tokens = line.split()
                if len(tokens) < 6:
                    raise Exception('Not able to read stacksize.')
                self.yres = int(tokens[2])
                self.xres = int(tokens[3])
                self.stacksize = int(tokens[5])
            elif i == headerlen - 1:
                tokens = line.split()
                if len(tokens) < 7:
                    raise Exception("Not able to read Image dimensions.")
                self.left = int(tokens[1])
                self.top = int(tokens[2])
                self.right = int(tokens[3])
                self.bottom = int(tokens[4])
                self.xbin = int(tokens[5])
                self.ybin = int(tokens[6])
            i += 1

        f.close()

        width = self.right - self.left + 1
        mod = width % self.xbin
        self.width = int((width - mod) / self.ybin)
        height = self.top - self.bottom + 1
        mod = height % self.ybin
        self.height = int((height - mod) / self.xbin)

        self.filesize = os.path.getsize(filepath)
        self.datasize = self.width * self.height * 4 * self.stacksize
        self.m_offset = self.filesize - self.datasize - 8

        self.x_axis = np.polyval(self.wavelength_coefficients, np.arange(self.left, self.right + 1))

    def read_block(self, num=0):
        """
        Returns a specific block (i.e. frame) in the .sif file as a numpy array.
        :param num: block number
        :return: a numpy array with shape (y, x)
        """
        f = open(self.filepath, 'rb')
        f.seek(self.m_offset + num * self.width * self.height * 4)
        block = f.read(self.width * self.height * 4)
        data = np.fromstring(block, dtype=np.float32)
        f.close()
        return data.reshape(self.height, self.width)

    def read_all(self):
        """
        Returns all blocks (i.e. frames) in the .sif file as a numpy array.
        :return: a numpy array with shape (blocks, y, x)
        """
        f = open(self.filepath, 'rb')
        f.seek(self.m_offset)
        block = f.read(self.width * self.height * self.stacksize * 4)
        data = np.fromstring(block, dtype=np.float32)
        f.close()
        return data.reshape(self.stacksize, self.height, self.width)

    def as_xarray(self, x_axis_quantity='wavelength'):
        """
        Returns an xarray.DataArray object containing all frames, all metadata and all coordinate axis values. If the
        file contains a spectrum, the wavelength axis can be converted to wavenumbers or photon energy.  This method
        requires the xarray package to be installed.
        :param x_axis_quantity: Only relevant for spectra. Can be either 'wavelength' (default), 'wavenumber' or \
        'photon energy'.
        :return: An xarray.DataArray containing the entire contents of the .sif file.
        """
        try:
            import xarray as xr
            data = self.read_all()
            y_axis = np.arange(data.shape[1])
            # determine if it's an image or a spectrum: check if the x_axis spacing is always one
            if (np.abs((np.diff(self.x_axis) - 1)) < 1e-5).all():
                # it's an image
                x_axis = self.x_axis.astype(np.uint16)
                x_axis_quantity = 'x'
                x_unit = 'px'
                x_name = 'x'
            else:
                # it's a spectrum
                if x_axis_quantity == 'wavelength':
                    x_axis = self.x_axis
                    x_unit = 'nm'
                    x_name = 'Wavelength'
                elif x_axis_quantity == 'wavenumber':
                    x_axis = (1e7 / self.x_axis)[::-1]
                    data = np.flip(data, 2)
                    x_unit = 'cm^-1'
                    x_name = 'Wavenumber'
                elif x_axis_quantity == 'photon_energy':
                    x_axis = (1239.84 / self.x_axis)[::-1]
                    data = np.flip(data, 2)
                    x_unit = 'eV'
                    x_name = 'Photon energy'
                else:
                    raise RuntimeError('X-axis quantity "{}" not recognized!'.format(x_axis_quantity))

            if data.shape[0] == 1:
                # Only one frame
                data = np.transpose(data[0])
                data_array = xr.DataArray(data, coords=[(x_axis_quantity, x_axis), ('y', y_axis)],
                                    name='intensity')
            else:
                # multiple frames
                frame_axis = np.arange(data.shape[0])
                data = np.transpose(data, [2, 1, 0])
                data_array = xr.DataArray(data, coords=[(x_axis_quantity, x_axis), ('y', y_axis),
                                                  ('frames', frame_axis)], name='intensity')
                data_array.frames.attrs['long_name'] = 'Frame number'

            data_array.attrs['long_name'] = 'Intensity'
            data_array.attrs['units'] = 'arb. u.'
            data_array.y.attrs['units'] = 'px'
            data_array[x_axis_quantity].attrs['long_name'] = x_name
            data_array[x_axis_quantity].attrs['units'] = x_unit
            data_array.attrs['sif_metadata'] = str(self)

            return data_array

        except ImportError:
            raise RuntimeError("xarray package required for this method!")
