if __name__ == "__main__":
    import configparser

    from data.icloud.manager.session import ICloudSessionManager

    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["login"]["username"]
    password = config["login"]["password"]

    session_manager = ICloudSessionManager(username, password)
    session_manager.login()

    contacts_manager = session_manager.contacts_manager

    contacts_and_groups = contacts_manager.get_contacts_and_groups()
    print(contacts_and_groups)

    with open("contacts_and_groups.json", "w+") as f:
        import json
        f.write(json.dumps(contacts_and_groups, indent=2))
