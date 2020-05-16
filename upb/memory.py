from enum import Enum

class UPBManufacturerID(Enum):
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

class SAProductID(Enum):
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
