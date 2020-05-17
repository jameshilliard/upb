from enum import IntFlag, unique

@unique
class UPBManufacturerID(IntFlag):
    OEM = 0
    PCS = 1
    MDManufacturing = 2
    WebMountainTech = 3
    SimplyAutomated = 4
    HAI = 5
    RCS = 10
    OEM90 = 90
    OEM91 = 91
    OEM92 = 92
    OEM93 = 93
    OEM94 = 94
    OEM95 = 95
    OEM96 = 96
    OEM97 = 97
    OEM98 = 98
    OEM99 = 99

@unique
class PCSProductID(IntFlag):
    PCS_WS1  = 1 # Wall Switch - 1 Channel - Dimmer
    PCS_WS1R = 2 # Wall Switch - 1 Channel - Relay
    PCS_WMC6 = 3 # Wall Mount Controller - 6 Button
    PCS_WMC8 = 4 # Wall Mount Controller - 8 Button
    PCS_OCM1 = 5 # Output Control Module - 1 Channel
    PCS_OCM2 = 6 # Output Control Module - 2 Channel
    PCS_UNUSED_7 = 7 # Load Control Module - 1 Channel
    PCS_LCM2 = 8 # Load Control Module - 2 Channel
    PCS_LM1  = 9 # Lamp Module - 1 Channel
    PCS_LM2  = 10 # Lamp Module - 2 Channel
    PCS_ICM2 = 11 # Input Control Module - 2 Channel
    PCS_DTC6 = 13 # Desktop Controller - 6 Button
    PCS_DTC8 = 14 # Desktop Controller - 8 Button
    PCS_AM1  = 15 # Appliance Module - 1 Channel

    PCS_UNUSED_16 = 16 # Commercial Lighting Controller
    PCS_UNUSED_17  = 17 # Commercial Fixture Controller
    PCS_PRS  = 18 # Phase Repeater Slave
    PCS_PRM  = 19 # Phase Repeater Master
    PCS_MSC  = 20 # Motion Sensor Controller
    PCS_HFC  = 21 # HID Fixture Controller
    PCS_RRM  = 22 # Router Repeater Master Chip
    PCS_RRS  = 23 # Router Repeater Slave  Chip
    PCS_WS1E = 24 # Wall Switch - Electronic Low Voltage
    PCS_UNUSED_25 = 25 # Load sheding module
    PCS_TEC  = 26 # Time Clock
    PCS_API  = 29 # Alarm Panel Interface
    PCS_XPW  = 30 # X10 to UPB Converter

    PCS_DSM  = 36 # Doorbell Sense Module
    PCS_TSM  = 37 # Telephone Sense Module

    PCS_SPR  = 40 # Split phase repeater
    PCS_TPR  = 41 # 3-phase repeater

    PCS_PIME  = 45 # Powerline Interface Module
    PCS_PIMA  = 46 # Powerline Interface Module
    PCS_PIP   = 47 # Powerline Interface Module
    PCS_PIM   = 48 # Powerline Interface Module
    PCS_DIAG1 = 49 # Diagnostics 1
    PCS_DIAG2 = 50 # Diagnostics 2
    PCS_DIAG3 = 51 # Diagnostics 3
    PCS_DIAG4 = 52 # Diagnostics 4
    PCS_TX4   = 53 # Test Transmitter 4
    PCS_TM4   = 54 # Test Module 4
    PCS_UTM   = 55 # UPB Test Module
    PCS_ATM   = 56 # UPB Alpha Test Module
    PCS_RM1   = 58 # Receptacle Module

    PCS_FDM2  = 60 # Fixture Dimmer Module
    PCS_FRM   = 61 # Inline Fixture Relay Module
    PCS_WS2   = 62 # Wall Switch - 1 Channel - Dimmer
    PCS_KPLD6 = 63 # Keypad Light Dimmer

    PCS_SCM   = 64 # Shade control module

    PCS_KPC6  = 65 # 6-key keypad
    PCS_KPC8  = 66 # 8-key keypad
    PCS_RFI   = 67 # RFI Interface
    PCS_WS1X  = 68 # Wall switch

    PCS_KPLD8 = 69 # Keypad Light Dimmer
    PCS_KPLR6 = 70 # Keypad Load Relay
    PCS_KPLR8 = 71 # Keypad Load Relay

    PCS_WS1L  = 72 # WS1L Wall Switch LED/CFL Dimmer
    PCS_KPC7  = 73 # KPC7 Controller - 7 Button
    PCS_KPR7  = 74 # KPR7 Controller Load Relay - 7 Button
    PCS_KPD7  = 75 # KPD7 Controller Load Dimmer - 7 Button

@unique
class MDProductID(IntFlag):
    MD_UNUSED_32  = 32 # Vacuum Handle Controller
    MD_UNUSED_33  = 33 # Vacuum Power Module
    MD_UNUSED_35  = 35 # Vacuum Input Module
    MD_DSM  = 36 # Doorbell Sense Module
    MD_TSM  = 37 # Telephone Sense Module

@unique
class HAIProductID(IntFlag):
    HAI_WS1  = 1 # Wall Switch - 1 Channel - 600W
    HAI_WS2  = 2 # Wall Switch - 1 Channel - 1000W
    HAI_WS9  = 6
    HAI_WS3  = 16 # Wall Switch - 1 Channel - 600W
    HAI_WS4  = 17 # Wall Switch - 1 Channel - 1000W
    HAI_WS5  = 18 # Wall Switch - 1 Channel - Non-Dim

    HAI_WS6  = 3 # Wall Switch - 1 Channel - 1000W
    HAI_WS7  = 4 # Wall Switch - 1 Channel - 1500W
    HAI_WS8  = 5 # Wall Switch - 1 Channel - 2400W

    HAI_LM1  = 32 # Lamp Module
    HAI_AM1  = 48 # Appliance Module

    HAI_PIM  = 64 # Powerline Interface Module
    HAI_SPR  = 65
    HAI_TPR  = 66

    HAI_WMC6 = 80 # Wall Mount Controller - 6 Button
    HAI_HLCK6 = 81 # Wall Mount Controller - 6 button new model
    HAI_WMC8 = 96 # Wall Mount Controller - 8 Button

@unique
class WMTProductID(IntFlag):
    WMT_Dimmer    = 1 # Dimmer Module
    WMT_Relay     = 5 # Relay Module
    WMT_FxtRelay  = 7 # Fixture Relay
    WMT_ConOutlet = 8 # Controlled Outlet

    WMT_RelayT    = 9 # Relay Module w/timer

    WMT_WIDimmer  = 10 # Wired-in dimmer module

    WMT_DimmerT   = 12 # Dimmer Module w/timer
    WMT_FxtRelayT = 13 # Fixture Relay w/timer
    WMT_WIDimmerT = 14 # Wired-in dimmer module w/timer

    WMT_MultiBtn  = 15 # Multi-Button Controller

    WMT_USM1      = 20 # Motorized Drapery Control USM1

    WMT_MultiSw   = 22 # Multi-Switch
    WMT_Quad      = 26 # Quad Output Module
    WMT_US4       = 27 # US4
    WMT_US1_40    = 28 # US1-40
    WMT_US2_40    = 29 # US2-40

    WMT_SerXfc    = 30 # Serial PIM
    WMT_USBXfc    = 31 # USB PIM
    WMT_EthXfc    = 32 # Ethernet PIM
    WMT_Test      = 33 # Signal Quality Monitoring Unit

    WMT_US1_40T   = 34 # US1-40 w/timer

    WMT_ESI       = 35 # ESI
    WMT_UCQTX     = 36 # UCQ TX only
    WMT_InOut     = 40 # Input / Output module

    WMT_RUC       = 41 # Remote PIM

    WMT_USM1R     = 44 # Motorized Drapery Control USM1
    WMT_USM2R     = 45 # Motorized Drapery Control USM1

    WMT_US22_40   = 62 # US22-40

    WMT_WS1       = 88 # Relabled PCS switch
    WMT_WMC6      = 89 # Relabled PCS WMC6

@unique
class SAProductID(IntFlag):
    SA_Dimmer    = 1 # Dimmer Module
    SA_Relay     = 5 # Relay Module
    SA_FxtRelay  = 7 # Fixture Relay

    SA_RelayT    = 9 # Relay Module w/timer
    SA_WIDimmer  = 10 # Wired-in dimmer module

    SA_DimmerT   = 12 # Dimmer Module w/timer
    SA_FxtRelayT = 13 # Fixture Relay w/timer
    SA_WIDimmerT = 14 # Wired-in dimmer module w/timer

    SA_MultiBtn  = 15 # Multi-Button Controller

    SA_USM1      = 20 # Motorized Drapery Control USM1

    SA_MultiSw   = 22 # Multi-Switch
    SA_Quad      = 26 # Quad Output Module
    SA_US4       = 27 # US4
    SA_US1_40    = 28 # US1-40
    SA_US2_40    = 29 # US2-40

    SA_SerXfc    = 30 # Serial PIM
    SA_USBXfc    = 31 # USB PIM
    SA_EthXfc    = 32 # Ethernet PIM
    SA_Test      = 33 # Signal Quality Monitoring Unit

    SA_US1_40T   = 34 # US1-40 w/timer

    SA_UCQTX     = 36 # UCQ TX only

    SA_InOut     = 40 # Input / Output module
    SA_Input     = 41 # Input Module
    SA_Sprinkler = 43 # Sprinkler Controller

    SA_USM1R     = 44 # Motorized Drapery Control USM1
    SA_USM2R     = 45 # Motorized Drapery Control USM2

    SA_UCQ       = 50
    SA_UCQ_40    = 51
    SA_UCQ_F     = 52

    SA_US22_40   = 62 # US22-40

    SA_XDimmer   = 201 # Dimmer Module
    SA_XRelay    = 205 # Relay Module
    SA_XMultiSw  = 222 # Multi-Switch
    SA_XInOut    = 240 # Input / Output module

@unique
class OEMProductID(IntFlag):
    OEM_Dimmer    = 1 # Dimmer Module
    OEM_Relay     = 5 # Relay Module
    OEM_FxtRelay  = 7 # Fixture Relay

    OEM_RelayT    = 9 # Relay Module w/timer
    OEM_WIDimmer  = 10 # Wired-in dimmer module

    OEM_DimmerT   = 12 # Dimmer Module w/timer
    OEM_FxtRelayT = 13 # Fixture Relay w/timer
    OEM_WIDimmerT = 14 # Wired-in dimmer module w/timer

    OEM_MultiBtn  = 15 # Multi-Button Controller

    OEM_USM1      = 20 # Motorized Drapery Control USM1

    OEM_MultiSw   = 22 # Multi-Switch
    OEM_Quad      = 26 # Quad Output Module
    OEM_US4       = 27 # US4
    OEM_US1_40    = 28 # US1-40
    OEM_US2_40    = 29 # US2-40

    OEM_SerXfc    = 30 # Serial PIM
    OEM_USBXfc    = 31 # USB PIM
    OEM_EthXfc    = 32 # Ethernet PIM
    OEM_Test      = 33 # Signal Quality Monitoring Unit

    OEM_US1_40T   = 34 # US1-40 w/timer

    OEM_UCQTX     = 36 # UCQ TX only

    OEM_InOut     = 40 # Input / Output module

    OEM_USM1R     = 44 # Motorized Drapery Control USM1
    OEM_USM2R     = 45 # Motorized Drapery Control USM1

    OEM_US22_40   = 62 # US22-40

    OEM_XDimmer   = 201 # Dimmer Module
    OEM_XRelay    = 205 # Relay Module
    OEM_XMultiSw  = 222 # Multi-Switch
    OEM_XInOut    = 240 # Input / Output module

@unique
class OEM90ProductID(IntFlag):
    OEM90_Dimmer  = 201 # Dimmer Module
    OEM90_Relay   = 205 # Relay Module
    OEM90_MultiSw = 222 # Multi-Switch
    OEM90_InOut   = 240 # Input / Output module

@unique
class RCSProductID(IntFlag):
    RCS_TU16  = 10
    RCS_TU40  = 11
    RCS_TU50  = 12
    RCS_RelayUnit  = 20

UPBKindSwitch = {
    PCSProductID.PCS_WS1,
    PCSProductID.PCS_WS1R,
    PCSProductID.PCS_WS1E,
    PCSProductID.PCS_WS2,
    PCSProductID.PCS_WS1X,
    PCSProductID.PCS_WS1L,
    HAIProductID.HAI_WS1,
    HAIProductID.HAI_WS2,
    HAIProductID.HAI_WS3,
    HAIProductID.HAI_WS4,
    HAIProductID.HAI_WS5,
    HAIProductID.HAI_WS6,
    HAIProductID.HAI_WS7,
    HAIProductID.HAI_WS8,
    HAIProductID.HAI_WS9,
    WMTProductID.WMT_WS1
}

UPBKindModule1 = {
    PCSProductID.PCS_LM1,
    PCSProductID.PCS_AM1,
    PCSProductID.PCS_RM1,
    PCSProductID.PCS_FRM,
    HAIProductID.HAI_LM1,
    HAIProductID.HAI_AM1,
    WMTProductID.WMT_Dimmer,
    WMTProductID.WMT_Relay,
    WMTProductID.WMT_DimmerT,
    WMTProductID.WMT_RelayT,
    WMTProductID.WMT_FxtRelay,
    WMTProductID.WMT_ConOutlet,
    SAProductID.SA_Dimmer,
    SAProductID.SA_Relay,
    SAProductID.SA_DimmerT,
    SAProductID.SA_RelayT,
    SAProductID.SA_XDimmer,
    SAProductID.SA_XRelay,
    OEMProductID.OEM_Dimmer,
    OEMProductID.OEM_Relay,
    OEMProductID.OEM_DimmerT,
    OEMProductID.OEM_RelayT,
    OEMProductID.OEM_XDimmer,
    OEMProductID.OEM_XRelay,
    OEM90ProductID.OEM90_Dimmer,
    OEM90ProductID.OEM90_Relay
}

UPBKindModule2 = {
    PCSProductID.PCS_OCM2,
    PCSProductID.PCS_LM2,
    PCSProductID.PCS_FDM2
}

UPBKindKeypad = {
    PCSProductID.PCS_WMC6,
    PCSProductID.PCS_WMC8,
    PCSProductID.PCS_DTC6,
    PCSProductID.PCS_DTC8,
    PCSProductID.PCS_KPC6,
    PCSProductID.PCS_KPC7,
    PCSProductID.PCS_KPC8,
    HAIProductID.HAI_WMC6,
    HAIProductID.HAI_WMC8,
    WMTProductID.WMT_MultiBtn,
    WMTProductID.WMT_WMC6,
    SAProductID.SA_MultiBtn,
    OEMProductID.OEM_MultiBtn
}

UPBKindKeypadDimmer = {
    PCSProductID.PCS_KPLD6,
    PCSProductID.PCS_KPD7,
    PCSProductID.PCS_KPLD8,
    PCSProductID.PCS_KPLR6,
    PCSProductID.PCS_KPR7,
    PCSProductID.PCS_KPLR8
}

UPBKindInput = {
    PCSProductID.PCS_ICM2,
    PCSProductID.PCS_DSM,
    PCSProductID.PCS_TSM,
    MDProductID.MD_DSM,
    MDProductID.MD_TSM
}

UPBKindUSQ = {
    WMTProductID.WMT_MultiSw,
    WMTProductID.WMT_US1_40,
    WMTProductID.WMT_US1_40T,
    SAProductID.SA_MultiSw,
    SAProductID.SA_US1_40,
    SAProductID.SA_US1_40T,
    SAProductID.SA_XMultiSw,
    OEMProductID.OEM_MultiSw,
    OEMProductID.OEM_US1_40,
    OEMProductID.OEM_US1_40T,
    OEMProductID.OEM_XMultiSw,
    OEM90ProductID.OEM90_MultiSw
}
