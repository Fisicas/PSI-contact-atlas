# PSI Contact Atlas — 7DKZ protomer 1, P_A network
# Pisum sativum (pea) · Flowering plant, PSI-LHCI, X-ray · X-ray crystallography 2.3930 Å
#
# Run from the repository root:   pymol downloads/pymol/7DKZ_prot1_P_A.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/7DKZ_prot1_P_A.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 7DKZ, scene, type=cif
select lib_atoms, scene and ((chain A and resi 606+610+683+738+742+746+801+923))

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
set_bond stick_radius, 0.16, scene and ((chain A and resi 801 and resn CLA))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# CLA A 801 MG ··· HIS A 683 NE2 = 2.62 Å (Mg ligand)
distance d01_mg, scene and (chain A and resi 801 and resn CLA and name MG), scene and (chain A and resi 683 and resn HIS and name NE2)
# CLA A 801 O1A ··· TYR A 738 OH = 2.80 Å (polar candidate)
distance d02_polar, scene and (chain A and resi 801 and resn CLA and name O1A), scene and (chain A and resi 738 and resn TYR and name OH)
# CLA A 801 O2D ··· THR A 746 OG1 = 2.90 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 801 and resn CLA and name O2D), scene and (chain A and resi 746 and resn THR and name OG1)
# CLA A 801 OBD ··· THR A 746 OG1 = 2.94 Å (polar candidate)
distance d04_polar, scene and (chain A and resi 801 and resn CLA and name OBD), scene and (chain A and resi 746 and resn THR and name OG1)
# CLA A 801 O2D ··· TYR A 606 OH = 3.32 Å (polar candidate)
distance d05_polar, scene and (chain A and resi 801 and resn CLA and name O2D), scene and (chain A and resi 606 and resn TYR and name OH)
# HOH A 923 O ··· THR A 746 OG1 = 2.98 Å (water polar candidate)
distance d06_water, scene and (chain A and resi 923 and resn HOH and name O), scene and (chain A and resi 746 and resn THR and name OG1)
# HOH A 923 O ··· TYR A 606 OH = 3.05 Å (water polar candidate)
distance d07_water, scene and (chain A and resi 923 and resn HOH and name O), scene and (chain A and resi 606 and resn TYR and name OH)
# CLA A 801 O2D ··· HOH A 923 O = 3.46 Å (water polar candidate)
distance d08_water, scene and (chain A and resi 801 and resn CLA and name O2D), scene and (chain A and resi 923 and resn HOH and name O)
# CLA A 801 OBD ··· CLA A 801 O2D = 3.30 Å (intramolecular)
distance d09_intra, scene and (chain A and resi 801 and resn CLA and name OBD), scene and (chain A and resi 801 and resn CLA and name O2D)
set_color cls_mg, [0.09, 0.541, 0.235]
group Mg_ligand, d01_mg
set dash_color, cls_mg, Mg_ligand
set dash_length, 0.3, Mg_ligand
set dash_gap, 0.0, Mg_ligand
set_color cls_polar, [0.114, 0.165, 0.227]
group polar_candidate, d02_polar d03_polar d04_polar d05_polar
set dash_color, cls_polar, polar_candidate
set dash_length, 0.25, polar_candidate
set dash_gap, 0.18, polar_candidate
set_color cls_water, [0.043, 0.498, 0.612]
group water_polar_candidate, d06_water d07_water d08_water
set dash_color, cls_water, water_polar_candidate
set dash_length, 0.25, water_polar_candidate
set dash_gap, 0.18, water_polar_candidate
set_color cls_intra, [0.478, 0.322, 0.78]
group intramolecular, d09_intra
set dash_color, cls_intra, intramolecular
set dash_length, 0.3, intramolecular
set dash_gap, 0.12, intramolecular

# --- labels (residues at the library anchor atoms, roles as plain text)
set label_font_id, 7
set label_size, 16
set float_labels, 1
label scene and (chain A and resi 801 and resn CLA and name MG), "PA"
label scene and (chain A and resi 606 and resn TYR and name CA), "Tyr606 A"
label scene and (chain A and resi 610 and resn SER and name CA), "Ser610 A"
label scene and (chain A and resi 683 and resn HIS and name CA), "His683 A"
label scene and (chain A and resi 738 and resn TYR and name CA), "Tyr738 A"
label scene and (chain A and resi 742 and resn GLY and name CA), "Gly742 A"
label scene and (chain A and resi 746 and resn THR and name CA), "Thr746 A"
label scene and (chain A and resi 923 and resn HOH and name O), "HOH923 A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (-0.972064, -0.030060, -0.232781, 0.231887, -0.276447, -0.932633, -0.036317, -0.960559, 0.275695, 0.000000, 3.492929, -127.180267, 20.867356, 55.042715, 34.066194, 107.743217, 146.617325, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
