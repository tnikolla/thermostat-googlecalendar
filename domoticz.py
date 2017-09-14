#!/usr/bin/python
import sys
import json
import urllib2
import re
import time
import datetime
import httplib, urllib


class Domoticz():

    def __init__(self, url):

        self.baseurl = url

    def __execute__(self, url):

        req = urllib2.Request(url)
        return urllib2.urlopen(req, timeout=5)

    def set_device_on(self, xid):
        """
        Get the Domoticz device information.
        """
        url = "%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On" % (self.baseurl, xid)
        data = json.load(self.__execute__(url))
        return data

    def set_device_off(self, xid):
        """
        Get the Domoticz device information.
        """
        url = "%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off" % (self.baseurl, xid)
        data = json.load(self.__execute__(url))
        return data

    def set_thermostat_value(self, xid, value):
        """
        Update Setpoint for Thermostat
        """
        url = "%s/json.htm?type=command&param=udevice&idx=%s&svalue=%s" % (self.baseurl, xid, value)
        data = json.load(self.__execute__(url))
        return data['status']

    def get_thermostat_value(self, xid):
        """
        Get current Thermostat Value
        """
        url = "%s/json.htm?type=devices&rid=%s" % (self.baseurl, xid)
        data = json.load(self.__execute__(url))
        return data['result'][0]['SetPoint']

