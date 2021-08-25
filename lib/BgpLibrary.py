import xml.etree.ElementTree as ET
import io
from SandboxLibrary import SandboxLibrary
import logging
from robot.api import logger

class BgpLibrary(object):
    def __init__(self):
        pass

    def _remove_xml_namespace(self,xml):
        for _, el in xml:
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        return xml.root

    def _trim_xml_only(self, bgp_reponse):
        result = bgp_reponse[bgp_reponse.find('<rpc-reply'):bgp_reponse.rfind('/rpc-reply>')+len('/rpc-reply>')]
        return result

    def test_message(self,message):
        return message

    def validate_bgp_groups(self, bgp_reponse, number):
        xml_string = self._trim_xml_only(bgp_reponse)
        bgp_info = ET.iterparse(io.StringIO(xml_string))
        bgp_info = self._remove_xml_namespace(bgp_info).find('bgp-information')
        if bgp_info is None:
            raise AssertionError("Could not find an active BGP")
        group_count = bgp_info.find('group-count').text
        if group_count != number:
            raise AssertionError("Expected {expected} neighbors but found: {found}"
                                 .format(expected=number, found=group_count))