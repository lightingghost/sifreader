# SIF Reader

This package is designed to read Andor SIF image file.

In addition to raw image data, it provides access to the wavelength axis for spectra, and metadata such as
exposure time, gain, recording date etc. Image data can be read as a `numpy` array or as an
[xarray](https://xarray.pydata.org/en/stable/) `DataArray`, which contains the image data as well as the coordinate
axes and labels in a single object. For spectra, the spectral axis can be returned as nanometers, wavenumbers or
electron volts.

**To the best of our knowledge, this is currently the only Python package that can extract wavelength information
from .sif files using only pure Python and numpy (i.e. without relying on any Andor dll libraries).**

## Requirements
`numpy` (optionally `xarray`, `pytest` to run the unit tests)

## Installation
Install with `pip`:
```
>pip install sifreader
```

## Usage

Open a file and print the metadata:

```
>file = SIFFile('my_image.sif')
>print(file)
<sifreader.sifreader.sifreader.SIFFile object at 0x30f9eecc0>
Original Filename:             E:\test_sequence.sif
Date:                          Thu May 10 12:01:48 2018
...
```

Read a single or all frames contained in the file as numpy arrays:
```
>first_frame = file.read_block(0)
>all_frames = file.read_all()
```

The horizontal axis is contained in the `x_axis` member variable. If the file contains a spectrum, the axis will be
the wavelength in namometers, otherwise it will contain the pixel numbers:
```
>wavelengths = file.x_axis
```

### With the optional xarray package

Read all frames in the file as a `DataArray`:
```
>xarr = file.as_xarray()
```

For spectra: make a `DataArray` that contains the photon energy in eV rather than the default wavelength:
```
>spectrum_file = SIFFile('my_spectrum.sif')
>xarr = spectrum_file.as_xarray('photon_energy')
```
The options for this method are 'wavelength' (default), 'wavenumber' and 'photon_energy'. Note, that this only makes a difference
if the file contains a spectrum. For images, both axes will always contain the pixel numbers.

One of the nice features of `DataArray` is the ability to easily select data and plot it in a single line:
```python
spectrum_file.as_xarray().sel(frames=0, wavelength=slice(749.5, 768.2)).plot()
```

## Version History

- 0.2: Added support for wavelength information, xarray exporting and unit tests
- 0.1: First release
