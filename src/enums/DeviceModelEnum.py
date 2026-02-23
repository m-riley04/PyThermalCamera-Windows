from enum import Enum
class DeviceModel(Enum):
    """
    Thermal camera device models with their specifications.
    Based on research from EEVBlog forum and manufacturer specs.
    """
    TC001 = "TC001" # Topdon TC001
    TS001 = "TS001" # Topdon TS001
    P2_PRO = "P2_PRO" # Infiray P2 Pro
