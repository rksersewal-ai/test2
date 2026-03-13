# EDMS OCR Agent Training Data - January 2026
# Indian Railways Comprehensive Knowledge Base
# Sources: RDSO, CLW, DMW, DLF, Public Railway Documentation

# =============================================================================
# SECTION 1: LOCOMOTIVE FLEET DATABASE (As of January 2026)
# =============================================================================

LOCOMOTIVE_DATABASE = {
    # --- DIESEL LOCOMOTIVES ---
    "WDG-6G": {
        "type": "Diesel-Electric",
        "power_hp": 6000,
        "power_kw": 4474,
        "max_speed_kmph": 120,
        "traction": "AC-AC (IGBT)",
        "manufacturer": "GE Transportation / DLF Marhowrah",
        "tot_partner": "General Electric (USA)",
        "tot_year": 2015,
        "units_produced": 204,
        "gauge": "Broad Gauge (1676mm)",
        "axle_load_tonnes": 22.5,
        "tractive_effort_kn": 544,
        "aliases": ["ES43ACmi", "Evolution Series"],
        "status": "Last diesel induction (electrification)",
        "use_case": "Heavy-haul freight",
        "special_features": ["Trip Optimizer", "Distributed Power", "LOCOTROL"],
    },
    "WDG-4G": {
        "type": "Diesel-Electric",
        "power_hp": 4500,
        "power_kw": 3357,
        "max_speed_kmph": 120,
        "traction": "AC-AC",
        "manufacturer": "DLF Marhowrah",
        "units_operational": 800,
        "use_case": "Freight/Mixed",
        "aliases": ["GE Dash 4"],
    },
    "WDP-4D": {
        "type": "Diesel-Electric",
        "power_hp": 4500,
        "power_kw": 3357,
        "max_speed_kmph": 160,
        "manufacturer": "Banaras Locomotive Works",
        "units_operational": 500,
        "use_case": "Passenger (Rajdhani, Shatabdi)",
    },
    "ALCO WDM-3A": {
        "type": "Diesel-Electric",
        "power_hp": 3100,
        "max_speed_kmph": 120,
        "manufacturer": "DLW Varanasi",
        "status": "Being phased out",
        "use_case": "Mixed traffic",
    },
    # --- ELECTRIC LOCOMOTIVES ---
    "WAP-5": {
        "type": "AC Electric",
        "power_kw": 4480,
        "power_hp": 6000,
        "max_speed_kmph": 160,
        "traction": "3-phase AC (IGBT)",
        "manufacturer": "Chittaranjan Locomotive Works (CLW)",
        "tot_partner": "Adtranz (Switzerland) / ABB",
        "tot_year": 1995,
        "units_produced": 249,
        "voltage": "25 kV AC 50 Hz",
        "special_features": ["Regenerative braking", "Aerodynamic cab", "Remote monitoring"],
        "use_case": "Premium passenger (Shatabdi, Vande Bharat)",
    },
    "WAP-7": {
        "type": "AC Electric",
        "power_kw": 5400,
        "power_hp": 7240,
        "max_speed_kmph": 130,
        "traction": "3-phase AC (IGBT)",
        "manufacturer": "CLW",
        "units_operational": 1400,
        "use_case": "Freight/Passenger",
    },
    "WAG-9": {
        "type": "AC Electric Freight",
        "power_kw": 6120,
        "power_hp": 8205,
        "max_speed_kmph": 100,
        "manufacturer": "CLW/BHEL",
        "units_produced": 6983,
        "use_case": "Heavy freight",
    },
    "WAG-12B": {
        "type": "AC Electric Freight",
        "power_kw": 12000,
        "power_hp": 16090,
        "max_speed_kmph": 120,
        "traction": "IGBT Based",
        "manufacturer": "CLW Chittaranjan",
        "tot_partner": "Alstom (France)",
        "tot_year": 2017,
        "units_operational": 100,
        "axle_config": "Bo-Bo-Bo + Bo-Bo-Bo",
        "aliases": ["Prima T8", "9000 Class"],
        "use_case": "Super Heavy Freight (DFC)",
    },
    # --- EMERGING TECHNOLOGIES ---
    "H2-Hybrid": {
        "type": "Hydrogen-Hybrid",
        "status": "Pilot Phase",
        "start_date": "March 2025",
        "speed_kmph": 110,
        "manufacturer": "RDSO Design",
        "trial_route": "Kalka-Shimla / Jind-Sonipat",
        "fuel": "Green Hydrogen",
        "emissions": "Zero (Water vapor only)",
    },
    "Battery-Electric Shunter": {
        "type": "Electric-Hybrid",
        "power": "Battery + OHE",
        "manufacturer": "CLW / RDSO Design",
        "use_case": "Yard shunting (non-electrified sections)",
        "spec_ref": "RDSO/2020/EL-HY/Draft",
    },
    "Medha E6": {
        "type": "Battery-Electric",
        "power_kw": 600,
        "manufacturer": "Medha Servo Drives",
        "status": "Under Development",
        "use_case": "Zero-emission shunting",
    },
}

# =============================================================================
# SECTION 2: MAINTENANCE SCHEDULES & CODES
# =============================================================================

MAINTENANCE_SCHEDULES = {
    "P1": {"name": "Trip Schedule", "periodicity_days": 10, "scope": "Running repairs, visual inspection, oil top-up, coolant check, exterior wash", "duration_hours": 2, "location": "Home Shed"},
    "P2": {"name": "Fortnightly Schedule", "periodicity_days": 30, "scope": "Air filter cleaning, fuel filter change, battery levels, brake adjustments", "duration_hours": 8, "location": "Home Shed"},
    "P3": {"name": "Monthly Schedule", "periodicity_days": 45, "scope": "Oil sampling, traction motor inspection, compressor check, governor tuning", "duration_hours": 24, "location": "Home Shed"},
    "P4": {"name": "Quarterly Schedule", "periodicity_days": 90, "scope": "Turbocharger cleaning, injector testing, wheel profiling, dynamic brake test", "duration_hours": 72, "location": "Diesel Shed"},
    "P5": {"name": "Half-Yearly Schedule", "periodicity_days": 180, "scope": "Major component overhaul, power pack service, bogie drop", "duration_hours": 168, "location": "Diesel Shed / Workshop"},
    "T1": {"name": "Trip Inspection", "periodicity_km": 3000, "scope": "Pantograph check, auxiliary systems, brake test"},
    "T2": {"name": "Monthly Electric", "periodicity_days": 30, "scope": "Traction motor brushes, transformer oil, IGBT cooling"},
    "T3": {"name": "Quarterly Electric", "periodicity_days": 90, "scope": "Major electrical tests, bogie inspection"},
    "T4": {"name": "Half-Yearly Electric", "periodicity_days": 180, "scope": "Transformer testing, wheel turning, full electrical overhaul"},
    "IOH": {"name": "Intermediate Overhaul", "periodicity_years": 4, "scope": "Mid-life rebuild, major component replacement", "location": "Workshop"},
    "POH": {"name": "Periodical Overhaul", "periodicity_years": 8, "scope": "Complete rebuild, life extension", "location": "Principal Workshops (DMW/CLW)"},
    "M-24": {"name": "24-Month Special", "scope": "IGBT module inspection, thyristor tests"},
    "M-36": {"name": "36-Month Special", "scope": "Traction transformer overhaul"},
    "AOH": {"name": "Accident Overhaul", "scope": "Post-incident rebuild"},
}

# =============================================================================
# SECTION 3: RDSO STANDARDS & SPECIFICATIONS
# =============================================================================

RDSO_SPECIFICATIONS = {
    "KAVACH": {
        "spec_no": "RDSO/SPN/196/2020",
        "version": "4.0",
        "approved_date": "2024-07-16",
        "type": "Automatic Train Protection (ATP)",
        "sil_level": "SIL-4",
        "features": ["Enhanced location accuracy", "Signal aspect info for large yards", "Electronic Interlocking interface", "SPAD prevention", "Emergency brake trigger"],
        "deployment_target": "2024-25 (5000+ km)",
        "radio_freq": "UHF (406-407 MHz)",
    },
    "DPWCS": {
        "spec_no": "RDSO/SPN/DPWCS/2023",
        "name": "Distributed Power Wireless Control",
        "description": "Multi-unit wireless loco control for long-haul freight",
        "frequency": "406-407 MHz UHF",
        "max_locos": 12,
    },
    "EOTT": {
        "spec_no": "RDSO/SPN/EOTT/2024",
        "name": "End of Train Telemetry",
        "description": "Guard-free freight operation",
    },
    "IGBT_MODULE": {
        "spec_no": "RDSO/PE/SPEC/TL/0236",
        "version": "2024 Rev 1",
        "thermal_normal": "60-75 deg C",
        "thermal_warning": "85 deg C",
        "thermal_critical": "95 deg C",
        "applications": ["WAP-5", "WAP-7", "WAG-12B", "WDG-6G"],
    },
    "TRACTION_MOTOR": {
        "types": {
            "TM410AR": {"power_kw": 410, "voltage": 750, "rpm": 1120, "use": "WAP-5"},
            "TM615": {"power_kw": 615, "voltage": 2180, "rpm": 970, "use": "WAG-9"},
            "TM850": {"power_kw": 850, "voltage": 2500, "use": "WAG-12B"},
        }
    },
    "DRAWING_STANDARDS": {
        "spec_no": "RDSO/M/DRG/2019",
        "sheet_sizes": ["A0", "A1", "A2", "A3", "A4"],
        "title_block": "RDSO Standard",
        "numbering": {"format": "XX/YY/ZZZZ/NNN", "XX": "Department Code", "YY": "Year", "ZZZZ": "Subject Code", "NNN": "Serial Number"},
        "revision_markings": ["A", "B", "C"],
        "approval_workflow": ["Draughtsman", "ADEN", "DEN", "PCEEN"],
    },
}

# =============================================================================
# SECTION 4: MANUFACTURING UNITS
# =============================================================================

PRODUCTION_UNITS = {
    "CLW": {"name": "Chittaranjan Locomotive Works", "location": "Chittaranjan, West Bengal", "established": 1950, "products": ["Electric Locomotives", "WAP-5", "WAP-7", "WAG-9", "WAG-12B"], "capacity_per_year": 500, "certifications": ["ISO 9001", "ISO 14001"], "tot_partners": ["Adtranz/ABB (WAP-5)", "Alstom (WAG-12B)"]},
    "DLF": {"name": "Diesel Locomotive Factory", "location": "Marhowrah, Bihar", "established": 2016, "products": ["WDG-6G", "WDG-4G"], "capacity_per_year": 100, "tot_partners": ["GE Transportation"], "aliases": ["DLW Marhowrah"]},
    "DLW": {"name": "Diesel Locomotive Works", "location": "Varanasi, Uttar Pradesh", "established": 1961, "products": ["WDM-3A", "WDP-4D", "WDG-4"], "capacity_per_year": 200, "status": "Transitioning to electric components"},
    "DMW": {"name": "Diesel Loco Modernisation Works", "location": "Patiala, Punjab", "established": 1981, "products": ["Loco upgrades", "Component manufacturing", "POH"], "aliases": ["PLW (Patiala Locomotive Works)"], "certifications": ["ISO 9001:2015"]},
    "BLW": {"name": "Banaras Locomotive Works", "location": "Varanasi, Uttar Pradesh", "products": ["WDG-5", "ALCO locos"], "capacity": 150},
    "ICF": {"name": "Integral Coach Factory", "location": "Chennai, Tamil Nadu", "products": ["LHB Coaches", "Vande Bharat", "Amrit Bharat"]},
    "RCF": {"name": "Rail Coach Factory", "location": "Kapurthala, Punjab", "products": ["LHB Coaches", "AC Coaches"]},
}

# =============================================================================
# SECTION 5: DOCUMENT TYPES & PATTERNS
# =============================================================================

DOCUMENT_TYPES = {
    "DRG": {"code": "DRG", "name": "Engineering Drawing", "patterns": [r"Drg\.?\s*No\.?", r"Drawing\s+Number", r"RDSO\s+Drg"], "numbering": r"[A-Z]{2,4}/\d{2,4}/[A-Z\d]+/\d+"},
    "SMI": {"code": "SMI", "name": "Special Maintenance Instruction", "patterns": [r"SMI[/-]", r"Special\s+Maintenance\s+Instruction"], "numbering": r"SMI[/-]?[A-Z]*[/-]?\d{4}[/-]\d{2,4}", "issuing_authority": ["RDSO", "CLW", "DLW", "Zonal Railways"]},
    "CAMTECH": {"code": "CAMTECH", "name": "CAMTECH Technical Bulletin", "patterns": [r"CAMTECH", r"Technical\s+Bulletin"], "numbering": r"CAMTECH[/-]\d{4}[/-]\d{2,4}"},
    "STR": {"code": "STR", "name": "Schedule of Technical Requirements", "patterns": [r"STR", r"Schedule\s+of\s+Technical"], "use": "Tender specifications"},
    "JC": {"code": "JC", "name": "Job Card", "patterns": [r"JC[/-]", r"Job\s+Card"], "numbering": r"JC[/-]?\d{4}[/-]\d{3,4}"},
    "SR": {"code": "SR", "name": "Service Record", "patterns": [r"SR[/-]", r"Service\s+Record"], "numbering": r"SR[/-]?[A-Z0-9]+[/-]\d+[/-]\d{4}"},
    "EC": {"code": "EC", "name": "Engineering Change", "patterns": [r"EC[/-]", r"Engineering\s+Change"], "numbering": r"EC[/-]?\d{4}[/-]\d+"},
    "TB": {"code": "TB", "name": "Technical Bulletin", "patterns": [r"TB[/-]", r"Tech\.?\s*Bulletin"]},
    "TI": {"code": "TI", "name": "Technical Instruction", "patterns": [r"TI[/-]", r"Technical\s+Instruction"]},
    "SOP": {"code": "SOP", "name": "Standard Operating Procedure", "patterns": [r"SOP[/-]", r"Standard\s+Operating"]},
}

# =============================================================================
# SECTION 6: RAILWAY ABBREVIATIONS
# =============================================================================

RAILWAY_ABBREVIATIONS = {
    "RDSO": "Research Designs and Standards Organisation",
    "CLW": "Chittaranjan Locomotive Works",
    "DLW": "Diesel Locomotive Works (Varanasi)",
    "DLF": "Diesel Locomotive Factory (Marhowrah)",
    "DMW": "Diesel Loco Modernisation Works (Patiala)",
    "BLW": "Banaras Locomotive Works",
    "ICF": "Integral Coach Factory (Chennai)",
    "RCF": "Rail Coach Factory (Kapurthala)",
    "CAMTECH": "Centre for Advanced Maintenance Technology",
    "COFMOW": "Central Organisation for Modernisation of Workshops",
    "IGBT": "Insulated Gate Bipolar Transistor",
    "GTO": "Gate Turn-Off Thyristor",
    "VVVF": "Variable Voltage Variable Frequency",
    "ATP": "Automatic Train Protection",
    "ATC": "Automatic Train Control",
    "TCAS": "Train Collision Avoidance System",
    "KAVACH": "Kavach (Indigenous ATP - means Armor)",
    "SPAD": "Signal Passed At Danger",
    "OHE": "Overhead Equipment (25kV AC)",
    "EMU": "Electric Multiple Unit",
    "DEMU": "Diesel Electric Multiple Unit",
    "MEMU": "Mainline Electric Multiple Unit",
    "LHB": "Linke Hofmann Busch (Coach design)",
    "CBC": "Centre Buffer Coupler",
    "MU": "Multiple Unit (working)",
    "POH": "Periodical Overhaul",
    "IOH": "Intermediate Overhaul",
    "AOH": "Accident Overhaul",
    "ROH": "Routine Overhaul",
    "TXR": "Traction Motor Exchange Repair",
    "SSE": "Senior Section Engineer",
    "CWI": "Chief Workshop Inspector",
    "CME": "Chief Mechanical Engineer",
    "CEE": "Chief Electrical Engineer",
    "ToT": "Transfer of Technology",
    "DFC": "Dedicated Freight Corridor",
    "WDFC": "Western Dedicated Freight Corridor",
    "EDFC": "Eastern Dedicated Freight Corridor",
    "DFCCIL": "Dedicated Freight Corridor Corporation of India Ltd",
}

# =============================================================================
# SECTION 7: TECHNICAL PARAMETERS
# =============================================================================

TECHNICAL_PARAMETERS = {
    "POWER": {"units": ["HP", "kW", "MW"], "conversions": {"HP_to_kW": 0.7457, "kW_to_HP": 1.341}},
    "SPEED": {"units": ["km/h", "kmph", "mph"], "max_operational": 160, "design_max": 200},
    "TEMPERATURE": {"igbt_normal": "60-75 deg C", "igbt_warning": "85 deg C", "igbt_critical": "95 deg C", "coolant_normal": "80-90 deg C", "transformer_oil_max": "105 deg C"},
    "VOLTAGE": {"ohc": "25 kV AC 50 Hz", "dc_link": "2800 V DC", "auxiliary": "415 V AC / 110 V DC", "battery": "110 V DC"},
    "WEIGHT": {"units": ["tonnes", "kg"], "axle_load_freight": 22.5, "axle_load_passenger": 18.5},
    "GAUGE": {"broad": "1676 mm", "meter": "1000 mm", "narrow": "610 mm / 762 mm"},
}

# =============================================================================
# SECTION 8: STRATEGIC INITIATIVES (2025-2026)
# =============================================================================

STRATEGIC_INITIATIVES_2026 = {
    "ELECTRIFICATION": {"target": "100% passenger trains electric by FY 2025-26", "current_percentage": 95, "remaining_diesel_routes": ["Hill sections", "Remote areas"]},
    "GREEN_RAIL": {"hydrogen_train_pilot": "March 2025", "battery_shunters": "Under development", "diesel_replacement_target": 2500, "net_zero_target": 2030},
    "KAVACH_ROLLOUT": {"target_km": 5000, "target_year": "2024-25", "funding": "Approved Jan 2026"},
    "VANDE_BHARAT": {"sleeper_version": "Launch 2026", "target_trainsets": 400, "current_operational": 100},
    "AMRIT_BHARAT": {"gen2_prototype": "2025", "features": ["Semi-auto couplers", "EP brakes", "Sealed gangway", "Onboard monitoring"]},
}
