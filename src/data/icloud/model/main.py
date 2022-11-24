if __name__ == "__main__":
    from data.icloud import ICloudContact

    with open("../contacts.json") as f:
        contacts = f.read().strip().split("\n")
    for contact in contacts:
        ct = ICloudContact.from_json(contact)
        if ct.birthday:
            print(ct.firstName, ct.birthday)
