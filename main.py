from enum import Enum
import yaml


class connection_Type(Enum):

    CONNECTED = "connected"
    STATIC = "static"
    BGP = "bgp"
    RIP = "rip"


class interface_Type(Enum):

    ETHERNET = "e"
    FAST_ETHERNET = "fa"
    GIGA_ETHERNET = "g"
    LOOPBACK = "lo"

class ipv6_Type(Enum):

    LINK_LOCAL = "link_local"
    EUI_64 = "eui-64"


class vrf_Type(Enum):

    GLOBAL = 'global'
    PRIVATE = 'private'


class CreateConfigPE:
    asnID: int
    loopback0: str
    hostname: str


class CreateConfig:
    def create_interface(self, **kwargs):
        """That function is used to create the differente interface and subinterface we want:
        funcion used : - self.inteface(dic)
                       - self.sub_interface(dic)"""
        interface = kwargs['interface']
        interface_str = f"!interfaces\n\n"
        for inter in interface:
            interface_str += f"{self.interface(inter)}"
            try:
                if inter['subInterface']:
                    interface_str += f"{self.sub_interface(inter)}"
            except:
                pass

        return interface_str

    def interface(self, inter):
        """interface will generate the configuration for an interface.
        function used : - interface_config(dic)"""
        interface_str = ""
        if inter['type'] == "ethernet":
            interface_str += f"int {interface_Type.ETHERNET.value}{inter['interfaceID']}\n"
        elif inter['type'] == "loopback":
            interface_str += f"int {interface_Type.LOOPBACK.value}{inter['interfaceID']}\n"
        elif inter['type'] == "fast_ethernet":
            interface_str += f"int {interface_Type.FAST_ETHERNET.value}{inter['interfaceID']}\n"
        elif inter['type'] == "giga_ethernet":
            interface_str += f"int {interface_Type.GIGA_ETHERNET.value}{inter['interfaceID']}\n"
        interface_str += f"{self.interface_config(inter)}"
        return interface_str

    def sub_interface(self, inter):
        """interface will generate all the configuration for the subinterface of an interface.
                function used : - interface_config(dic)
                it return all the sub_interface"""

        interface_str = ""
        for sub_int in inter['subInterface']:
            if inter['type'] == "ethernet":
                interface_str += f"int {interface_Type.ETHERNET.value}{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            elif inter['type'] == "loopback":
                interface_str += f"int {interface_Type.LOOPBACK.value}{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            elif inter['type'] == "fast_ethernet":
                interface_str += f"int {interface_Type.FAST_ETHERNET.value}{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            elif inter['type'] == "giga_ethernet":
                interface_str += f"int {interface_Type.GIGA_ETHERNET.value}{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            interface_str += f"{self.interface_config(sub_int)}"
        return interface_str

    def interface_config(self, inter):
        """function who will generate the differente section of the interface configuration files"""
        interface_str = f"description {inter['description']}\n"
        try:
            if inter['mode'] == "acces":
                interface_str += f"switchport mode acces vlan {inter['vlan']}\n"
            elif inter['mode'] == "trunk":
                interface_str += f"switchport trunk encapsulation {inter['encapsulation']} {inter['vlan']}\n" \
                                 f"switchport mode trunk\n"
        except:
            pass
        if inter['interfaceAddress']:
            try:
                if inter['interfaceAddress']['ipv4'] == "dhcp":
                    interface_str += f"ip address dhcp\n"
                else:
                    interface_str += f"ip address {inter['interfaceAddress']['ipv4']['ip']} {inter['interfaceAddress']['ipv4']['mask']}\n"
            except:
                pass
            try:
                if inter['interfaceAddress']['ipv6']:
                    for line in inter['interfaceAddress']['ipv6']:

                        if line == "link_local":
                            interface_str += f"ipv6 address fe80::{inter['interfaceAddress']['ipv6']['link_local']} linklocal\n"
                        elif line == "address":
                            for addr in inter['interfaceAddress']['ipv6']['address']:
                                if addr['type'] == "eui-64":
                                    interface_str += f"ipv6 address {addr['ip']} eui-64\n"
                                else:
                                    interface_str += f"ipv6 address {addr['ip']}\n"
            except:
                pass

            try:
                if inter['vrf']:
                    interface_str += f"vrf forwarding {inter['vrf']}\n"
            except:
                pass

        interface_str += "\n\n"
        return interface_str

    def vrf_def(self, **kwargs):
        """fucntion that create all the vrf definition for all the vrf"""
        vrf_def = f"!VRF DEFINITON\n"
        for vrf in kwargs['Vrf']:
            vrf_def += f"vrf definion {vrf['vrf']}\n" \
                       f"rd {vrf['rd']}\n"
            if vrf['import']:
                for import_ in vrf['import']['id']:
                    vrf_def += f'route-target import {import_}\n'
            if vrf['export']:
                for export in vrf['export']['id']:
                    vrf_def += f'route-target export {export}\n'
            vrf_def += f"address-family-ipv4\n" \
                       f"address-family-ipv6\n\n"

        return vrf_def

    def bgp_router(self, **kwargs):
        bgp_router_str = ""
        for bgp in kwargs['Bgp']:
            bgp_router_str += f"!{bgp['bgpType']}\n"
            try :
                if bgp['asn']:
                    bgp_router_str += f"router bgp {bgp['asn']['id']}\n"
            except:
                pass

            bgp_router_str += f"{self.peer_session_template(bgp)}"

        return bgp_router_str

    def peer_session_template(self,bgp):
        peer_session = ""
        try:
            if bgp['peer_session_template']:
                peer_session += f"template peer-session {bgp['bgpType']}-{bgp['asn']['id']}\n"
                try:
                    if bgp['peer_session_template']['remote-as']:
                        peer_session += f"remote-as {bgp['peer_session_template']['remote-as']}\n"
                except:
                    pass
                try:
                    if bgp['peer_session_template']['update-source']:
                        peer_session += f"update-source {bgp['peer_session_template']['update-source']}\n"
                except:
                    pass
                peer_session += "exit-peer-session\n"
        except:
            pass
        peer_session += "\n\n"

        return peer_session


def get_config(path):
    with open(path, 'r') as files:
        try:
            parsed_yaml = yaml.safe_load(files)
            return parsed_yaml
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == '__main__':
    path = "Fichier-config.yml"
    config = CreateConfig()
    #print(config.create_interface(**get_config(path)))
    print(config.bgp_router(**get_config(path)))
