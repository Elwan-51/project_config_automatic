from CreateConfig import CreateConfig

def main():
    path = "config_file.yml"
    config = CreateConfig(path)
    config.create_config_file("./config.txt")
if __name__ == '__main__':
    main()
