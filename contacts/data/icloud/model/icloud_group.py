"""A dataclass representation of the json object response for an iCloud group."""
import dataclasses
import uuid

from utils import dataclasses_utils


@dataclasses.dataclass
class HeaderPositions(dataclasses_utils.DataClassJsonMixin):
    A: int | None = None
    B: int | None = None
    C: int | None = None
    D: int | None = None
    E: int | None = None
    F: int | None = None
    G: int | None = None
    H: int | None = None
    I: int | None = None
    J: int | None = None
    K: int | None = None
    L: int | None = None
    M: int | None = None
    N: int | None = None
    O: int | None = None
    P: int | None = None
    Q: int | None = None
    R: int | None = None
    S: int | None = None
    T: int | None = None
    U: int | None = None
    V: int | None = None
    W: int | None = None
    X: int | None = None
    Y: int | None = None
    Z: int | None = None


@dataclasses.dataclass
class ICloudGroup(dataclasses_utils.DataClassJsonMixin):
    contactIds: list[uuid.UUID]
    etag: str
    groupId: uuid.UUID
    headerPositions: HeaderPositions
    isGuardianApproved: bool
    name: str
    whitelisted: bool
