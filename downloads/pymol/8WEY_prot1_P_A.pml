# PSI Contact Atlas — 8WEY protomer 1, P_A network
# Cyanidium caldarium RK-1 (NIES-2137) · Red alga, PSI-LHCI monomer · Cryo-EM 1.92 Å
#
# Run from the repository root:   pymol downloads/pymol/8WEY_prot1_P_A.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/8WEY_prot1_P_A.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 8WEY, scene, type=cif
select lib_atoms, scene and ((chain A and resi 596+600+673+728+732+736+801+1002))

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
set_bond stick_radius, 0.16, scene and ((chain A and resi 801 and resn CL0))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# CL0 A 801 MG ··· HIS A 673 NE2 = 2.27 Å (Mg ligand)
distance d01_mg, scene and (chain A and resi 801 and resn CL0 and name MG), scene and (chain A and resi 673 and resn HIS and name NE2)
# CL0 A 801 O1A ··· TYR A 728 OH = 2.60 Å (polar candidate)
distance d02_polar, scene and (chain A and resi 801 and resn CL0 and name O1A), scene and (chain A and resi 728 and resn TYR and name OH)
# CL0 A 801 OBD ··· THR A 736 OG1 = 2.76 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 801 and resn CL0 and name OBD), scene and (chain A and resi 736 and resn THR and name OG1)
# CL0 A 801 O2D ··· TYR A 596 OH = 3.08 Å (polar candidate)
distance d04_polar, scene and (chain A and resi 801 and resn CL0 and name O2D), scene and (chain A and resi 596 and resn TYR and name OH)
# CL0 A 801 O2D ··· THR A 736 OG1 = 3.33 Å (polar candidate)
distance d05_polar, scene and (chain A and resi 801 and resn CL0 and name O2D), scene and (chain A and resi 736 and resn THR and name OG1)
# HOH A 1002 O ··· THR A 736 OG1 = 2.68 Å (water polar candidate)
distance d06_water, scene and (chain A and resi 1002 and resn HOH and name O), scene and (chain A and resi 736 and resn THR and name OG1)
# HOH A 1002 O ··· TYR A 596 OH = 2.81 Å (water polar candidate)
distance d07_water, scene and (chain A and resi 1002 and resn HOH and name O), scene and (chain A and resi 596 and resn TYR and name OH)
# HOH A 1002 O ··· SER A 600 OG = 3.10 Å (water polar candidate)
distance d08_water, scene and (chain A and resi 1002 and resn HOH and name O), scene and (chain A and resi 600 and resn SER and name OG)
# CL0 A 801 O2D ··· HOH A 1002 O = 3.19 Å (water polar candidate)
distance d09_water, scene and (chain A and resi 801 and resn CL0 and name O2D), scene and (chain A and resi 1002 and resn HOH and name O)
# HOH A 1002 O ··· GLY A 732 O = 3.25 Å (water polar candidate)
distance d10_water, scene and (chain A and resi 1002 and resn HOH and name O), scene and (chain A and resi 732 and resn GLY and name O)
# CL0 A 801 OBD ··· CL0 A 801 O2D = 3.68 Å (intramolecular)
distance d11_intra, scene and (chain A and resi 801 and resn CL0 and name OBD), scene and (chain A and resi 801 and resn CL0 and name O2D)
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
group water_polar_candidate, d06_water d07_water d08_water d09_water d10_water
set dash_color, cls_water, water_polar_candidate
set dash_length, 0.25, water_polar_candidate
set dash_gap, 0.18, water_polar_candidate
set_color cls_intra, [0.478, 0.322, 0.78]
group intramolecular, d11_intra
set dash_color, cls_intra, intramolecular
set dash_length, 0.3, intramolecular
set dash_gap, 0.12, intramolecular

# --- labels (residues at the library anchor atoms, roles as plain text)
set label_font_id, 7
set label_size, 16
set float_labels, 1
label scene and (chain A and resi 596 and resn TYR and name CA), "Tyr596 A"
label scene and (chain A and resi 600 and resn SER and name CA), "Ser600 A"
label scene and (chain A and resi 673 and resn HIS and name CA), "His673 A"
label scene and (chain A and resi 728 and resn TYR and name CA), "Tyr728 A"
label scene and (chain A and resi 732 and resn GLY and name CA), "Gly732 A"
label scene and (chain A and resi 736 and resn THR and name CA), "Thr736 A"
label scene and (chain A and resi 801 and resn CL0 and name MG), "PA"
label scene and (chain A and resi 1002 and resn HOH and name O), "HOH1002 A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (-0.115991, 0.193799, 0.974160, 0.391649, 0.910238, -0.134450, -0.912774, 0.365934, -0.181481, 0.000000, 3.462895, -127.180267, 106.176109, 105.747366, 97.297909, 107.713722, 146.646805, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
