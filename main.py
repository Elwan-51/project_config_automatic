from CreateConfig import CreateConfig

def main():
    config = CreateConfig(input("Path for your configuration file : \n"))
    try:
        config.create_config_file(input("Path for the generate configuration file : \n"))
        print("File created")
    except:
        print("Error with the file creation")


if __name__ == '__main__':
    main()
