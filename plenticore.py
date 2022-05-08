#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  kostal_modbusquery - Read only query of the Kostal Plenticore Inverters using TCP/IP modbus protocol
#  Copyright (C) 2018  Kilian Knoll
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#  Please note that any incorrect or careless usage of this module as well as errors in the implementation can damage your Inverter!
#  Therefore, the author does not provide any guarantee or warranty concerning to correctness, functionality or performance and does not accept any liability for damage caused by this module, examples or mentioned information.
#  Thus, use it at your own risk!
#
#
#  Purpose:
#           Query values from Kostal inverter
#           Used with Kostal Plenticore Plus 10
#  Based on the documentation provided by Kostal:
#           https://www.kostal-solar-electric.com/en-gb/download/download#PLENTICORE%20plus/PLENTICORE%20plus%204.2/Worldwide/Interfaces%20protocols/
#
# Requires pymodbus
# Tested with:
#           python 3.5
#           pymodbus 2.10
# Please change the IP address of your Inverter (e.g. 192.168.178.41 and Port (default 1502) to suite your environment - see below)
#
import pymodbus
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from vedbus import VeDbusService
from dbus.mainloop.glib import DBusGMainLoop
try:
    import gobject  # Python 2.x
except:
    from gi.repository import GLib as gobject  # Python 3.x
import dbus
import dbus.service
import sys
import os
import platform

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(
    __file__), '/opt/victronenergy/dbus-modem'))

# Again not all of these needed this is just duplicating the Victron code.


class SystemBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SYSTEM)


class SessionBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SESSION)


def dbusconnection():
    return SessionBus() if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else SystemBus()


powerAC = 0.0
currentL1 = 0.0
currentL2 = 0.0
currentL3 = 0.0
voltageL1 = 0.0
voltageL2 = 0.0
voltageL3 = 0.0
powerPV = 0.0

# Have a mainloop, so we can send/receive asynchronous calls to and from dbus
DBusGMainLoop(set_as_default=True)


class kostal_modbusquery:
    def __init__(self):
        #Change the IP address and port to suite your environment:
        self.inverter_ip="192.168.169.9"
        self.inverter_port="1502"
        #No more changes required beyond this point
        self.KostalRegister = []
        self.Adr6=[]
        self.Adr6=[6]
        self.Adr6.append("Inverter article number")
        self.Adr6.append("Strg8")
        self.Adr6.append(0)
        
        self.Adr46=[]
        self.Adr46 =[46]
        self.Adr46.append("Software-Version IO-Controller (IOC)")
        self.Adr46.append("Strg8")
        self.Adr46.append(0) 
        
        self.Adr100=[]
        self.Adr100 =[100]
        self.Adr100.append("Total DC power")
        self.Adr100.append("Float")
        self.Adr100.append(0) 
                
        self.Adr104=[]
        self.Adr104 =[104]
        self.Adr104.append("State of energy manager")
        self.Adr104.append("Float")
        self.Adr104.append(0) 
        
        self.Adr106=[]
        self.Adr106 =[106]
        self.Adr106.append("Home own consumption from battery")
        self.Adr106.append("Float")
        self.Adr106.append(0) 
        
        self.Adr108=[]
        self.Adr108 =[108]
        self.Adr108.append("Home own consumption from grid")
        self.Adr108.append("Float")
        self.Adr108.append(0) 
        
        self.Adr110=[]
        self.Adr110 =[110]
        self.Adr110.append("Total home consumption PV")
        self.Adr110.append("Float")
        self.Adr110.append(0) 
        
        self.Adr112=[]
        self.Adr112 =[112]
        self.Adr112.append("Total home consumption Grid")
        self.Adr112.append("Float")
        self.Adr112.append(0) 

        self.Adr114=[]
        self.Adr114 =[114]
        self.Adr114.append("Total home consumption Battery")
        self.Adr114.append("Float")
        self.Adr114.append(0) 

        self.Adr116=[]
        self.Adr116 =[116]
        self.Adr116.append("Home own consumption from PV")
        self.Adr116.append("Float")
        self.Adr116.append(0) 

        self.Adr118=[]
        self.Adr118 =[118]
        self.Adr118.append("Total home consumption")
        self.Adr118.append("Float")
        self.Adr118.append(0) 

        self.Adr120=[]
        self.Adr120 =[120]
        self.Adr120.append("Isolation resistance")
        self.Adr120.append("Float")
        self.Adr120.append(0) 

        self.Adr122=[]
        self.Adr122 =[122]
        self.Adr122.append("Power limit from EVU")
        self.Adr122.append("Float")
        self.Adr122.append(0) 

        self.Adr124=[]
        self.Adr124 =[124]
        self.Adr124.append("Total home consumption rate")
        self.Adr124.append("Float")
        self.Adr124.append(0) 

        self.Adr144=[]
        self.Adr144 =[144]
        self.Adr144.append("Worktime")
        self.Adr144.append("Float")
        self.Adr144.append(0) 

        self.Adr150=[]
        self.Adr150 =[150]
        self.Adr150.append("Actual cos phi")
        self.Adr150.append("Float")
        self.Adr150.append(0) 

        self.Adr152=[]
        self.Adr152 =[152]
        self.Adr152.append("Grid frequency")
        self.Adr152.append("Float")
        self.Adr152.append(0) 

        self.Adr154=[]
        self.Adr154 =[154]
        self.Adr154.append("Current Phase 1")
        self.Adr154.append("Float")
        self.Adr154.append(0) 

        self.Adr156=[]
        self.Adr156 =[156]
        self.Adr156.append("Active power Phase 1")
        self.Adr156.append("Float")
        self.Adr156.append(0) 

        self.Adr158=[]
        self.Adr158 =[158]
        self.Adr158.append("Voltage Phase 1")
        self.Adr158.append("Float")
        self.Adr158.append(0) 

        self.Adr160=[]
        self.Adr160 =[160]
        self.Adr160.append("Current Phase 2")
        self.Adr160.append("Float")
        self.Adr160.append(0) 

        self.Adr162=[]
        self.Adr162 =[162]
        self.Adr162.append("Active power Phase 2")
        self.Adr162.append("Float")
        self.Adr162.append(0) 

        self.Adr164=[]
        self.Adr164 =[164]
        self.Adr164.append("Voltage Phase 2")
        self.Adr164.append("Float")
        self.Adr164.append(0) 

        self.Adr166=[]
        self.Adr166 =[166]
        self.Adr166.append("Current Phase 3")
        self.Adr166.append("Float")
        self.Adr166.append(0) 

        self.Adr168=[]
        self.Adr168 =[168]
        self.Adr168.append("Active power Phase 3")
        self.Adr168.append("Float")
        self.Adr168.append(0) 

        self.Adr170=[]
        self.Adr170 =[170]
        self.Adr170.append("Voltage Phase 3")
        self.Adr170.append("Float")
        self.Adr170.append(0) 

        self.Adr172=[]
        self.Adr172 =[172]
        self.Adr172.append("Total AC active power")
        self.Adr172.append("Float")
        self.Adr172.append(0) 

        self.Adr174=[]
        self.Adr174 =[174]
        self.Adr174.append("Total AC reactive power")
        self.Adr174.append("Float")
        self.Adr174.append(0) 

        self.Adr178=[]
        self.Adr178 =[178]
        self.Adr178.append("Total AC apparent power")
        self.Adr178.append("Float")
        self.Adr178.append(0) 

        self.Adr190=[]
        self.Adr190 =[190]
        self.Adr190.append("Battery charge current")
        self.Adr190.append("Float")
        self.Adr190.append(0) 

        self.Adr194=[]
        self.Adr194 =[194]
        self.Adr194.append("Number of battery cycles")
        self.Adr194.append("Float")
        self.Adr194.append(0) 

        self.Adr200=[]
        self.Adr200 =[200]
        self.Adr200.append("Actual battery charge -minus or discharge -plus current")
        self.Adr200.append("Float")
        self.Adr200.append(0) 

        self.Adr202=[]
        self.Adr202 =[202]
        self.Adr202.append("PSSB fuse state")
        self.Adr202.append("Float")
        self.Adr202.append(0) 

        self.Adr208=[]
        self.Adr208 =[208]
        self.Adr208.append("Battery ready flag")
        self.Adr208.append("Float")
        self.Adr208.append(0) 
                        
        self.Adr210=[]
        self.Adr210 =[210]
        self.Adr210.append("Act. state of charge")
        self.Adr210.append("Float")
        self.Adr210.append(0) 

        self.Adr212=[]
        self.Adr212 =[212]
        self.Adr212.append("Battery state")
        self.Adr212.append("Float")
        self.Adr212.append(0) 

        self.Adr214=[]
        self.Adr214 =[214]
        self.Adr214.append("Battery temperature")
        self.Adr214.append("Float")
        self.Adr214.append(0) 

        self.Adr216=[]
        self.Adr216 =[216]
        self.Adr216.append("Battery voltage")
        self.Adr216.append("Float")
        self.Adr216.append(0) 

        self.Adr218=[]
        self.Adr218 =[100]
        self.Adr218.append("Cos phi (powermeter)")
        self.Adr218.append("Float")
        self.Adr218.append(0) 

        self.Adr220=[]
        self.Adr220 =[220]
        self.Adr220.append("Frequency (powermeter)")
        self.Adr220.append("Float")
        self.Adr220.append(0) 

        self.Adr222=[]
        self.Adr222 =[222]
        self.Adr222.append("Current phase 1 (powermeter)")
        self.Adr222.append("Float")
        self.Adr222.append(0) 

        self.Adr224=[]
        self.Adr224 =[224]
        self.Adr224.append("Active power phase 1 (powermeter)")
        self.Adr224.append("Float")
        self.Adr224.append(0) 

        self.Adr226=[]
        self.Adr226 =[226]
        self.Adr226.append("Reactive power phase 1 (powermeter)")
        self.Adr226.append("Float")
        self.Adr226.append(0) 

        self.Adr228=[]
        self.Adr228 =[228]
        self.Adr228.append("Apparent power phase 1 (powermeter)")
        self.Adr228.append("Float")
        self.Adr228.append(0) 

        self.Adr230=[]
        self.Adr230 =[230]
        self.Adr230.append("Voltage phase 1 (powermeter)")
        self.Adr230.append("Float")
        self.Adr230.append(0) 

        self.Adr232=[]
        self.Adr232 =[232]
        self.Adr232.append("Current phase 2 (powermeter)")
        self.Adr232.append("Float")
        self.Adr232.append(0) 

        self.Adr234=[]
        self.Adr234 =[234]
        self.Adr234.append("Active power phase 2 (powermeter)")
        self.Adr234.append("Float")
        self.Adr234.append(0) 

        self.Adr236=[]
        self.Adr236 =[236]
        self.Adr236.append("Reactive power phase 2 (powermeter)")
        self.Adr236.append("Float")
        self.Adr236.append(0) 

        self.Adr238=[]
        self.Adr238 =[238]
        self.Adr238.append("Apparent power phase 2 (powermeter)")
        self.Adr238.append("Float")
        self.Adr238.append(0) 

        self.Adr240=[]
        self.Adr240 =[240]
        self.Adr240.append("Voltage phase 2 (powermeter)")
        self.Adr240.append("Float")
        self.Adr240.append(0) 

        self.Adr242=[]
        self.Adr242 =[242]
        self.Adr242.append("Current phase 3 (powermeter)")
        self.Adr242.append("Float")
        self.Adr242.append(0) 

        self.Adr244=[]
        self.Adr244 =[244]
        self.Adr244.append("Active power phase 3 (powermeter)")
        self.Adr244.append("Float")
        self.Adr244.append(0) 

        self.Adr246=[]
        self.Adr246 =[246]
        self.Adr246.append("Reactive power phase 3 (powermeter)")
        self.Adr246.append("Float")
        self.Adr246.append(0) 

        self.Adr248=[]
        self.Adr248 =[248]
        self.Adr248.append("Apparent power phase 3 (powermeter)")
        self.Adr248.append("Float")
        self.Adr248.append(0) 

        self.Adr250=[]
        self.Adr250 =[250]
        self.Adr250.append("Voltage phase 3 (powermeter)")
        self.Adr250.append("Float")
        self.Adr250.append(0) 

        self.Adr252=[]
        self.Adr252 =[252]
        powerAC = [252]
        self.Adr252.append("Total active power (powermeter)")
        self.Adr252.append("Float")
        self.Adr252.append(0) 

        self.Adr254=[]
        self.Adr254 =[254]
        self.Adr254.append("Total reactive power (powermeter)")
        self.Adr254.append("Float")
        self.Adr254.append(0) 
                                                                                                                                                                                      
        self.Adr256=[]
        self.Adr256 =[256]
        self.Adr256.append("Total apparent power (powermeter)")
        self.Adr256.append("Float")
        self.Adr256.append(0) 

        self.Adr258=[]
        self.Adr258 =[258]
        self.Adr258.append("Current DC1")
        self.Adr258.append("Float")
        self.Adr258.append(0) 

        self.Adr260=[]
        self.Adr260 =[260]
        self.Adr260.append("Power DC1")
        self.Adr260.append("Float")
        self.Adr260.append(0) 

        self.Adr266=[]
        self.Adr266 =[100]
        self.Adr266.append("Voltage DC1")
        self.Adr266.append("Float")
        self.Adr266.append(0) 

        self.Adr268=[]
        self.Adr268 =[268]
        self.Adr268.append("Current DC2")
        self.Adr268.append("Float")
        self.Adr268.append(0) 

        self.Adr270=[]
        self.Adr270 =[270]
        self.Adr270.append("Power DC2")
        self.Adr270.append("Float")
        self.Adr270.append(0) 

        self.Adr276=[]
        self.Adr276 =[276]
        self.Adr276.append("Voltage DC2")
        self.Adr276.append("Float")
        self.Adr276.append(0) 

        self.Adr278=[]
        self.Adr278 =[278]
        self.Adr278.append("Current DC3")
        self.Adr278.append("Float")
        self.Adr278.append(0) 

        self.Adr280=[]
        self.Adr280 =[280]
        self.Adr280.append("Power DC3")
        self.Adr280.append("Float")
        self.Adr280.append(0) 

        self.Adr286=[]
        self.Adr286 =[286]
        self.Adr286.append("Voltage DC3")
        self.Adr286.append("Float")
        self.Adr286.append(0) 

        self.Adr320=[]
        self.Adr320 =[320]
        self.Adr320.append("Total yield")
        self.Adr320.append("Float")
        self.Adr320.append(0) 

        self.Adr322=[]
        self.Adr322 =[322]
        self.Adr322.append("Daily yield")
        self.Adr322.append("Float")
        self.Adr322.append(0) 

        self.Adr324=[]
        self.Adr324 =[324]
        self.Adr324.append("Yearly yield")
        self.Adr324.append("Float")
        self.Adr324.append(0) 

        self.Adr326=[]
        self.Adr326 =[326]
        self.Adr326.append("Monthly yield")
        self.Adr326.append("Float")
        self.Adr326.append(0) 

        self.Adr514=[]
        self.Adr514 =[514]
        self.Adr514.append("Battery actual SOC")
        self.Adr514.append("U16")
        self.Adr514.append(0) 

        self.Adr531=[]
        self.Adr531 =[531]
        self.Adr531.append("Inverter Max Power")
        self.Adr531.append("Float")
        self.Adr531.append(0)
        
        self.Adr575=[]
        self.Adr575 =[575]
        self.Adr575.append("Inverter Generation Power (actual)")
        self.Adr575.append("S16")
        self.Adr575.append(0)      

        self.Adr578=[]
        self.Adr578 =[578]
        self.Adr578.append("Total energy")
        self.Adr578.append("U32")
        self.Adr578.append(0)

        self.Adr582=[]
        self.Adr582 =[582]
        self.Adr582.append("Actual battery charge-discharge power")
        self.Adr582.append("S16")
        self.Adr582.append(0)

    # -----------------------------------------
    # Routine to read a string from one address with 8 registers
    def ReadStr8(self, myadr_dec):
        r1 = self.client.read_holding_registers(myadr_dec, 8, unit=71)
        STRG8Register = BinaryPayloadDecoder.fromRegisters(
            r1.registers, byteorder=Endian.Big)
        result_STRG8Register = STRG8Register.decode_string(8)
        return(result_STRG8Register)
    # -----------------------------------------
    # Routine to read a Float from one address with 2 registers

    def ReadFloat(self, myadr_dec):
        r1 = self.client.read_holding_registers(myadr_dec, 2, unit=71)
        FloatRegister = BinaryPayloadDecoder.fromRegisters(
            r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_FloatRegister = round(FloatRegister.decode_32bit_float(), 2)
        return(result_FloatRegister)
    # -----------------------------------------
    # Routine to read a U16 from one address with 1 register

    def ReadU16_1(self, myadr_dec):
        r1 = self.client.read_holding_registers(myadr_dec, 1, unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(
            r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return(result_U16register)
    # -----------------------------------------
    # Routine to read a U16 from one address with 2 registers

    def ReadU16_2(self, myadr_dec):
        r1 = self.client.read_holding_registers(myadr_dec, 2, unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(
            r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return(result_U16register)
    # -----------------------------------------
    # Routine to read a U32 from one address with 2 registers

    def ReadU32(self, myadr_dec):
        r1 = self.client.read_holding_registers(myadr_dec, 8, unit=71)
        U32register = BinaryPayloadDecoder.fromRegisters(
            r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U32register = U32register.decode_32bit_uint()
        return(result_U32register)
    # -----------------------------------------
    # Routine to read a U32 from one address with 2 registers

    def ReadS16(self, myadr_dec):
        r1 = self.client.read_holding_registers(myadr_dec, 1, unit=71)
        S16register = BinaryPayloadDecoder.fromRegisters(
            r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_S16register = S16register.decode_16bit_uint()
        return(result_S16register)

    try:
        def run(self):

            self.client = ModbusTcpClient(
                self.inverter_ip, port=self.inverter_port)
            self.client.connect()

            # LONG List of reads...
            self.Adr6[3] = self.ReadStr8(self.Adr6[0])
            self.Adr46[3] = self.ReadStr8(self.Adr46[0])
            self.Adr100[3] = self.ReadFloat(self.Adr100[0])
            self.Adr104[3] = self.ReadFloat(self.Adr104[0])
            self.Adr106[3] = self.ReadFloat(self.Adr106[0])
            self.Adr108[3] = self.ReadFloat(self.Adr108[0])
            self.Adr110[3] = self.ReadFloat(self.Adr110[0])
            self.Adr112[3] = self.ReadFloat(self.Adr112[0])
            self.Adr114[3] = self.ReadFloat(self.Adr114[0])
            self.Adr116[3] = self.ReadFloat(self.Adr116[0])
            self.Adr118[3] = self.ReadFloat(self.Adr118[0])
            self.Adr120[3] = self.ReadFloat(self.Adr120[0])
            self.Adr122[3] = self.ReadFloat(self.Adr122[0])
            self.Adr124[3] = self.ReadFloat(self.Adr124[0])
            self.Adr144[3] = self.ReadFloat(self.Adr144[0])
            self.Adr150[3] = self.ReadFloat(self.Adr150[0])
            self.Adr152[3] = self.ReadFloat(self.Adr152[0])
            self.Adr154[3] = self.ReadFloat(self.Adr154[0])
            self.Adr156[3] = self.ReadFloat(self.Adr156[0])
            self.Adr158[3] = self.ReadFloat(self.Adr158[0])
            self.Adr160[3] = self.ReadFloat(self.Adr160[0])
            self.Adr162[3] = self.ReadFloat(self.Adr162[0])
            self.Adr162[3] = self.ReadFloat(self.Adr162[0])
            self.Adr164[3] = self.ReadFloat(self.Adr164[0])
            self.Adr166[3] = self.ReadFloat(self.Adr166[0])
            self.Adr168[3] = self.ReadFloat(self.Adr168[0])
            self.Adr170[3] = self.ReadFloat(self.Adr170[0])
            self.Adr172[3] = self.ReadFloat(self.Adr172[0])
            self.Adr174[3] = self.ReadFloat(self.Adr174[0])
            self.Adr178[3] = self.ReadFloat(self.Adr178[0])
            self.Adr190[3] = self.ReadFloat(self.Adr190[0])
            self.Adr194[3] = self.ReadFloat(self.Adr194[0])
            self.Adr200[3] = self.ReadFloat(self.Adr200[0])
            self.Adr202[3] = self.ReadFloat(self.Adr202[0])
            self.Adr208[3] = self.ReadFloat(self.Adr208[0])
            self.Adr210[3] = self.ReadFloat(self.Adr210[0])
            self.Adr212[3] = self.ReadFloat(self.Adr212[0])
            self.Adr214[3] = self.ReadFloat(self.Adr214[0])
            self.Adr216[3] = self.ReadFloat(self.Adr216[0])
            self.Adr218[3] = self.ReadFloat(self.Adr218[0])
            self.Adr220[3] = self.ReadFloat(self.Adr220[0])
            self.Adr222[3] = self.ReadFloat(self.Adr222[0])
            self.Adr224[3] = self.ReadFloat(self.Adr224[0])
            self.Adr226[3] = self.ReadFloat(self.Adr226[0])
            self.Adr228[3] = self.ReadFloat(self.Adr228[0])
            self.Adr230[3] = self.ReadFloat(self.Adr230[0])
            self.Adr232[3] = self.ReadFloat(self.Adr232[0])
            self.Adr234[3] = self.ReadFloat(self.Adr234[0])
            self.Adr236[3] = self.ReadFloat(self.Adr236[0])
            self.Adr238[3] = self.ReadFloat(self.Adr238[0])
            self.Adr240[3] = self.ReadFloat(self.Adr240[0])
            self.Adr242[3] = self.ReadFloat(self.Adr242[0])
            self.Adr244[3] = self.ReadFloat(self.Adr244[0])
            self.Adr246[3] = self.ReadFloat(self.Adr246[0])
            self.Adr248[3] = self.ReadFloat(self.Adr248[0])
            self.Adr250[3] = self.ReadFloat(self.Adr250[0])
            self.Adr252[3] = self.ReadFloat(self.Adr252[0])
            self.Adr254[3] = self.ReadFloat(self.Adr254[0])
            self.Adr256[3] = self.ReadFloat(self.Adr256[0])
            self.Adr258[3] = self.ReadFloat(self.Adr258[0])
            self.Adr260[3] = self.ReadFloat(self.Adr260[0])
            self.Adr266[3] = self.ReadFloat(self.Adr266[0])
            self.Adr268[3] = self.ReadFloat(self.Adr268[0])
            self.Adr270[3] = self.ReadFloat(self.Adr270[0])
            self.Adr276[3] = self.ReadFloat(self.Adr276[0])
            self.Adr278[3] = self.ReadFloat(self.Adr278[0])
            self.Adr280[3] = self.ReadFloat(self.Adr280[0])
            self.Adr286[3] = self.ReadFloat(self.Adr286[0])
            self.Adr320[3] = self.ReadFloat(self.Adr320[0])
            self.Adr322[3] = self.ReadFloat(self.Adr322[0])
            self.Adr324[3] = self.ReadFloat(self.Adr324[0])
            self.Adr326[3] = self.ReadFloat(self.Adr326[0])
            self.Adr514[3] = self.ReadU16_1(self.Adr514[0])
            self.Adr531[3] = self.ReadU16_1(self.Adr531[0])
            self.Adr575[3] = self.ReadS16(self.Adr575[0])
            # self.Adr578[3]=self.ReadU32(self.Adr578[0])        #Having issues with this one
            self.Adr582[3] = self.ReadS16(self.Adr582[0])

            self.KostalRegister = []
            self.KostalRegister.append(self.Adr6)
            self.KostalRegister.append(self.Adr46)
            self.KostalRegister.append(self.Adr104)
            self.KostalRegister.append(self.Adr106)
            self.KostalRegister.append(self.Adr108)
            self.KostalRegister.append(self.Adr110)
            self.KostalRegister.append(self.Adr112)
            self.KostalRegister.append(self.Adr114)
            self.KostalRegister.append(self.Adr116)
            self.KostalRegister.append(self.Adr118)
            self.KostalRegister.append(self.Adr122)
            self.KostalRegister.append(self.Adr124)
            self.KostalRegister.append(self.Adr144)
            self.KostalRegister.append(self.Adr150)
            self.KostalRegister.append(self.Adr152)
            self.KostalRegister.append(self.Adr154)
            self.KostalRegister.append(self.Adr156)
            self.KostalRegister.append(self.Adr158)
            self.KostalRegister.append(self.Adr160)
            self.KostalRegister.append(self.Adr162)
            self.KostalRegister.append(self.Adr164)
            self.KostalRegister.append(self.Adr166)
            self.KostalRegister.append(self.Adr168)
            self.KostalRegister.append(self.Adr170)
            self.KostalRegister.append(self.Adr172)
            self.KostalRegister.append(self.Adr174)
            self.KostalRegister.append(self.Adr178)
            self.KostalRegister.append(self.Adr190)
            self.KostalRegister.append(self.Adr194)
            self.KostalRegister.append(self.Adr200)
            self.KostalRegister.append(self.Adr202)
            self.KostalRegister.append(self.Adr208)
            self.KostalRegister.append(self.Adr210)
            self.KostalRegister.append(self.Adr212)
            self.KostalRegister.append(self.Adr214)
            self.KostalRegister.append(self.Adr216)
            self.KostalRegister.append(self.Adr218)
            self.KostalRegister.append(self.Adr220)
            self.KostalRegister.append(self.Adr222)
            self.KostalRegister.append(self.Adr224)
            self.KostalRegister.append(self.Adr226)
            self.KostalRegister.append(self.Adr228)
            self.KostalRegister.append(self.Adr230)
            self.KostalRegister.append(self.Adr232)
            self.KostalRegister.append(self.Adr234)
            self.KostalRegister.append(self.Adr236)
            self.KostalRegister.append(self.Adr238)
            self.KostalRegister.append(self.Adr240)
            self.KostalRegister.append(self.Adr242)
            self.KostalRegister.append(self.Adr244)
            self.KostalRegister.append(self.Adr246)
            self.KostalRegister.append(self.Adr248)
            self.KostalRegister.append(self.Adr250)
            self.KostalRegister.append(self.Adr252)
            self.KostalRegister.append(self.Adr254)
            self.KostalRegister.append(self.Adr256)
            self.KostalRegister.append(self.Adr258)
            self.KostalRegister.append(self.Adr260)
            self.KostalRegister.append(self.Adr266)
            self.KostalRegister.append(self.Adr268)
            self.KostalRegister.append(self.Adr270)
            self.KostalRegister.append(self.Adr276)
            self.KostalRegister.append(self.Adr278)
            self.KostalRegister.append(self.Adr280)
            self.KostalRegister.append(self.Adr286)
            self.KostalRegister.append(self.Adr320)
            self.KostalRegister.append(self.Adr322)
            self.KostalRegister.append(self.Adr324)
            self.KostalRegister.append(self.Adr326)
            self.KostalRegister.append(self.Adr514)
            self.KostalRegister.append(self.Adr531)
            self.KostalRegister.append(self.Adr575)
            self.KostalRegister.append(self.Adr582)

            self.client.close()
            
            # smartmeter
            
            dbusservice['grid']['/Ac/Power'] =  self.Adr252[3]

            dbusservice['grid']['/Ac/L1/Current'] = self.Adr222[3]
            dbusservice['grid']['/Ac/L2/Current'] = self.Adr232[3]
            dbusservice['grid']['/Ac/L3/Current'] = self.Adr242[3]
            
            dbusservice['grid']['/Ac/L1/Voltage'] = self.Adr230[3]
            dbusservice['grid']['/Ac/L2/Voltage'] = self.Adr240[3]
            dbusservice['grid']['/Ac/L3/Voltage'] = self.Adr250[3]
            
            dbusservice['grid']['/Ac/L1/Power'] = self.Adr224[3]
            dbusservice['grid']['/Ac/L2/Power'] = self.Adr234[3]
            dbusservice['grid']['/Ac/L3/Power'] = self.Adr244[3]
            
            dbusservice['grid']['/Ac/Energy/Forward'] = self.Adr112[3] 
            
            #pv inverter          
            
            dbusservice['pvinverter.pv0']['/Ac/L1/Current'] = self.Adr154[3]
            dbusservice['pvinverter.pv0']['/Ac/L2/Current'] = self.Adr160[3]
            dbusservice['pvinverter.pv0']['/Ac/L3/Current'] = self.Adr166[3]
            
            dbusservice['pvinverter.pv0']['/Ac/L1/Voltage'] = self.Adr158[3]
            dbusservice['pvinverter.pv0']['/Ac/L2/Voltage'] = self.Adr164[3]
            dbusservice['pvinverter.pv0']['/Ac/L3/Voltage'] = self.Adr170[3]
            
            dbusservice['pvinverter.pv0']['/Ac/L1/Power'] = self.Adr156[3]
            dbusservice['pvinverter.pv0']['/Ac/L2/Power'] = self.Adr162[3]
            dbusservice['pvinverter.pv0']['/Ac/L3/Power'] = self.Adr168[3]
            
            
            dbusservice['pvinverter.pv0']['/Ac/Energy/Forward'] = self.Adr320[3]
            
            dbusservice['pvinverter.pv0']['/Ac/Power'] = self.Adr172[3]
           
    except Exception as ex:
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXX- Hit the following error :From subroutine kostal_modbusquery :", ex)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
# -----------------------------


# Here is the bit you need to create multiple new services - try as much as possible timplement the Victron Dbus API requirements.


def new_service(base, type, physical, id, instance):
    self = VeDbusService("{}.{}.{}_id{:02d}".format(
        base, type, physical,  id), dbusconnection())

    # Create the management objects, as specified in the ccgx dbus-api document
    self.add_path('/Mgmt/ProcessName', __file__)
    self.add_path('/Mgmt/ProcessVersion',
                  'Unkown version, and running on Python ' + platform.python_version())
    self.add_path('/Connected', 1)
    self.add_path('/HardwareVersion', 0)

    def _kwh(p, v): return (str(v) + 'kWh')
    def _a(p, v): return (str(v) + 'A')
    def _w(p, v): return (str(v) + 'W')
    def _v(p, v): return (str(v) + 'V')
    def _c(p, v): return (str(v) + 'C')

 # Create device type specific objects
    if physical == 'grid':
        self.add_path('/DeviceInstance', instance)
        self.add_path('/Serial', "12345678")
        # value used in ac_sensor_bridge.cpp of dbus-cgwacs
        self.add_path('/ProductId', 45069)
        self.add_path(
            '/ProductName', "SmartMeter")
        self.add_path('/Ac/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L1/Voltage', None, gettextcallback=_v)
        self.add_path('/Ac/L2/Voltage', None, gettextcallback=_v)
        self.add_path('/Ac/L3/Voltage', None, gettextcallback=_v)
        self.add_path('/Ac/L1/Current', None, gettextcallback=_a)
        self.add_path('/Ac/L2/Current', None, gettextcallback=_a)
        self.add_path('/Ac/L3/Current', None, gettextcallback=_a)
        self.add_path('/Ac/L1/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L2/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L3/Power', None, gettextcallback=_w)
        # energy bought from the grid
        self.add_path('/Ac/Energy/Forward', None, gettextcallback=_kwh)

    if physical == 'pvinverter':
        self.add_path('/DeviceInstance', instance)
        self.add_path('/FirmwareVersion', "1234")
        # value used in ac_sensor_bridge.cpp of dbus-cgwacs
        self.add_path('/ProductId', 41284)
        self.add_path(
            '/ProductName', "Kostal")
        self.add_path('/Ac/Energy/Forward', None, gettextcallback=_kwh)
        self.add_path('/Ac/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L1/Current', None, gettextcallback=_a)
        self.add_path('/Ac/L2/Current', None, gettextcallback=_a)
        self.add_path('/Ac/L3/Current', None, gettextcallback=_a)
        self.add_path('/Ac/L1/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L2/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L3/Power', None, gettextcallback=_w)
        self.add_path('/Ac/L1/Voltage', None, gettextcallback=_v)
        self.add_path('/Ac/L2/Voltage', None, gettextcallback=_v)
        self.add_path('/Ac/L3/Voltage', None, gettextcallback=_v)
        self.add_path('/Ac/MaxPower', None, gettextcallback=_w)
        self.add_path('/ErrorCode', None)
        self.add_path('/Position', 0)
        self.add_path('/StatusCode', None)

    return self


def _update():
    try:
        Kostalvalues = []
        Kostalquery = kostal_modbusquery()
        Kostalquery.run()
    except Exception as ex:
        print("Issues querying Kostal Plenticore -ERROR :", ex)

    return True


dbusservice = {}  # Dictonary to hold the multiple services

base = 'com.victronenergy'

# service defined by (base*, type*, id*, instance):
# * items are include in service name
# Create all the dbus-services we want
dbusservice['grid'] = new_service(
    base, 'grid',           'grid',              0, 31)
dbusservice['pvinverter.pv0'] = new_service(
    base, 'pvinverter.pv0', 'pvinverter',        0, 20)

# Everything done so just set a time to run an update function to update the data values every 1 second
gobject.timeout_add(1000, _update)


print("Connected to dbus, and switching over to gobject.MainLoop() (= event based)")
mainloop = gobject.MainLoop()
mainloop.run()

if __name__ == "__main__":
    try:

        Kostalquery = kostal_modbusquery()
        Kostalquery.run()
    except Exception as ex:
        print("Issues querying Kostal Plenticore -ERROR :", ex)
