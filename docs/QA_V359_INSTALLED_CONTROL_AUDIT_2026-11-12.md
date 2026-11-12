# v359 installed-control audit on Jens-PC (2026-11-12)

Source: `cad/Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend` opened in Blender 4.5.10 LTS, running `scripts/audit_v359_control_installation.py`.

- Original master image SHA256 checked on Jens-PC: `a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd` (matches immutable reference).
- `assembly_screen_pass = false`.
- For each of `aileron_L`, `aileron_R`, `elevator_L`, `elevator_R`, `rudder`, the audit found no meshes under the required `<surface>__<part>` naming contract for surface, fixed/moving hinge, servo mount, horn, or pushrod; measured min/max deflection and sweep report SHA256 properties were absent.
- **Interpretation:** This proves that the v333 scene does not pass the current integration audit. It does not prove that geometrically equivalent parts under other names do not exist. Object mapping/inspection is required before geometry reconstruction.
- **No mechanical approval:** No swept-volume interference, tolerances, physical printed assembly or control authority demonstrated. No top/side/perspective photo-match approval. No land/water/air operation acceptance.

Local machine report (untracked, intentionally not committed): `docs/v359_control_installation_local.json`.

Next: inspect actual v333 scene object names, map existing surface objects to functional roles without inventing geometry, then integrate verified hinge and actuation solids and rerun the audit. README master imagery remains unchanged.
