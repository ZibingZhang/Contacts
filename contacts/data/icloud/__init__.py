from data.icloud import manager, model

ALERT_UUIDS = [
    "4B949DAF-F587-47DF-95C2-857B85800ADC",
    "0A4DED51-0751-4B30-AD58-27E8556D5D91",
]
TEST_CONTACT_UUIDS = [
    "129C6305-F868-4711-B139-C209B4AF3852",
    "50786E4F-651F-4393-8F9C-060C40A22BB5",
    "623AE0B7-EB13-47BB-8CCF-09F2EAE2E4A3",
]
OTHER_UUIDS = [
    "FAB3DDA6-7529-4D3C-8714-35EF820DCCA8",  # italkbb
]
IGNORED_UUIDS = ALERT_UUIDS + TEST_CONTACT_UUIDS + OTHER_UUIDS

ICloudContactManager = manager.ICloudContactManager
ICloudManager = manager.ICloudManager
ICloudSession = manager.ICloudSession

ICloudContact = model.ICloudContact
ICloudGroup = model.ICloudGroup
