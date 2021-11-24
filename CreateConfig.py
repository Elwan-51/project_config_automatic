import yaml


class CreateConfig:
    def __init__(self, path):
        data = self.get_config(path)
        try:
            if data['General']:
                self.general = data['General']
        except:
            print("No general data")
        try:
            if data['Interface']:
                self.interface = data['Interface']
        except:
            print("No interface data")
        try:
            if data['Vrf']:
                self.vrf = data['Vrf']
        except:
            print('No vrf data')
        try:
            if data['Bgp']:
                self.bgp = data['Bgp']
        except:
            print('No bgp data')
        try:
            if data['Dhcp']:
                self.dhcp = data['Dhcp']
        except:
            print('No dhcp data')
        try:
            if data['Vlan']:
                self.vlan = data['Vlan']
        except:
            print('No vlan data')
        try:
            if data['Ospf']:
                self.ospf = data['Ospf']
        except:
            print("No ospf data")

    def get_new_config_file(self, path):
        self.__init__(path)

    # INTERFACE SECTION

    def create_interface(self):
        """That function is used to create the diverse interface and subinterface we want:
        function used : - self.interface(dic)
                       - self.sub_interface(dic)"""

        interface_str = f"!interfaces\n\n"
        for inter in self.interface:
            interface_str += f"{self.set_interface(inter)}"
            try:
                if inter['subInterface']:
                    interface_str += f"{self.set_sub_interface(inter)}"
            except:
                pass

        return interface_str

    def set_interface(self, inter):
        """interface will generate the configuration for an interface.
        function used : - interface_config(dic)"""
        interface_str = ""
        if inter['type'] == "ethernet":
            interface_str += f"int e{inter['interfaceID']}\n"
        elif inter['type'] == "loopback":
            interface_str += f"int lo{inter['interfaceID']}\n"
        elif inter['type'] == "fast_ethernet":
            interface_str += f"int fa{inter['interfaceID']}\n"
        elif inter['type'] == "giga_ethernet":
            interface_str += f"int g{inter['interfaceID']}\n"
        elif inter['type'] == "vlan":
            interface_str += f"int vlan {inter['vlan']}\n"
        interface_str += f"{self.set_interface_config(inter)}"
        return interface_str

    def set_sub_interface(self, inter):
        """interface will generate all the configuration for the subinterface of an interface.
                function used : - interface_config(dic)
                it return all the sub_interface"""

        interface_str = ""
        for sub_int in inter['subInterface']:
            if inter['type'] == "ethernet":
                interface_str += f"int e{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            elif inter['type'] == "loopback":
                interface_str += f"int lo{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            elif inter['type'] == "fast_ethernet":
                interface_str += f"int fa{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            elif inter['type'] == "giga_ethernet":
                interface_str += f"int g{inter['interfaceID']}.{sub_int['subInterfaceID']}\n"
            interface_str += f"{self.set_interface_config(sub_int)}"

        return interface_str

    def set_interface_config(self, inter):
        """function who will generate the diverse section of the interface configuration files"""
        interface_str = f"description {inter['description']}\n"
        try:
            if inter['mode'] == "acces":
                interface_str += f"switchport mode acces vlan {inter['vlan']}\n"
            elif inter['mode'] == "trunk":
                interface_str += f"switchport trunk encapsulation {inter['encapsulation']} {inter['vlan']}\n" \
                                 f"switchport mode trunk\n"
        except:
            pass
        try:

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
                                interface_str += f"ipv6 address fe80::{inter['interfaceAddress']['ipv6']['link_local']} link-local\n"
                            elif line == "address":
                                for addr in inter['interfaceAddress']['ipv6']['address']:
                                    if addr['type'] == "eui-64":
                                        interface_str += f"ipv6 address {addr['ip']} eui-64\n"
                                    else:
                                        interface_str += f"ipv6 address {addr['ip']}\n"
                except:
                    pass
        except:
            pass

            try:
                if inter['vrf']:
                    interface_str += f"vrf forwarding {inter['vrf'].upper()}\n"
            except:
                pass

        interface_str += "no shut\n\n\n"
        return interface_str

    # VRF SECTION

    def set_vrf_def(self):
        """function that create all the vrf definition for all the vrf"""
        vrf_def = f"!vrf definition\n"
        for vrf in self.vrf:
            vrf_def += f"vrf definition {vrf['vrf'].upper()}\n" \
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

    # BGP SECTION

    def set_bgp_router(self):
        bgp_router_str = ""
        for bgp in self.bgp:
            bgp_router_str += f"!{bgp['bgpType']}\n"
            try:
                if bgp['asn']:
                    bgp_router_str += f"router bgp {bgp['asn']['id']}\n"
            except:
                pass

            bgp_router_str += f"{self.set_peer_session_template(bgp)}\n"
            try:
                if bgp['neighbor']:
                    for neighbor in bgp['neighbor']:
                        bgp_router_str += f"neighbor {neighbor} inherit peer-session {bgp['bgpType'].upper()}-{bgp['asn']['id'].upper()}\n"
            except:
                pass
            bgp_router_str += f"\n{self.set_vpn(bgp)}\n"
            bgp_router_str += f"{self.set_vrf_bgp(bgp)}\n"
            bgp_router_str += "\n"
        return bgp_router_str

    def set_peer_session_template(self, bgp):
        peer_session = ""
        try:
            if bgp['peer_session_template']:
                peer_session += f"template peer-session {bgp['bgpType'].upper()}-{bgp['asn']['id'].upper()}\n"
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

        return peer_session

    def set_vpn(self, vpn_list):
        vpn_str = ""
        try:
            vpns = vpn_list['vpn']
            for vpn in vpns:
                vpn_str += f"address-family {vpn['type']}\n"
                for client in vpn['client']:
                    vpn_str += f"!vpn for {client['name'].upper()}\n" \
                               f"neighbor {client['ip']} activate\n" \
                               f"neighbor {client['ip']} send-community both\n"
                vpn_str += "exit-address-family\n\n"
        except:
            pass
        return vpn_str

    def set_vrf_bgp(self, bgp):
        vrf_list = ""
        try:
            if bgp['vrf']:
                vrf_list = f"!vrf list\n"
                for vrf in bgp['vrf']:
                    vrf_list += f"address-family {vrf['ipType']} vrf {vrf['name'].upper()}\n"
                    for connection in vrf['connection']:
                        vrf_list += f"redistribute {connection}\n"
                    vrf_list += f"exit-address-family\n"
        except:
            pass
        return vrf_list

    # VLAN SECTION

    def set_vlan(self):
        vlan_str = ""
        try:
            if self.vlan:
                vlan_str = "!vlan\n"
                for vlan in self.vlan:
                    print(vlan)
                    vlan_str += f"vlan {vlan['id']}\n" \
                                f"name {vlan['name']}\n\n"
        except:
            pass
        return vlan_str

    # CONFIG FILE SECTION

    def get_config(self, path):
        with open(path, 'r') as files:
            try:
                parsed_yaml = yaml.safe_load(files)
                return parsed_yaml
            except yaml.YAMLError as exc:
                print(exc)
