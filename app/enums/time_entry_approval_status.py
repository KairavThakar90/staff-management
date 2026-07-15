from enum import Enum


class TimeEntryApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"