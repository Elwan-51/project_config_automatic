from CreateConfig import CreateConfig

def main():
    path = "config_file.yml"
    config = CreateConfig(path)
    print(config.create_interface())
    #print(config.set_bgp_router())
    print(config.set_vlan())
if __name__ == '__main__':
    main()
