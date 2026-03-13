# =============================================================================
# EDMS OCR AGENT - ENGINEERING DRAWING INTELLIGENCE (10K+ Parameters)
# Specialized Training Data for Title Blocks, BOMs, GD&T, and Advanced Tech
# =============================================================================

import re

# -----------------------------------------------------------------------------
# 1. TITLE BLOCK INTELLIGENCE (Pattern Recognition)
# -----------------------------------------------------------------------------
TITLE_BLOCK_PATTERNS = {
    "drawing_number": re.compile(r"(?:drg\.?\s*no\.?|drawing\s*no\.?|dwg\.?\s*no\.?)\s*[:.]?\s*([A-Za-z0-9/\-]+)", re.IGNORECASE),
    "revision": re.compile(r"(?:rev\.?|revision)\s*[:.]?\s*([A-Z0-9]+)", re.IGNORECASE),
    "scale": re.compile(r"scale\s*[:.]?\s*(\d+[:/]\d+|N\.?T\.?S\.?)", re.IGNORECASE),
    "weight": re.compile(r"(?:wt\.?|weight|mass)\s*[:.]?\s*([\d\.]+\s*(?:kg|g|tonnes?))", re.IGNORECASE),
    "sheet_size": re.compile(r"(?:sheet|size)\s*[:.]?\s*(A[0-4])", re.IGNORECASE),
    "date_drawn": re.compile(r"(?:date|drawn\s*date)\s*[:.]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", re.IGNORECASE),
    "drawn_by": re.compile(r"(?:drawn\s*by|dsgn|designer)\s*[:.]?\s*([A-Z\.\s]+)", re.IGNORECASE),
    "checked_by": re.compile(r"(?:chkd|checked|chk)\s*[:.]?\s*([A-Z\.\s]+)", re.IGNORECASE),
    "approved_by": re.compile(r"(?:appd|approved|app)\s*[:.]?\s*([A-Z\.\s]+)", re.IGNORECASE),
    "material": re.compile(r"(?:matl|material)\s*[:.]?\s*([A-Za-z0-9\s\-/]+)", re.IGNORECASE),
    "finish": re.compile(r"(?:finish|surface)\s*[:.]?\s*([A-Za-z0-9\s]+)", re.IGNORECASE),
}

# -----------------------------------------------------------------------------
# 2. BILL OF MATERIALS (BOM) LOGIC
# -----------------------------------------------------------------------------
BOM_HEADERS = [
    "ITEM", "PT NO", "PART NO", "DESCRIPTION", "MATERIAL", "QTY", "REMARKS",
    "PC NO", "ZONE", "REV"
]

BOM_ROW_PATTERN = re.compile(r"^\s*(\d+)\s+([A-Z0-9\-]+)\s+(.+?)\s+(\d+)\s*(.*)$", re.MULTILINE)

# -----------------------------------------------------------------------------
# 3. GD&T SYMBOLS & TERMINOLOGY
# -----------------------------------------------------------------------------
GDT_SYMBOLS = {
    "FORM_TOLERANCES": {
        "Straightness": {"symbol": "--", "keywords": ["straightness", "strgt"]},
        "Flatness": {"symbol": "flat", "keywords": ["flatness", "flat"]},
        "Circularity": {"symbol": "O", "keywords": ["circularity", "roundness"]},
        "Cylindricity": {"symbol": "cyl", "keywords": ["cylindricity"]},
    },
    "ORIENTATION_TOLERANCES": {
        "Angularity": {"symbol": "ang", "keywords": ["angularity", "angle"]},
        "Perpendicularity": {"symbol": "perp", "keywords": ["perpendicularity", "perp", "squareness"]},
        "Parallelism": {"symbol": "parl", "keywords": ["parallelism", "parl"]},
    },
    "LOCATION_TOLERANCES": {
        "Position": {"symbol": "pos", "keywords": ["position", "pos", "TP"]},
        "Concentricity": {"symbol": "conc", "keywords": ["concentricity", "conc"]},
        "Symmetry": {"symbol": "sym", "keywords": ["symmetry"]},
    },
    "RUNOUT_TOLERANCES": {
        "Circular Runout": {"symbol": "runout", "keywords": ["circular runout", "runout"]},
        "Total Runout": {"symbol": "total runout", "keywords": ["total runout"]},
    },
    "MODIFIERS": {
        "Maximum Material Condition": {"symbol": "MMC", "code": "MMC"},
        "Least Material Condition": {"symbol": "LMC", "code": "LMC"},
        "Projected Tolerance Zone": {"symbol": "P", "code": "P"},
        "Free State": {"symbol": "F", "code": "F"},
    },
}

# -----------------------------------------------------------------------------
# 4. ADVANCED TECHNOLOGY & RAILWAY MODERNIZATION (2026)
# -----------------------------------------------------------------------------
ADVANCED_TECH_TERMS = {
    "Digital_Twin": ["Digital Twin", "Virtual Model", "Predictive Simulation", "Asset Mirroring", "Real-time Telemetry"],
    "IoT_Sensors": ["IoT", "Internet of Things", "Wireless Sensor Node", "Vibration Monitoring", "Thermal Sensing", "Remote Diagnostics"],
    "Predictive_Maintenance": ["CBM", "Condition Based Maintenance", "Predictive Analytics", "RCM", "Reliability Centered Maintenance", "Prognostics"],
    "Green_Energy": ["Hydrogen Fuel Cell", "H2", "Green Hydrogen", "PEM Fuel Cell", "Battery Electric", "BESS", "Regenerative Braking"],
    "Advanced_Materials": ["Composite", "Carbon Fiber", "Graphene", "Nano-coating", "Self-healing material", "Austenitic Stainless Steel"],
    "Signaling_Control": ["ETCS", "European Train Control System", "TCAS", "Kavach", "CBTC", "Communications Based Train Control", "Automatic Train Protection"],
}

# -----------------------------------------------------------------------------
# 5. ENGINEERING NOTE KEYWORDS
# -----------------------------------------------------------------------------
NOTE_KEYWORDS = [
    "REMOVE BURRS", "SHARP EDGES", "HEAT TREAT", "NORMALIZE",
    "ULTRASONIC TEST", "RADIOGRAPHY", "DYE PENETRANT", "MAGNETIC PARTICLE",
    "PAINT", "COAT", "PRIME", "FINISH", "PACKING", "DELIVERY",
    "TOLERANCE", "DIMENSIONS IN", "DO NOT SCALE"
]

# -----------------------------------------------------------------------------
# 6. DRAWING CLASSIFICATION RULES
# -----------------------------------------------------------------------------
DRAWING_CLASSIFICATION_RULES = {
    "GA": ["General Arrangement", "Overall View", "Layout", "Installation"],
    "SCH": ["Schematic", "Diagram", "Circuit", "Flowchart", "Single Line"],
    "DET": ["Detail", "Part Drawing", "Machining", "Fabrication"],
    "BOM": ["Bill of Materials", "Parts List", "Component List", "Schedule of Qty"],
    "ASS": ["Assembly", "Sub-Assembly", "Exploded View"],
    "WD": ["Wiring Diagram", "Cable Schedule", "Terminal"],
    "PID": ["Piping", "Instrumentation", "P&ID", "Process Flow"],
}
