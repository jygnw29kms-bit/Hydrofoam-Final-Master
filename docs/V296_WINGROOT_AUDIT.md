# v296 Wing-root fairings, 2026-11-08

Source: v295 Blender model; user-supplied Final-Master image remains the only appearance reference.

## Actual change
Four new closed loft surfaces at the central wing shoulders and the transitions to the two floats. 46 mesh objects, 0 non-manifold/open edges in per-object Blender audit. This is an incremental geometry correction, not a validated visual match.

## Files
- cad/Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend
- cad/Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.stl
- scripts/build_v296_wingroot_fairings.py
- scripts/render_v296.py
- renders/v296/assembled_{iso,top,side,front}.png

## Outstanding
Wing and fuselage meshes still overlap; joining into printable watertight subassemblies and real filleted continuous surfaces is not done. The whole-assembly STL is a visualization export only. No P2S part cuts, tolerances, screw seats, 3S power sizing, mass/CG, water and flight testing or final photo overlay acceptance. No README hero update because photo fidelity is not yet verified.
