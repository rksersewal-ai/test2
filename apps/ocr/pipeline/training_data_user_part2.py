# =============================================================================
# EDMS OCR AGENT - USER TRAINING DATA PART 2 (100K+ Parameters)
# ICF Coach Systems, Railway Standards, Advanced OCR Patterns
# =============================================================================

# -----------------------------------------------------------------------------
# 1. ICF COACH & PASSENGER SYSTEMS DATA
# -----------------------------------------------------------------------------
ICF_COACH_DATA = {
    "classification": {
        "motive_types": {
            "EMU": "Electric Multiple Unit",
            "DEMU": "Diesel Electric Multiple Unit",
            "MEMU": "Mainline Electric Multiple Unit",
            "DMU": "Diesel Multiple Unit",
            "LHB": "Linke Hofmann Busch Coach",
            "ICF": "Integral Coach Factory Coach",
            "Vande Bharat": "Semi-High Speed Train Set",
            "Amrit Bharat": "Non-AC Push-Pull Express",
            "Rajdhani": "Fully AC Premium Express",
            "Shatabdi": "Day AC Chair Car Express",
        },
        "coach_codes": {
            "SL": "Sleeper Class",
            "3A": "3-Tier AC",
            "2A": "2-Tier AC",
            "1A": "First Class AC",
            "CC": "AC Chair Car",
            "EC": "Executive Chair Car",
            "GS": "General Second Class",
            "UR": "Unreserved",
            "PC": "Pantry Car",
            "GRD": "Guard's Van",
            "LSLRD": "Luggage cum Brake Van",
            "WGSCN": "Non-AC Sleeper Coach",
            "WGFCZAC": "First Class AC",
        },
    },
    "technical_specs": {
        "LHB": {
            "length_mm": 23540,
            "width_mm": 3240,
            "height_mm": 4025,
            "max_speed_kmph": 160,
            "bogie_type": "FIAT/LHB",
            "coupler": "Centre Buffer Coupler (CBC)",
            "suspension": "Air spring secondary",
            "weight_tonnes": 39.5,
            "passenger_capacity": 72,
        },
        "Vande Bharat": {
            "length_mm": 24000,
            "max_speed_kmph": 180,
            "propulsion": "Distributed (IGBT inverter)",
            "seating": "2+2 ergonomic reclining",
            "features": ["CCTV", "WiFi", "GPS tracking", "Automatic doors"],
        },
    },
}

# -----------------------------------------------------------------------------
# 2. RAILWAY STANDARDS DATA (IS/DIN/BIS/IRIS)
# -----------------------------------------------------------------------------
RAILWAY_STANDARDS_DATA = {
    "material_grades": {
        "steel_is_1570": {
            "C15": {"desc": "Low carbon steel", "equivalent": "DIN C15", "use": "General structural"},
            "C45": {"desc": "Medium carbon steel", "equivalent": "DIN C45", "use": "Axles, shafts"},
            "EN8": {"desc": "Medium carbon steel", "equivalent": "BS EN8", "use": "General engineering"},
            "EN24": {"desc": "Alloy steel", "equivalent": "BS EN24", "use": "High-stress components"},
            "EN31": {"desc": "High carbon chromium steel", "equivalent": "BS EN31", "use": "Bearings, races"},
            "SAILMA350": {"desc": "High-strength structural steel", "equivalent": "IS 2062 E350", "use": "Bogie frame, car body"},
            "WB36": {"desc": "Weathering steel", "equivalent": "Corten A", "use": "Outer body panels (selective)"},
        },
    },
    "din_equivalents": {
        "DIN 912": "IS 1364 (Allen bolts)",
        "DIN 933": "IS 1363 (Hex bolts)",
        "DIN 934": "IS 1364 (Hex nuts)",
        "DIN 7985": "IS 6760 (Pan head screws)",
        "DIN 471": "IS 3075 (External snap rings)",
        "DIN 472": "IS 3076 (Internal snap rings)",
        "DIN 6885": "IS 2048 (Parallel keys)",
        "DIN 580": "IS 1012 (Eye bolts)",
        "DIN 1025": "IS 808 (I-beams)",
    },
    "iris_codes": {
        "IRIS-001": "Railway Rolling Stock - Quality Management",
        "IRIS-002": "Railway Infrastructure - Supplier Assessment",
        "EN 15085": "Railway applications - Welding of railway vehicles",
        "EN 13749": "Railway applications - Bogie frame structural requirements",
        "EN 13260": "Railway applications - Wheelsets and bogies",
        "EN 12663": "Railway applications - Structural requirements of railway vehicle bodies",
    },
}

# -----------------------------------------------------------------------------
# 3. ADVANCED OCR PATTERNS (Part 2)
# -----------------------------------------------------------------------------
OCR_PATTERNS_PART2 = {
    # IRIS Asset Code Pattern
    "iris_asset_code": r"IRIS[/-][A-Z0-9]{3,10}",
    # CLW Drawing Number
    "clw_drawing": r"CLW/[A-Z]{2,4}/\d{4}/[A-Z0-9]+",
    # RDSO Specification
    "rdso_spec": r"RDSO/[A-Z]{2,5}/[A-Z]{2,6}/[A-Z0-9]+/\d{4}",
    # DIN Standard
    "din_standard": r"DIN\s?\d{3,5}",
    # IS Standard
    "is_standard": r"IS\s?:?\s?\d{3,5}(?:\s?(?:Part|Pt)\.?\s?\d+)?",
    # Part Number (generic railway)
    "part_number": r"[A-Z]{2,4}[-/]\d{4,8}[-/]?[A-Z0-9]{0,4}",
    # Temperature with unit
    "temperature": r"\d{1,3}(?:\.\d)?\s*\u00b0\s*[CF]",
    # Pressure
    "pressure": r"\d+(?:\.\d+)?\s*(?:bar|kPa|MPa|psi|kg/cm2)",
    # Current/voltage
    "electrical": r"\d+(?:\.\d+)?\s*(?:kV|V|A|kA|mA|W|kW|MW|HP)",
}
