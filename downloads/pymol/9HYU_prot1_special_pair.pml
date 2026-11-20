# PSI Contact Atlas — 9HYU protomer 1, special pair
# Chromera velia · Alveolate, PSI-FCP with SOD heterodimer · Cryo-EM 1.84 Å
#
# Run from the repository root:   pymol downloads/pymol/9HYU_prot1_special_pair.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/9HYU_prot1_special_pair.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 9HYU, scene, type=cif
select lib_atoms, scene and ((chain A and resi 244+248+252+321+376+380+384+387+407+524) or (chain B and resi 1000+1062+1065+1125+1128+1129+1132+1207))

# --- style: white background, grey carbon, element colours (library palette)
bg_color white
set orthoscopic, 1
set stick_radius, 0.13
set sphere_scale, 0.25
hide everything
show sticks, lib_atoms
show spheres, lib_atoms and (elem MG or resn HOH)
set_color lib_C, [0.5, 0.5, 0.5]
color lib_C, lib_atoms and elem C
set_color lib_N, [0.15, 0.3, 0.9]
color lib_N, lib_atoms and elem N
set_color lib_O, [1.0, 0.12, 0.12]
color lib_O, lib_atoms and elem O
set_color lib_S, [0.95, 0.8, 0.1]
color lib_S, lib_atoms and elem S
set_color lib_Mg, [0.1, 0.75, 0.25]
color lib_Mg, lib_atoms and elem MG
# cofactor(s) slightly thicker
set_bond stick_radius, 0.16, scene and ((chain A and resi 407 and resn CL0) or (chain B and resi 1207 and resn CLA))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# CLA B 1207 MG ··· HIS B 1062 NE2 = 1.91 Å (Mg ligand)
distance d01_mg, scene and (chain B and resi 1207 and resn CLA and name MG), scene and (chain B and resi 1062 and resn HIS and name NE2)
# CL0 A 407 MG ··· HIS A 321 NE2 = 1.91 Å (Mg ligand)
distance d02_mg, scene and (chain A and resi 407 and resn CL0 and name MG), scene and (chain A and resi 321 and resn HIS and name NE2)
# CL0 A 407 O1A ··· TYR A 376 OH = 2.66 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 407 and resn CL0 and name O1A), scene and (chain A and resi 376 and resn TYR and name OH)
# CL0 A 407 OBD ··· THR A 384 OG1 = 2.94 Å (polar candidate)
distance d04_polar, scene and (chain A and resi 407 and resn CL0 and name OBD), scene and (chain A and resi 384 and resn THR and name OG1)
# CLA B 1207 O1D ··· TYR B 1129 N = 3.07 Å (polar candidate)
distance d05_polar, scene and (chain B and resi 1207 and resn CLA and name O1D), scene and (chain B and resi 1129 and resn TYR and name N)
# CL0 A 407 O2D ··· THR A 384 OG1 = 3.31 Å (polar candidate)
distance d06_polar, scene and (chain A and resi 407 and resn CL0 and name O2D), scene and (chain A and resi 384 and resn THR and name OG1)
# CL0 A 407 O2D ··· TYR A 244 OH = 3.36 Å (polar candidate)
distance d07_polar, scene and (chain A and resi 407 and resn CL0 and name O2D), scene and (chain A and resi 244 and resn TYR and name OH)
# CL0 A 407 O2D ··· HOH A 524 O = 3.31 Å (water polar candidate)
distance d08_water, scene and (chain A and resi 407 and resn CL0 and name O2D), scene and (chain A and resi 524 and resn HOH and name O)
# CLA B 1207 O2A ··· TYR B 1125 OH = 3.98 Å (longer context)
distance d09_context, scene and (chain B and resi 1207 and resn CLA and name O2A), scene and (chain B and resi 1125 and resn TYR and name OH)
set_color cls_mg, [0.09, 0.541, 0.235]
group Mg_ligand, d01_mg d02_mg
set dash_color, cls_mg, Mg_ligand
set dash_length, 0.3, Mg_ligand
set dash_gap, 0.0, Mg_ligand
set_color cls_polar, [0.114, 0.165, 0.227]
group polar_candidate, d03_polar d04_polar d05_polar d06_polar d07_polar
set dash_color, cls_polar, polar_candidate
set dash_length, 0.25, polar_candidate
set dash_gap, 0.18, polar_candidate
set_color cls_water, [0.043, 0.498, 0.612]
group water_polar_candidate, d08_water
set dash_color, cls_water, water_polar_candidate
set dash_length, 0.25, water_polar_candidate
set dash_gap, 0.18, water_polar_candidate
set_color cls_context, [0.541, 0.573, 0.612]
group longer_context, d09_context
set dash_color, cls_context, longer_context
set dash_length, 0.08, longer_context
set dash_gap, 0.3, longer_context

# --- labels (residues at the library anchor atoms, roles as plain text)
set label_font_id, 7
set label_size, 16
set float_labels, 1
label scene and (chain A and resi 244 and resn TYR and name CA), "Tyr244 A"
label scene and (chain A and resi 248 and resn SER and name CA), "Ser248 A"
label scene and (chain A and resi 252 and resn PHE and name CA), "Phe252 A"
label scene and (chain A and resi 321 and resn HIS and name CA), "His321 A"
label scene and (chain A and resi 376 and resn TYR and name CA), "Tyr376 A"
label scene and (chain A and resi 380 and resn GLY and name CA), "Gly380 A"
label scene and (chain A and resi 384 and resn THR and name CA), "Thr384 A"
label scene and (chain A and resi 387 and resn PHE and name CA), "Phe387 A"
label scene and (chain A and resi 407 and resn CL0 and name MG), "PA"
label scene and (chain B and resi 1000 and resn PHE and name CA), "Phe1000 B"
label scene and (chain B and resi 1062 and resn HIS and name CA), "His1062 B"
label scene and (chain B and resi 1065 and resn TRP and name CA), "Trp1065 B"
label scene and (chain B and resi 1125 and resn TYR and name CA), "Tyr1125 B"
label scene and (chain B and resi 1128 and resn THR and name CA), "Thr1128 B"
label scene and (chain B and resi 1129 and resn TYR and name CA), "Tyr1129 B"
label scene and (chain B and resi 1132 and resn PHE and name CA), "Phe1132 B"
label scene and (chain B and resi 1207 and resn CLA and name MG), "PB"
label scene and (chain A and resi 524 and resn HOH and name O), "HOH524 A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (0.872380, 0.358277, 0.332552, -0.387603, 0.092464, 0.917178, 0.297855, -0.929025, 0.219533, 0.000000, -2.058625, -124.535011, 196.784150, 176.315646, 178.219006, 105.042145, 144.027878, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
