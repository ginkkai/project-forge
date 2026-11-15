# Five-Case Expansion Review Worksheet

This worksheet is generated from the versioned synthetic dataset and review CSV.
It is a reviewer aid, not evidence of a completed review. Record decisions in
`data/new_case_domain_review_v1.csv`, then run the strict validator.

Allowed values are `yes`, `no`, or `uncertain`; `correction_required` accepts
`yes` or `no`. Do not enter names, email addresses, employers, customers, sites,
real incident details, credentials, or proprietary information.

## 1. SYN-CNC-003 — 5-Axis CNC Machining Center

- **Review ID:** `NC-001`
- **Equipment ID:** `CNC-001`
- **Case fingerprint:** `03078be9ded4a0f60cbfc19fd691e959ed2122d7cced785c54de1820e28c136c`
- **Synthetic error code:** `SIM-E330`

**Symptom:** A simulated axis following error appears only during rapid positioning moves.

**Proposed root cause:** A simulated encoder feedback connector was not fully retained after maintenance access.

**Troubleshooting steps:**

1. Stop the machine and apply the approved electrical isolation procedure.
2. Review the alarm history and identify the affected axis.
3. Inspect accessible feedback connectors for retention without bypassing guards.
4. Run the approved reduced-speed axis verification after authorized correction.

**Proposed solution:** Secure the simulated encoder connector using the approved service procedure and record the intervention.

**Verification result:** The simulated axis completed ten reduced-speed and five rapid positioning cycles without another following error.

**Safety notes:**

- Stored electrical and mechanical energy can cause injury.
- Only authorized personnel may access feedback wiring or guarded motion components.

**Review decisions:**

- Technical plausibility: **Not reviewed**
- Root-cause plausibility: **Not reviewed**
- Troubleshooting sequence safe: **Not reviewed**
- Safety notes adequate: **Not reviewed**
- Correction required: **Not reviewed**
- Reviewer role: **Not reviewed**
- Review date: **Not reviewed**
- Review notes: **Not reviewed**

## 2. SYN-ROBOT-003 — Industrial Robot

- **Review ID:** `NC-002`
- **Equipment ID:** `ROBOT-001`
- **Case fingerprint:** `51fced8e154a4bb8b8a91665ba13431d745ed226102544fdd420e2b7b920a909`
- **Synthetic error code:** `SIM-R620`

**Symptom:** The robot grips a simulated part but the cell does not receive the part-present confirmation.

**Proposed root cause:** A simulated gripper presence sensor shifted outside its validated detection position.

**Troubleshooting steps:**

1. Place the robot cell in the approved safe state.
2. Review the input status and gripper change record.
3. Inspect sensor position and mounting without entering an energized hazardous zone.
4. Verify the signal through the approved reduced-speed test sequence.

**Proposed solution:** Restore the simulated sensor to its validated position and secure the mounting hardware.

**Verification result:** The simulated part-present signal changed correctly during twenty reduced-speed grip cycles.

**Safety notes:**

- Do not enter the safeguarded space while hazardous motion is enabled.
- Use the cell-specific isolation and restart procedure.

**Review decisions:**

- Technical plausibility: **Not reviewed**
- Root-cause plausibility: **Not reviewed**
- Troubleshooting sequence safe: **Not reviewed**
- Safety notes adequate: **Not reviewed**
- Correction required: **Not reviewed**
- Reviewer role: **Not reviewed**
- Review date: **Not reviewed**
- Review notes: **Not reviewed**

## 3. SYN-COMP-003 — Industrial Air Compressor

- **Review ID:** `NC-003`
- **Equipment ID:** `COMP-001`
- **Case fingerprint:** `0dbea413e0bb89a25d866acde91da60ce4172ce4e5ffe9c7b5d3a07e57000c8e`
- **Synthetic error code:** `SIM-C430`

**Symptom:** Moisture appears downstream even though simulated compressor pressure remains stable.

**Proposed root cause:** A simulated automatic condensate drain remained closed and allowed water to accumulate.

**Troubleshooting steps:**

1. Follow the approved shutdown and depressurization procedure.
2. Confirm the moisture observation at an approved sampling point.
3. Inspect the condensate collection point and drain status.
4. Test drain operation only with the approved service method.

**Proposed solution:** Restore the simulated condensate drain operation and document the collected condition.

**Verification result:** No simulated liquid carryover was observed during the next controlled operating cycle.

**Safety notes:**

- Compressed air and condensate can retain hazardous pressure.
- Verify zero energy before opening any drain or separator component.

**Review decisions:**

- Technical plausibility: **Not reviewed**
- Root-cause plausibility: **Not reviewed**
- Troubleshooting sequence safe: **Not reviewed**
- Safety notes adequate: **Not reviewed**
- Correction required: **Not reviewed**
- Reviewer role: **Not reviewed**
- Review date: **Not reviewed**
- Review notes: **Not reviewed**

## 4. SYN-INSPECT-003 — Coordinate Measuring Machine

- **Review ID:** `NC-004`
- **Equipment ID:** `INSPECT-001`
- **Case fingerprint:** `0d7039e24e0c33826e9bf248417de7100087d0a8388c681696ada980a7abcd7c`
- **Synthetic error code:** `SIM-I315`

**Symptom:** Reference measurements shift gradually after a new artifact is brought into the inspection room.

**Proposed root cause:** The simulated reference artifact had not reached the controlled room temperature before measurement.

**Troubleshooting steps:**

1. Place affected measurement decisions on hold.
2. Review artifact and room temperature records.
3. Allow the artifact to stabilize according to the approved procedure.
4. Repeat the controlled reference measurement sequence.

**Proposed solution:** Condition the simulated reference artifact for the approved stabilization period before use.

**Verification result:** The simulated reference result remained within the defined control band across ten repeats.

**Safety notes:**

- Handle calibrated artifacts using the approved method.
- Do not release product based on an unstable measurement system.

**Review decisions:**

- Technical plausibility: **Not reviewed**
- Root-cause plausibility: **Not reviewed**
- Troubleshooting sequence safe: **Not reviewed**
- Safety notes adequate: **Not reviewed**
- Correction required: **Not reviewed**
- Reviewer role: **Not reviewed**
- Review date: **Not reviewed**
- Review notes: **Not reviewed**

## 5. SYN-LASER-003 — Laser Marking Machine

- **Review ID:** `NC-005`
- **Equipment ID:** `LASER-001`
- **Case fingerprint:** `8d11d4dcbb5ac45330097241c6d26ddff14ed9b22912e7337b025dcedf10800c`
- **Synthetic error code:** `SIM-L370`

**Symptom:** A simulated serial number repeats after a batch change although the marking remains readable.

**Proposed root cause:** The simulated job counter was reset when an outdated recipe copy was loaded.

**Troubleshooting steps:**

1. Stop release of affected marked parts.
2. Compare the active recipe revision with the controlled job record.
3. Review the serial counter state without disabling enclosure safeguards.
4. Run approved test coupons after restoring the controlled sequence.

**Proposed solution:** Load the validated simulated recipe and restore the approved serial counter state.

**Verification result:** Five simulated test coupons showed the expected sequential serial numbers.

**Safety notes:**

- Keep all laser enclosure interlocks functional.
- Treat duplicate identification as a traceability hold until resolved.

**Review decisions:**

- Technical plausibility: **Not reviewed**
- Root-cause plausibility: **Not reviewed**
- Troubleshooting sequence safe: **Not reviewed**
- Safety notes adequate: **Not reviewed**
- Correction required: **Not reviewed**
- Reviewer role: **Not reviewed**
- Review date: **Not reviewed**
- Review notes: **Not reviewed**
