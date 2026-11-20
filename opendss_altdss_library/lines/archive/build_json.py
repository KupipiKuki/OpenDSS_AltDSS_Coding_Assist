"""Build the EPRI OpenDSS Line/LineCode property extraction JSON (AltDSS-Python 0.2.4 mapping).

Sources actually fetched and verified during this session:
  - https://opendss.epri.com/Line.html          (Line element overview, default parameters)
  - https://opendss.epri.com/Properties14.html  ("Line Properties" - complete ordered property list)
  - https://opendss.epri.com/LineCode1.html     (LineCode element overview + complete ordered property list)
  - https://raw.githubusercontent.com/dss-extensions/AltDSS-Python/0.2.4/altdss/Line.py
  - https://raw.githubusercontent.com/dss-extensions/AltDSS-Python/0.2.4/altdss/LineCode.py
  - https://raw.githubusercontent.com/dss-extensions/AltDSS-Python/0.2.4/altdss/Obj.py
"""
import json

OC = "Official-current"
UV = "Unverified"

def P(name, dtype, default, desc, ev=OC):
    return {"name": name, "data_type": dtype, "default_value": default,
            "description": desc, "evidence_label": ev}

line_props = [
    P("bus1", "string", None,
      "Name of bus for terminal 1. Node order definitions optional."),
    P("bus2", "string", None,
      "Name of bus for terminal 2."),
    P("linecode", "string", None,
      "Name of an existing LineCode object containing impedance definitions. Per the EPRI Line element page, if no line code or impedance data are specified, the default Line object is a 1000-ft overhead line with 336 MCM ACSR conductor on an 8-ft crossarm."),
    P("length", "real", None,
      "Length multiplier to be applied to the impedance data."),
    P("phases", "integer", 3,
      "No. of phases. Default = 3. A line has the same number of conductors per terminal as it has phases. Neutrals are not explicitly modeled unless declared as a 'phase', and the impedance matrices must be augmented accordingly."),
    P("r1", "real", None,
      "Positive-sequence resistance, ohms per unit length. Setting any of R1, R0, X1, X0, C1, C0 forces the program to use the symmetrical component line definition. Default Line object value is 0.0580 ohms per 1000 ft (EPRI Line element page)."),
    P("x1", "real", None,
      "Positive-sequence reactance, ohms per unit length. Default Line object value is 0.1206 ohms per 1000 ft (EPRI Line element page)."),
    P("r0", "real", None,
      "Zero-sequence resistance, ohms per unit length. Default Line object value is 0.1784 ohms per 1000 ft (EPRI Line element page)."),
    P("x0", "real", None,
      "Zero-sequence reactance, ohms per unit length. Default Line object value is 0.4047 ohms per 1000 ft (EPRI Line element page)."),
    P("c1", "real", None,
      "Positive-sequence capacitance, nanofarads per unit length. Setting any of R1, R0, X1, X0, C1, C0 forces the program to use the symmetrical component line definition. See also Cmatrix and B1."),
    P("c0", "real", None,
      "Zero-sequence capacitance, nanofarads per unit length."),
    P("b1", "real", None,
      "Alternate way to enter C1, microS per unit length."),
    P("b0", "real", None,
      "Alternate way to enter C0, microS per unit length."),
    P("normamps", "real", None,
      "Normal ampacity, amps."),
    P("emergamps", "real", None,
      "Emergency ampacity, amps. Usually the one-hour rating."),
    P("faultrate", "real", None,
      "Number of faults per year per unit length. This is the default for this general line construction."),
    P("pctperm", "real", None,
      "Percent of the faults that become permanent (requiring a line crew to repair and a sustained interruption)."),
    P("repair", "real", None,
      "Hours to repair."),
    P("basefreq", "real", 60.0,
      "Base Frequency at which the impedance values are specified. Default = 60.0 Hz."),
    P("rmatrix", "array", None,
      "Series resistance matrix, ohms per unit length. See Command Language for syntax ('|' separates rows; extraneous numbers on each row are ignored). Lower triangle form is acceptable. Using any of Rmatrix, Xmatrix, Cmatrix forces the program to use the matrix values for line impedance definition."),
    P("xmatrix", "array", None,
      "Series reactance matrix, ohms per unit length."),
    P("cmatrix", "array", None,
      "Shunt nodal capacitance matrix, nanofarads per unit length."),
    P("switch", "boolean", False,
      "{y/n | T/F} Default= no/false. Designates this line as a switch for graphics and algorithmic purposes. SIDE EFFECT: Sets R1=0.001 X1=0.0. You must reset if you want something different."),
    P("rg", "real", 0.01805,
      "Carson earth return resistance per unit length used to compute impedance values at base frequency. For making better frequency adjustments. Does not apply to impedances defined by Geometry. Default values are same as for the default LineCode object: 0.01805 ohms per 1000 ft at 60 Hz for Rho=100 (EPRI Line element page). Set both Rg and Xg = 0 to disable earth return frequency adjustment."),
    P("xg", "real", 0.155081,
      "Carson earth return reactance per unit length used to compute impedance values at base frequency. For making better frequency adjustments. Does not apply to impedances defined by Geometry. Default values are same as for the default LineCode object: 0.155081 ohms per 1000 ft at 60 Hz for Rho=100 (EPRI Line element page)."),
    P("rho", "real", 100,
      "Earth resistivity used to compute earth correction factor. Overrides Line geometry definition if specified. Default=100 meter ohms."),
    P("geometry", "string", None,
      "Geometry code for LineGeometry Object. Supercedes any previous definition of line impedance. Line constants are computed for each frequency change or rho change. CAUTION: may cause the number of phases to be redefined."),
    P("earthmodel", "string", None,
      "One of {Carson | FullCarson | Deri}. Default is the global value established with the Set EarthModel option. Used to override the global value for this line. Applies only when the 'geometry' property is used."),
    P("units", "string", "none",
      "Length Units = {none | mi | kft | km | m | Ft | in | cm} Default is None - assumes length units match impedance units."),
    P("seasons", "integer", None,
      "Defines the number of ratings to be defined for the wire, to be used only when defining seasonal ratings using the 'Ratings' property."),
    P("ratings", "array", None,
      "An array of ratings to be used when the seasonal ratings flag is True. It can be used to insert multiple ratings to change during a QSTS simulation to evaluate different ratings in lines."),
    P("linetype", "string", "OH",
      "Code designating the type of line. One of: OH, UG, UG_TS, UG_CN, SWT_LDBRK, SWT_FUSE, SWT_SECT, SWT_REC, SWT_DISC, SWT_BRK, SWT_ELBOW. OpenDSS currently does not use this internally. Default is OH."),
    P("epsrmedium", "real", 1.0,
      "Relative Permittivity of the medium, used by lines with a geometry definition. Default=1.0 (defaults to 1.0 for air)."),
    P("like", "string", None,
      "Name of an existing Line object to build this like."),
    P("spacing", "string", None,
      "Reference to a LineSpacing object for line constants calculation, used with the 'wires' property (spacing must be specified before wires). Not listed on the current EPRI Line properties page; exposed in AltDSS-Python 0.2.4 (LineProperties.Spacing) and the DSS C-API 0.14.5 engine.", UV),
    P("wires", "array", None,
      "Array of WireData names for use in an overhead line constants calculation, used with the 'spacing' property; renamed 'Conductors' in AltDSS-Python 0.2.4 (LineProperties.Conductors). Not listed on the current EPRI Line properties page.", UV),
    P("enabled", "boolean", None,
      "Indicates whether this element is enabled. Common PD-element property not listed on the current EPRI Line properties page; exposed in AltDSS-Python 0.2.4 (LineProperties.Enabled).", UV),
]

linecode_props = [
    P("nphases", "integer", 3,
      "Number of phases. Default = 3."),
    P("r1", "real", None,
      "Positive-Sequence resistance, ohms per unit length."),
    P("x1", "real", None,
      "Positive-Sequence reactance, ohms per unit length."),
    P("r0", "real", None,
      "Zero-Sequence resistance, ohms per unit length."),
    P("x0", "real", None,
      "Zero-Sequence reactance, ohms per unit length."),
    P("c1", "real", None,
      "Positive-Sequence capacitance, nanofarads per unit length."),
    P("c0", "real", None,
      "Zero-Sequence capacitance, nanofarads per unit length."),
    P("units", "string", None,
      "{mi | km | kft | m | ft | in | cm} Length units. If not specified, it is assumed that the units correspond to the length being used in the Line models."),
    P("rmatrix", "array", None,
      "Series resistance matrix, ohms per unit length. The order of matrices expected is the number of phases; matrices may be entered in lower triangle form or full matrix and the result is always symmetrical ('|' separates rows, e.g. Rmatrix=\"11 | 21 22 | 31 32 33\"). If any Symmetrical Component data is specified, the impedance matrices are determined from that data."),
    P("xmatrix", "array", None,
      "Series reactance matrix, ohms per unit length."),
    P("cmatrix", "array", None,
      "Shunt nodal capacitance matrix, nanofarads per unit length."),
    P("basefreq", "real", 60.0,
      "Base Frequency at which the impedance values are specified. Default = 60.0 Hz."),
    P("normamps", "real", None,
      "Normal ampacity, amps."),
    P("emergamps", "real", None,
      "Emergency ampacity, amps."),
    P("faultrate", "real", None,
      "Number of faults per year per unit length. This is the default for this general line construction."),
    P("pctperm", "real", None,
      "Percent of the fault that become permanent (requiring a line crew to repair and a sustained interruption)."),
    P("kron", "boolean", False,
      "Y/N. Default=N. Perform Kron reduction on the impedance matrix after it is formed, reducing order by 1. Do this only on initial definition after matrices are defined. Ignored for symmetrical components."),
    P("rg", "real", 0.01805,
      "Carson earth return resistance per unit length used to compute impedance values at base frequency. For making better adjustments of line impedance values for frequency for harmonics studies. Default= 0.01805 ohms per 1000 ft at 60 Hz. If you do not wish to adjust the earth return impedance for frequency, set both Rg and Xg to zero."),
    P("xg", "real", 0.155081,
      "Carson earth return reactance per unit length used to compute impedance values at base frequency. For making better adjustments of line impedance values for frequency for harmonics studies. Default= 0.155081 ohms per 1000 ft at 60 Hz. If you do not wish to adjust the earth return impedance for frequency, set both Rg and Xg to zero."),
    P("rho", "real", 100,
      "Earth resistivity used to compute earth correction factor. Default=100 meter ohms."),
    P("neutral", "integer", None,
      "Designates which conductor is the 'neutral' conductor that will be eliminated by Kron reduction. Default is the last conductor (nphases value). After Kron reduction this property is set to 0. Subsequent issuing of Kron=Yes will not do anything until this property is set to a legitimate value. Applies only to LineCodes defined by R, X, and C matrix."),
    P("b1", "real", None,
      "Alternate way to specify C1. Micro-siemens per unit length."),
    P("b0", "real", None,
      "Alternate way to specify C0. Micro-siemens per unit length."),
    P("seasons", "integer", None,
      "Defines the number of ratings to be defined for the wire, to be used only when defining seasonal ratings using the 'Ratings' property."),
    P("ratings", "array", None,
      "An array of ratings to be used when the seasonal ratings flag is True. It can be used to insert multiple ratings to change during a QSTS simulation to evaluate different ratings in lines."),
    P("like", "string", None,
      "Name of an existing LineCode object to build this like."),
    P("repair", "real", None,
      "Hours to repair. Not listed on the current EPRI LineCode documentation page; exposed in AltDSS-Python 0.2.4 (LineCodeProperties.Repair) and the DSS C-API 0.14.5 engine.", UV),
    P("linetype", "string", None,
      "Code designating the type of line (e.g. OH, UG, UG_CN). Not listed on the current EPRI LineCode documentation page; exposed in AltDSS-Python 0.2.4 (LineCodeProperties.LineType).", UV),
]

result = [
    {
        "element_class": "Line",
        "epri_doc_url": "https://opendss.epri.com/Line.html",
        "properties": line_props,
        "required_properties": ["bus1", "bus2"],
        "altdss_mapping": "altdss.Line",
        "evidence_label": "Official-versioned"
    },
    {
        "element_class": "LineCode",
        "epri_doc_url": "https://opendss.epri.com/LineCode1.html",
        "properties": linecode_props,
        "required_properties": [],
        "altdss_mapping": "altdss.LineCode",
        "evidence_label": "Official-versioned"
    },
]

out = "/home/z/my-project/download/opendss_line_linecode_properties.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

# ---- validation ----
data = json.load(open(out, encoding="utf-8"))
VALID_DT = {"string", "real", "integer", "array", "boolean", "variant"}
VALID_EV = {"Official-current", "Official-versioned", "Unverified"}
assert len(data) == 2
for entry in data:
    assert set(entry) == {"element_class", "epri_doc_url", "properties",
                          "required_properties", "altdss_mapping", "evidence_label"}, entry["element_class"]
    names = []
    for p in entry["properties"]:
        assert set(p) == {"name", "data_type", "default_value", "description", "evidence_label"}
        assert p["data_type"] in VALID_DT, p
        assert p["evidence_label"] in VALID_EV, p
        dv, dt = p["default_value"], p["data_type"]
        if dv is not None:
            assert {"string": str, "real": (int, float), "integer": int,
                    "boolean": bool, "array": list}[dt].__instancecheck__ if False else True
            if dt == "string": assert isinstance(dv, str), p
            elif dt == "real": assert isinstance(dv, (int, float)) and not isinstance(dv, bool), p
            elif dt == "integer": assert isinstance(dv, int) and not isinstance(dv, bool), p
            elif dt == "boolean": assert isinstance(dv, bool), p
            elif dt == "array": assert isinstance(dv, list), p
        names.append(p["name"])
    assert len(names) == len(set(names)), "duplicate property"
    for rp in entry["required_properties"]:
        assert rp in names, rp
    blob = json.dumps(entry)
    for bad in ("【", "TODO", "XXX", "PASTE", "undefined", "NaN"):
        assert bad not in blob, bad
    print(entry["element_class"], "->", entry["altdss_mapping"],
          "| properties:", len(names), "| required:", entry["required_properties"],
          "| Unverified:", sum(1 for p in entry["properties"] if p["evidence_label"] == "Unverified"))
print("JSON valid, saved to", out)
