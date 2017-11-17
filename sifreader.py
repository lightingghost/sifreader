#!/usr/bin/python
# Zhenpeng Zhou <zhenp3ngzhou cir{a} gmail dot com>
# Fri Nov 17 2017


import os
import numpy as np

class SIFFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.read_header(filepath)

    def print_properties(self):
        print('Original Filename:\t\t\t\t%s' % self.original_filename)
        print('Camera Model:\t\t\t\t\t%s' % self.model)
        print('Temperature:\t\t\t\t\t%d deg. C' % self.temperature)
        print('Exposure Time:\t\t\t\t\t%f s' % self.exposuretime)
        print('Cycle Time:\t\t\t\t\t\t%f s' % self.cycletime)
        print('Pixel Readout Rate:\t\t\t\t%f MHz' % self.readout)
        print("Horizontal Camera Resolution:\t%i" % self.xres)
        print("Vertical Camera Resolution:\t\t%i" % self.yres)
        print("Image width:\t\t\t\t\t%i" % self.width)
        print("Image Height:\t\t\t\t\t%i"  % self.height)
        print("Horizontal Binning:\t\t\t\t%i" % self.xbin)
        print("Vertical Binning:\t\t\t\t%i" % self.ybin)
        print("EM Gain level:\t\t\t\t\t%f" %  self.gain)
        print("Vertical Shift Speed:\t\t\t%f s" % self.vertical_shift_speed)
        print("Pre-Amplifier Gain:\t\t\t\t%f" % self.pre_amp_gain)
        print("Stacksize: \t\t\t\t\t\t%i" % self.stacksize)
        print("Filesize: \t\t\t\t\t\t%i" % self.filesize)
        print("Offset to Image Data: \t\t\t%i" % self.m_offset)

    def read_header(self, filepath):

        f = open(filepath,'rb')
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
                self.exposuretime = float(tokens[12])
                self.cycletime = float(tokens[13])
                self.readout = 1 / float(tokens[18]) / 1e6
                self.gain = float(tokens[21])
                self.vertical_shift_speed = float(tokens[41])
                self.pre_amp_gain = float(tokens[43])
            elif i == 3:
                self.model = line
            elif i == 5:
                self.original_filename = line
            elif i == 7:
                tokens = line.split()
                if len(tokens) >= 1 and tokens[0] == 'Spooled':
                    spool = 1
            if i > 7 and i < headerlen - 12:
                if len(line) == 17 \
                    and line[0:6] == b'65539 ':
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

    def read_block(self, num=0):
        f = open(self.filepath, 'rb')
        f.seek(self.m_offset + num * self.width * self.height * 4)
        block = f.read(self.width * self.height * 4)
        data = np.fromstring(block, dtype=np.float32)
        f.close()
        return data.reshape(self.width, self.height)

    def read_all(self):
        f = open(self.filepath, 'rb')
        f.seek(self.m_offset)
        block = f.read(self.width * self.height * self.stacksize * 4)
        data = np.fromstring(block, dtype=np.float32)
        f.close()
        return data.reshape(self.stacksize, self.width, self.height)

def test():
    import matplotlib.pyplot as plt
    sif = SIFFile('0.sif')
    sif.print_properties()
    # first = sif.read_block()
    # plt.figure()
    # plt.imshow(first)
    # plt.show()

    all = sif.read_all()
    img = all[0]
    plt.figure()
    plt.imshow(img)
    plt.show()

test()






