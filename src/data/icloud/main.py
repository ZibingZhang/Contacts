if __name__ == "__main__":
    from data.icloud.manager.session import ICloudSessionManager

    session_manager = ICloudSessionManager("username", "password")
    session_manager.login()

    contacts_manager = session_manager.contacts_manager

    contacts_and_groups = contacts_manager.get_contacts_and_groups()
    print(contacts_and_groups)

    with open("temp.json", "w+") as f:
        import json
        f.write(json.dumps(contacts_and_groups, indent=2))
