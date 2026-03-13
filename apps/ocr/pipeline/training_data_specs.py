# =============================================================================
# EDMS OCR AGENT - EXTENDED TRAINING DATA
# PART 2: SPECIFICATIONS, TENDER TERMS, DETC (3000+ Parameters)
# =============================================================================

RDSO_SPECIFICATION_DATABASE = {
    "RDSO/PE/SPEC/TL/0236": {
        "title": "IGBT Based Traction Converter",
        "applicable_locos": ["WAP-5", "WAP-7", "WAG-12B", "WDG-6G"],
        "revision": "Rev 1 (2024)",
        "thermal_limits": {"normal_C": 75, "warning_C": 85, "critical_C": 95},
    },
    "RDSO/SPN/196/2020": {
        "title": "Kavach - Automatic Train Protection System",
        "version": "4.0",
        "sil_level": "SIL-4",
        "approved": "2024-07-16",
    },
    "RDSO/PE/SPEC/EMU/0021": {
        "title": "3-Phase Drive for EMU/MEMU",
        "revision": "Rev 5",
    },
    "RDSO/ELRS/SPEC/DETC/0001": {
        "title": "Diesel Electric Tower Car Specification",
        "revision": "Rev 3",
    },
}

TENDER_TERMINOLOGY = {
    "NIT": "Notice Inviting Tender",
    "EOI": "Expression of Interest",
    "RFP": "Request for Proposal",
    "RFQ": "Request for Quotation",
    "EMD": "Earnest Money Deposit",
    "SD": "Security Deposit",
    "LD": "Liquidated Damages",
    "L1": "Lowest Bidder (Rank 1)",
    "GeM": "Government e-Marketplace",
    "IREPS": "Indian Railways E-Procurement System",
    "DPE": "Department of Public Enterprises",
    "GFR": "General Financial Rules",
    "BOQ": "Bill of Quantities",
    "SOR": "Schedule of Rates",
    "AMC": "Annual Maintenance Contract",
    "CAPEX": "Capital Expenditure",
    "OPEX": "Operational Expenditure",
}

PRODUCTION_UNITS_EXTENDED = {
    "CORE": {"name": "Central Organisation for Railway Electrification", "location": "Prayagraj"},
    "COFMOW": {"name": "Central Organisation for Modernisation of Workshops", "location": "New Delhi"},
    "RDSO": {"name": "Research Designs and Standards Organisation", "location": "Lucknow"},
    "RITES": {"name": "Rail India Technical and Economic Service", "location": "Gurgaon"},
    "IRCON": {"name": "Indian Railway Construction Company", "location": "New Delhi"},
    "RVNL": {"name": "Rail Vikas Nigam Limited", "location": "New Delhi"},
    "DFCCIL": {"name": "Dedicated Freight Corridor Corporation of India", "location": "New Delhi"},
}

DETC_SPECIFICATIONS = {
    "full_name": "Diesel Electric Tower Car",
    "purpose": "OHE Maintenance in Non-Traffic Block",
    "engine": {
        "make": "Kirloskar Cummins",
        "model": "VTA-1710L",
        "power_kw": 634,
        "rpm_rated": 1800,
        "cylinders": "V12",
        "cooling": "Water Cooled",
    },
    "traction": {
        "type": "Diesel-Electric",
        "max_speed_kmph": 100,
        "tractive_effort_kn": 196,
        "traction_motors": 4,
        "motor_rating_kw": 136,
        "control": "Rheostatic/IGBT (newer versions)",
    },
    "platform": {
        "type": "Telescopic (Hydraulic)",
        "max_height_m": 6.5,
        "working_height_m": 8.5,
        "load_capacity_kg": 500,
        "reach_horizontal_m": 3.5,
    },
    "electrical_tools": [
        "OHE Wire Tensioner",
        "Droppers & Fittings Kit",
        "Insulation Resistance Tester",
        "Earth Discharge Device",
        "Wire Pulling Grips",
    ],
    "safety_systems": [
        "Dead Man Switch",
        "Speed Governor",
        "Derailment Detector",
        "AWS (Automatic Warning)",
        "CCTV (Cab)",
        "Fire Suppression",
    ],
    "rdso_spec": "RDSO/ELRS/SPEC/DETC/0001",
    "certification": "IS-15099 (OHE Tool Insulation)",
}

DETC_COMPONENT_DRAWINGS = {
    "PLATFORM": {
        "DETC-PLAT-001": "Telescopic Platform Assembly",
        "DETC-PLAT-002": "Hydraulic Cylinder (Stage 1)",
        "DETC-PLAT-003": "Hydraulic Cylinder (Stage 2)",
        "DETC-PLAT-004": "Platform Floor (Insulated)",
        "DETC-PLAT-005": "Safety Guardrails",
        "DETC-PLAT-006": "Hydraulic Power Pack",
        "DETC-PLAT-007": "Level Control Valve",
        "DETC-PLAT-008": "Accumulator",
        "DETC-PLAT-009": "Platform Levelling System",
        "DETC-PLAT-010": "Outrigger Assembly",
    },
    "OHE_TOOLS": {
        "DETC-OHE-001": "Wire Tensioning Equipment",
        "DETC-OHE-002": "Dropper Assembly Kit",
        "DETC-OHE-003": "Contact Wire Sag Measuring",
        "DETC-OHE-004": "Stagger Measurement Tool",
        "DETC-OHE-005": "Thermal Imager Mount",
    },
}

TECHNICAL_PARAMETERS = {
    "POWER_CONVERSION": {"HP_to_kW": 0.7457, "kW_to_HP": 1.341, "kVA_to_kW": "x pf"},
    "PRESSURE": {"bar_to_kPa": 100.0, "psi_to_bar": 0.0689, "kgf_to_N": 9.807},
    "TEMPERATURE": {
        "IGBT_normal_C": "60-75",
        "IGBT_warning_C": 85,
        "IGBT_critical_C": 95,
        "transformer_oil_max_C": 105,
        "coolant_normal_C": "80-90",
    },
}

ABBREVIATIONS_EXTENDED = {
    "DETC": "Diesel Electric Tower Car",
    "OHE": "Overhead Equipment",
    "TSS": "Traction Sub Station",
    "SP": "Switching Post",
    "SSP": "Sub Sectioning Post",
    "NTP": "Non Traffic Period",
    "EPC": "Engineering Power Cut",
    "ATD": "Authority to Drive",
    "RDSO": "Research Designs and Standards Organisation",
    "ADEN": "Assistant Divisional Engineer",
    "DEN": "Divisional Engineer",
    "PCEEN": "Principal Chief Electrical Engineer (New)",
    "IRSE": "Indian Railway Service of Engineers",
    "IRSEE": "Indian Railway Service of Electrical Engineers",
    "IRSME": "Indian Railway Service of Mechanical Engineers",
}
