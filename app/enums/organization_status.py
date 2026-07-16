from enum import Enum


class OrganizationStatus(str, Enum):
    active = "active"
    trial = "trial"
    inactive = "inactive"
    suspended = "suspended"
