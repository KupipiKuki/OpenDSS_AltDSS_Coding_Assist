### QA Audit & Remediation Report: OpenDSS `Line` & `LineCode` Schema

**Target Environment:** AltDSS-Python `0.2.4` / EPRI Official OpenDSS

**Artifacts Reviewed:**

1. `opendss_line_linecode_properties.json` (Revision 1)


2. `opendss_line_linecode_properties_2.json` (Revision 2)



**Overall Audit Status:** **FAIL** (Do not commit to library until Revision 3 passes)

---

### Part 1: Summary of Revision 1 Audit (`opendss_line_linecode_properties.json`)

The initial extraction contained five primary defects:

1. **Factual Error in `Line.wires`:** Incorrectly stated that `wires` was renamed to `Conductors` in AltDSS-Python 0.2.4. (`wires` remains valid for `WireData`, while `conductors` was added as a generalized property supporting `WireData`, `CNData`, and `TSData`).


2. **False `"Unverified"` Evidence Labels:** `Line.spacing`, `Line.wires`, `Line.enabled`, `LineCode.repair`, and `LineCode.linetype` were labeled `"Unverified"` with false notes claiming they were absent from EPRI OpenDSS documentation.


3. **Missing EPRI Default Values:** Numerous properties (`Line.length`, `r1`, `x1`, `r0`, `x0`, `c1`, `c0`, `normamps`, `emergamps`, `faultrate`, `pctperm`, `repair`, `enabled`, and `LineCode` equivalents) were set to `null` despite having explicit defaults in EPRI OpenDSS.


4. **Incomplete `required_properties`:** Omitted `"name"` from both `Line` and `LineCode`, and omitted conditional impedance/length requirements for `Line`.


5. **Incorrect `altdss_mapping`:** Used Python class types (`altdss.Line`, `altdss.LineCode`) instead of the active circuit collection accessors (`altdss.lines`, `altdss.linecodes`).



---

### Part 2: New Findings in Revision 2 (`opendss_line_linecode_properties_2.json`)

While Revision 2 resolved the `Line.wires` description and restored most `Line` default values, it introduced a critical regression and left several items unresolved:

* **CRITICAL REGRESSION — Dropped Property (`LineCode.x0`):**
* During the edit between Revision 1 and Revision 2, **`x0` (Zero-Sequence reactance) was completely deleted** from `LineCode.properties` (the array jumps directly from `r0` to `c1`).




* **Inconsistent `LineCode` Default Values:**
* `LineCode` symmetrical components (`r1`, `x1`, `r0`, `x0`, `c1`, `c0`) remain `null`, even though EPRI OpenDSS initializes `LineCode` with the exact same default 336 MCM ACSR conductor parameters as `Line`.


* `LineCode.repair` was set to `0.0` based on an uninitialized C-API struct field, rather than the EPRI OpenDSS default of `3.0`.




* **Baseline Conflation in `Line.epsrmedium`:**
* `Line.epsrmedium` carries `evidence_label: "Official-current"` while its description notes it is absent from DSS C-API 0.14.5 / AltDSS-Python 0.2.4. Mixing EPRI current-release properties with older C-API engine notes creates ambiguity for downstream schema consumers.




* **Unresolved `altdss_mapping`:**
* Both classes still map to `"altdss.Line"` and `"altdss.LineCode"` instead of `"altdss.lines"` and `"altdss.linecodes"`.




* **Unresolved `Line.required_properties`:**
* Still lists only `["name", "bus1", "bus2"]` without capturing the mandatory impedance/length requirement in the schema structure itself.





---

### Part 3: Actionable Remediation Instructions for Coding Model

Apply the following exact fixes to `opendss_line_linecode_properties_2.json` to generate Revision 3:

1. **Restore `LineCode.x0` (Mandatory):**
Insert the missing `x0` property object into `LineCode.properties` immediately after `r0`:


```json
{
  "name": "x0",
  "data_type": "real",
  "default_value": 0.4047,
  "description": "Zero-Sequence reactance, ohms per unit length. Default (default LineCode object): 0.4047 ohms per 1000 ft.",
  "evidence_label": "Official-current"
}

```


2. **Standardize `LineCode` Default Values to Match EPRI OpenDSS:**
Update the following `default_value` fields in `LineCode.properties` so they match EPRI OpenDSS initialization and `Line` defaults:


* `r1`: `null` $\rightarrow$ `0.058`


* `x1`: `null` $\rightarrow$ `0.1206`


* `r0`: `null` $\rightarrow$ `0.1784`


* `x0`: `0.4047` (from Step 1)
* `c1`: `null` $\rightarrow$ `3.4`


* `c0`: `null` $\rightarrow$ `1.6`


* `repair`: `0.0` $\rightarrow$ `3.0` (update description to reflect EPRI OpenDSS default of `3.0` hours, noting DSS C-API 0.14.5 leaves it uninitialized at `0.0` if version-specific parity is needed).




3. **Fix `altdss_mapping` for AltDSS-Python 0.2.4:**
* In `Line`: change `"altdss_mapping": "altdss.Line"` to `"altdss_mapping": "altdss.lines"`.


* In `LineCode`: change `"altdss_mapping": "altdss.LineCode"` to `"altdss_mapping": "altdss.linecodes"`.




4. **Update `Line.required_properties`:**
Include the conditional impedance and length requirements in `Line.required_properties` (or add a companion `conditional_required_properties` field if the schema enforces strict string-only arrays in `required_properties`):


```json
"required_properties": [
  "name",
  "bus1",
  "bus2",
  "length (or default 1.0) + one impedance source: linecode | geometry | spacing+wires | r1/x1 | rmatrix/xmatrix"
]

```


5. **Clean Up `Line.epsrmedium` Version Metadata:**
* If the schema targets strict compatibility with **AltDSS-Python 0.2.4 / DSS C-API 0.14.5**, change `Line.epsrmedium` `evidence_label` from `"Official-current"` to `"Official-versioned"` (or `"EPRI-only"`) so code generators do not attempt to pass `epsrmedium` to AltDSS-Python 0.2.4 at runtime.