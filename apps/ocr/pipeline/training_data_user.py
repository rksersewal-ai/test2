# =============================================================================
# EDMS OCR AGENT - USER'S CUSTOM TRAINING DATA (PART 1)
# Extended Locomotive / IGBT / Engine parameters from custom datasets
# Source: D:\LDO_ERP\Jan 2026\EDMS 2.0\EDMS OCR agent\OCR training dataset\
# =============================================================================

LOCOMOTIVE_SPECS_EXTENDED = {
    "WAG-9": {
        "axle_config": "Co-Co",
        "axle_load_tonnes": 22.5,
        "power_kw": 6120,
        "voltage": "25 kV AC",
        "traction_motors": 6,
        "motor_kw": 1020,
        "max_speed_kmph": 100,
        "length_m": 20.562,
        "weight_tonnes": 123,
        "tot_partner": "ABB / Adtranz",
    },
    "WAP-7": {
        "axle_config": "Co-Co",
        "axle_load_tonnes": 19.25,
        "power_kw": 5400,
        "voltage": "25 kV AC",
        "traction_motors": 6,
        "motor_kw": 900,
        "max_speed_kmph": 130,
        "length_m": 20.562,
        "weight_tonnes": 123,
        "regenerative_braking": True,
    },
    "WAP-5": {
        "axle_config": "Bo-Bo",
        "axle_load_tonnes": 18.5,
        "power_kw": 4480,
        "voltage": "25 kV AC",
        "traction_motors": 4,
        "motor_kw": 1120,
        "max_speed_kmph": 160,
        "length_m": 17.88,
        "weight_tonnes": 78,
        "tot_partner": "Adtranz / ABB Switzerland",
    },
    "WDG-6G": {
        "axle_config": "Co-Co",
        "axle_load_tonnes": 22.5,
        "power_kw": 4474,
        "engine_model": "GE 12-cylinder GEVO",
        "engine_displacement_L": 95.4,
        "fuel_tank_L": 6000,
        "turbocharger": "Single Stage",
        "max_speed_kmph": 120,
    },
}

ENGINE_PARAMETERS = {
    "RATED_POWER": {"unit": "kW", "condition": "Continuous Rating at Rated Speed"},
    "RATED_SPEED": {"unit": "RPM", "typical": "900-1050 rpm (diesel)"},
    "IDLE_SPEED": {"unit": "RPM", "typical": "400-450 rpm (diesel)"},
    "COMPRESSION_RATIO": {"typical": "14:1 to 16:1 (diesel)"},
    "FIRING_ORDER": {"note": "Specific to engine model"},
    "INJECTION_PRESSURE": {"unit": "bar", "typical": "1400-1800 bar (common rail)"},
    "COOLANT_TEMPERATURE": {"normal_C": "80-90", "max_C": 95},
    "LUBE_OIL_PRESSURE": {"unit": "bar", "min_bar": 2.0, "normal_bar": 3.5},
    "LUBE_OIL_TEMPERATURE": {"normal_C": "70-85", "max_C": 95},
    "CRANKCASE_PRESSURE": {"unit": "mm H2O", "typical_mmH2O": "0 to +10"},
    "AIR_INLET_RESTRICTION": {"max_mmH2O": 500},
    "EXHAUST_BACKPRESSURE": {"max_kPa": 10},
    "TURBO_INLET_TEMP": {"max_C": 50},
    "TURBO_BOOST_PRESSURE": {"unit": "bar", "typical_bar": "1.5-2.5"},
    "FUEL_CONSUMPTION_SPECIFIC": {"unit": "g/kWh", "typical": "195-215"},
}

IGBT_SPECIFICATIONS = {
    "semiconductor": {
        "device": "IGBT (Insulated Gate Bipolar Transistor)",
        "voltage_class_V": [1700, 3300, 4500, 6500],
        "current_class_A": [600, 1200, 1800, 2400, 3600],
        "switching_freq_kHz": "1-3 (traction)",
        "on_state_voltage_V": "2.5-4.0",
        "gate_voltage_on_V": 15,
        "gate_voltage_off_V": -15,
    },
    "thermal": {
        "junction_max_C": 150,
        "case_warning_C": 85,
        "case_critical_C": 95,
        "heatsink_normal_C": "60-75",
        "cooling_medium": "Forced Air or Water",
    },
    "protection": {
        "overcurrent": "Desaturation Detection",
        "overvoltage": "Active Clamp / TVS Diode",
        "overtemperature": "NTC Thermistor in Module",
        "gate_fault": "Short Circuit Protection Class I/II",
    },
    "abb_modules": {
        "WAP5_WAP7": "5SNA 2000K451300 (3.3kV, 2000A)",
        "WAG9": "5SNA 1200E330100 (3.3kV, 1200A)",
        "WAG12B": "5SNA 2000K451300 (4.5kV, 2000A)",
    },
}

DRAWING_STANDARDS = {
    "rdso_formats": {
        "electric_loco": r"RDSO/EL/[A-Z0-9]+/[A-Z]+/\d{4}",
        "diesel_loco": r"RDSO/M/L/[A-Z0-9]+/\d{4}",
        "power_electronics": r"RDSO/PE/SPEC/[A-Z]+/\d{4}",
    },
    "clw_formats": {
        "drawing": r"CLW/[A-Z0-9]+/[A-Z]+/\d{4}/[A-Z]?",
        "spec": r"CLW/SPEC/[A-Z0-9]+/\d{4}",
    },
    "dlw_formats": {
        "drawing": r"DLW/[A-Z0-9]+/[A-Z]+/\d{4}/\d{4}",
    },
}

TENDER_FRAMEWORK = {
    "classification": {
        "LTE": "Limited Tender Enquiry",
        "OTE": "Open Tender Enquiry",
        "STE": "Single Tender Enquiry",
        "GTE": "Global Tender Enquiry",
    },
    "financial_instruments": {
        "EMD": "Earnest Money Deposit",
        "SD": "Security Deposit (5-10% of contract value)",
        "BG": "Bank Guarantee",
        "LC": "Letter of Credit",
    },
    "evaluation_criteria": {
        "L1": "Lowest Evaluated Bidder",
        "QCBS": "Quality-cum-Cost Based Selection",
        "NQCBS": "Non-Quality-cum-Cost Based",
    },
    "procurement_portals": ["IREPS", "GeM", "CPP Portal"],
}

ABBREVIATIONS_USER = {
    "IGBT": "Insulated Gate Bipolar Transistor",
    "VVVF": "Variable Voltage Variable Frequency",
    "DSP": "Digital Signal Processor",
    "CPLD": "Complex Programmable Logic Device",
    "FPGA": "Field Programmable Gate Array",
    "CAN": "Controller Area Network",
    "MVB": "Multifunction Vehicle Bus",
    "WTB": "Wire Train Bus",
    "MPU": "Microprocessor Unit",
    "RTU": "Remote Terminal Unit",
    "PLC": "Programmable Logic Controller",
    "HMI": "Human Machine Interface",
    "SCADA": "Supervisory Control And Data Acquisition",
    "EDMS": "Electronic Document Management System",
    "LDO": "Locomotive Drawing Order",
    "BOM": "Bill of Materials",
    "ECN": "Engineering Change Note",
    "FAT": "Factory Acceptance Test",
    "SAT": "Site Acceptance Test",
    "ITP": "Inspection & Test Plan",
    "QAP": "Quality Assurance Plan",
    "MTC": "Material Test Certificate",
    "WPS": "Welding Procedure Specification",
    "PQR": "Procedure Qualification Record",
}

OCR_TRAINING_PATTERNS = {
    "loco_model": r"W[ADPG]{1,2}[GP]?-?\d[A-Z]?",
    "rdso_spec": r"RDSO/[A-Z]+/[A-Z]+/[A-Z0-9]+/\d{4}",
    "drawing_no": r"[A-Z]{2,4}/[A-Z0-9]+/[A-Z]+/\d{4}/[A-Z0-9]?",
    "rev_code": r"Rev\.?\s*[A-Z0-9]",
    "date": r"\d{1,2}[-./]\d{1,2}[-./]\d{2,4}",
    "serial_no": r"\b\d{5,6}\b",
    "temperature": r"\d{1,3}\s*(?:deg\s*C|\u00b0C)",
    "pressure_bar": r"\d+\.?\d*\s*bar",
    "current_A": r"\d+\.?\d*\s*[Aa](?:mps?)?",
    "voltage_kV": r"\d+\.?\d*\s*k[Vv]",
    "power_kW": r"\d+\.?\d*\s*k[Ww]",
    "speed_kmph": r"\d{2,3}\s*km[/\s]h",
}

PERFORMANCE_KPIS = {
    "availability": {"target_pct": 95, "formula": "(Serviceable Days / Total Days) * 100"},
    "reliability": {"unit": "MKBF", "desc": "Mean Kilometers Between Failures", "target_km": 50000},
    "punctuality": {"target_pct": 99, "applies_to": "Scheduled departures/arrivals"},
    "fuel_efficiency": {"unit": "HPIL", "desc": "HP-hours per Liter", "target_HPIL": 4.2},
    "energy_consumption": {"unit": "kWh per 1000 GTKM", "target": 14.0},
}
