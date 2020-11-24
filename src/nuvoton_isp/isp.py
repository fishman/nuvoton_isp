# -*- coding: utf-8 -*-
# when you are on 64-bit Windows, MS64\dll\libusb-1.0.dll must be copied into C:\Windows\System32 and
# for running 32-bit applications that use libusb) MS32\dll\libusb-1.0.dll must be copied into C:\Windows\SysWOW64.

import platform
import struct
import time

import usb.core
import usb.util


class Usb:
    ap_file = []
    ap_checksum = 0
    packet_number = 0
    dev = None
    ep_in = None
    name = ""

    def error_return(self):
        print("Checksum cannot be calculated")

        return 0

    def __init__(self):
        # self.name=name
        # print(name)
        self.packet_number = 0
        self.dev = usb.core.find(idVendor=0x0416, idProduct=0x3F00)
        # was it found?

        if self.dev is None:
            raise ValueError('USB Device not found')
        # linux

        if(platform.system() == "Linux"):
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
        self.dev.set_configuration()
        usb.util.claim_interface(self.dev, 0)
        self.dev.reset()
        cfg = self.dev[0]
        intf = cfg[(0, 0)]
        self.ep_in = usb.util.find_descriptor(intf,  # match the first OUT endpoint
                                              custom_match=lambda e: \
                                              usb.util.endpoint_direction(e.bEndpointAddress) == \
                                              usb.util.ENDPOINT_IN)

        ep_out = usb.util.find_descriptor(intf,  # match the first OUT endpoint
                                          custom_match=lambda e: \
                                          usb.util.endpoint_direction(e.bEndpointAddress) == \
                                          usb.util.ENDPOINT_OUT)

    def usb_transfer(self, thelist, PN):
        thelist[4] = PN & 0xff
        thelist[5] = PN >> 8 & 0xff
        thelist[6] = PN >> 16 & 0xff
        thelist[7] = PN >> 24 & 0xff

        test = self.dev.write(0x02, thelist)
        return_str = self.dev.read(0x81, 64, 1000)  # return by string
        return_buffer = bytearray(return_str)
        # print 'rx package'
        # print '[{}]'.format(', '.join(hex(x) for x in return_buffer))

        checksum = 0

        for i in range(64):
            checksum = checksum+thelist[i]
        # print "checksum=0x%x"%checksum
        packege_checksum = 0
        packege_checksum = return_buffer[0]
        packege_checksum = (return_buffer[1] << 8) | packege_checksum

        if checksum != packege_checksum:
            # print("checksum error")
            self.error_return()

        RPN = 0
        RPN = return_buffer[4]
        RPN = (return_buffer[5] << 8) | RPN
        RPN = (return_buffer[6] << 16) | RPN
        RPN = (return_buffer[7] << 24) | RPN

        if RPN != (PN+1):
            # print("package number error")
            self.error_return()

        return return_buffer

    def link_fun(self):
        LINK = [0 for i in range(64)]  # 64 byte data buffer is all zero
        self.packet_number = 0x01
        LINK[0] = 0xae
        self.usb_transfer(LINK, self.packet_number)

    def sn_fun(self):
        self.packet_number = self.packet_number+2
        sn_package = [0 for i in range(64)]
        sn_package[0] = 0xa4
        sn_package[8] = self.packet_number & 0xff
        sn_package[9] = self.packet_number >> 8 & 0xff
        sn_package[10] = self.packet_number >> 16 & 0xff
        sn_package[11] = self.packet_number >> 24 & 0xff
        self.usb_transfer(sn_package, self.packet_number)

    def read_fw_fun(self):
        self.packet_number = self.packet_number+2
        readfw_version = [0 for i in range(64)]
        readfw_version[0] = 0xa6
        buf = self.usb_transfer(readfw_version, self.packet_number)
        FW_VERSION = buf[8]
        # print("FW_VERSION=0x%8x" % FW_VERSION)

    def run_to_aprom_fun(self):
        self.packet_number = self.packet_number+2
        run_to_aprom = [0 for i in range(64)]
        run_to_aprom[0] = 0xab
        self.usb_transfer(run_to_aprom, self.packet_number)

    def read_pid_fun(self):
        self.packet_number = self.packet_number+2
        read_pid = [0 for i in range(64)]
        read_pid[0] = 0xB1
        buf = self.usb_transfer(read_pid, self.packet_number)
        PID = buf[8] | buf[9] << 8 | buf[10] << 16 | buf[11] << 24
        # print("PID=0x%8x" % PID)

    def read_config_fun(self):
        self.packet_number = self.packet_number+2
        READ_CONFIG = [0 for i in range(64)]
        READ_CONFIG[0] = 0xa2
        buf = self.usb_transfer(READ_CONFIG, self.packet_number)
        # CONFIG0 = buf[8] | buf[9] << 8 | buf[10] << 16 | buf[11] << 24
        # CONFIG1 = buf[12] | buf[13] << 8 | buf[14] << 16 | buf[15] << 24
        # print("CONFIG0=0x%8x" % CONFIG0)
        # print("CONFIG1=0x%8x" % CONFIG1)

    def read_aprom_bin_file(self, filename):
        f = open(filename, 'rb')
        self.ap_checksum = 0

        while True:
            x = f.read(1)

            if not x:
                break
            temp = struct.unpack('B', x)
            self.ap_file.append(temp[0])
            self.ap_checksum = self.ap_checksum+temp[0]
        f.close()
        # print(len(self.ap_file))
        # print(self.ap_checksum)

    def usb_transfer_erase(self, thelist, PN):
        thelist[4] = PN & 0xff
        thelist[5] = PN >> 8 & 0xff
        thelist[6] = PN >> 16 & 0xff
        thelist[7] = PN >> 24 & 0xff
        test = self.dev.write(0x02, thelist)
        time.sleep(5)
        return_str = self.dev.read(0x81, 64, 1000)  # return by string
        return_buffer = bytearray(return_str)
        # print 'rx package'
        # print '[{}]'.format(', '.join(hex(x) for x in return_buffer))

        checksum = 0

        for i in range(64):
            checksum = checksum+thelist[i]
        # print "checksum=0x%x"%checksum
        packege_checksum = 0
        packege_checksum = return_buffer[0]
        packege_checksum = (return_buffer[1] << 8) | packege_checksum

        if checksum != packege_checksum:
            # print("checksum error")
            self.error_return()

        RPN = 0
        RPN = return_buffer[4]
        RPN = (return_buffer[5] << 8) | RPN
        RPN = (return_buffer[6] << 16) | RPN
        RPN = (return_buffer[7] << 24) | RPN

        if RPN != (PN+1):
            # print("package number error")
            self.error_return()

        return return_buffer

    def update_aprom(self):
        self.packet_number = self.packet_number+2
        AP_ADRESS = 0
        AP_SIZE = len(self.ap_file)
        pap_command = [0 for i in range(64)]
        pap_command[0] = 0xa0
        # APROM START ADDRESS
        pap_command[8] = AP_ADRESS & 0xff
        pap_command[9] = AP_ADRESS >> 8 & 0xff
        pap_command[10] = AP_ADRESS >> 16 & 0xff
        pap_command[11] = AP_ADRESS >> 24 & 0xff
        # APROM SIZE
        pap_command[12] = AP_SIZE & 0xff
        pap_command[13] = AP_SIZE >> 8 & 0xff
        pap_command[14] = AP_SIZE >> 16 & 0xff
        pap_command[15] = AP_SIZE >> 24 & 0xff
        pap_command[16:64] = self.ap_file[0:48]  # first package to copy
        # print '[{}]'.format(', '.join(hex(x) for x in pap_command))
        self.usb_transfer_erase(pap_command, self.packet_number)

        for i in range(48, AP_SIZE, 56):
            # print(i)
            self.packet_number = self.packet_number+2
            pap1_command = [0 for j in range(64)]
            pap1_command[8:64] = self.ap_file[i:(i+56)]
            # print "test len: %d" % len(pap1_command)

            if len(pap1_command) < 64:
                for k in range(64-len(pap1_command)):
                    pap1_command.append(0xFF)
                    # print '[{}]'.format(', '.join(hex(x) for x in pap1_command))

            if (((AP_SIZE-i) < 56) or ((AP_SIZE-i) == 56)):
                # print "end"
                buf = self.usb_transfer(pap1_command, self.packet_number)
                d_checksum = buf[8] | buf[9] << 8

                if(d_checksum == (self.ap_checksum & 0xffff)):
                    self.error_return()
                    # print("checksum pass")
            else:
                # print "loop"
                self.usb_transfer(pap1_command, self.packet_number)
