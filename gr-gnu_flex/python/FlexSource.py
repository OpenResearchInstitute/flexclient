#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 Jonny Slim.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#


import numpy
from gnuradio import gr
from FlexModule.SmartLink import SmartLink
from FlexModule.Radio import Radio
from time import sleep
import FlexModule.DataHandler

class FlexSource(gr.sync_block):
    """
    Source block for FLEX radio connection, streaming audio data
    """
    def __init__(self, serial):
        gr.sync_block.__init__(self,
            name="FlexSource",
            in_sig=None,
            out_sig=[numpy.float32, ])
        self.serial = serial

        self.smartLink = SmartLink()    # relies on a Windows operating machine as it sends "Windows_NT" when registering with radio
        self.radioInfo = self.smartLink.GetRadioFromAvailable(self.serial)
        self.flexRadio = Radio(self.radioInfo, self.smartLink)

        if self.flexRadio.serverHandle:
            receiveThread = FlexModule.DataHandler.ReceiveData(self.flexRadio)
            receiveThread.start()

            self.flexRadio.UpdateAntList()
            self.flexRadio.SendCommand('sub slice all')
            self.flexRadio.SendCommand("sub pan all")

            self.flexRadio.CreateAudioStream(False)

            """ should find a nicer way of doing this """
            for _ in range(5):
                if not self.flexRadio.RxAudioStreamer:
                    sleep(1)
            self.flexRadio.OpenUDPConnection()
        else:
            # raise exception in GR interface
            return


    def work(self, input_items, output_items):
        out = output_items[0]
        # if self.flexRadio.RxAudioStreamer.isCompressed:
            # do Opus decompression
        
        """ list implementation """    
        # temp = numpy.array(self.flexRadio.RxAudioStreamer.outBuffer)
        # out[:] = temp
        # del self.flexRadio.RxAudioStreamer.outBuffer[0:len(temp)]


        """ Queue() implementation"""
        out_len = min(len(output_items[0]), self.flexRadio.RxAudioStreamer.outBuffer.qsize())
        print(out_len, end=" ")
        if out_len == 0:
            return 0

        temp = []
        for i in range(out_len):
            temp.append(self.flexRadio.RxAudioStreamer.outBuffer.get_nowait())
        out[:out_len] = numpy.array(temp)
        
        return out_len

    def setFreq(self, newFreq):
        self.flexRadio.GetSlice(0).Tune(newFreq)

    def setMode(self, newMode):
        self.flexRadio.GetSlice(0).Set(mode=newMode)

    def setAnt(self, newAnt):
        self.flexRadio.GetSlice(0).Set(ant=newAnt)

