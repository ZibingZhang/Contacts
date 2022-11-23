if __name__ == "__main__":
    import configparser
    import dataclasses
    import json

    from data.icloud.manager import ICloudContactManager, ICloudSessionManager

    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["login"]["username"]
    password = config["login"]["password"]

    session_manager = ICloudSessionManager(username, password)
    session_manager.login()
    contacts_manager = ICloudContactManager(session_manager)

    contacts, groups = contacts_manager.get_contacts_and_groups()

    with open("contacts.json", "w") as f:
        for contact in contacts:
            f.write(f"{json.dumps(dataclasses.asdict(contact))}\n")

    with open("groups.json", "w") as f:
        for group in groups:
            f.write(f"{json.dumps(dataclasses.asdict(group))}\n")
