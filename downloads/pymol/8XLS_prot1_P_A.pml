# PSI Contact Atlas — 8XLS protomer 1, P_A network
# Thalassiosira pseudonana CCMP1335 · Diatom, PSI-5 FCPI · Cryo-EM 2.3 Å
#
# Run from the repository root:   pymol downloads/pymol/8XLS_prot1_P_A.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/8XLS_prot1_P_A.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 8XLS, scene, type=cif
select lib_atoms, scene and ((chain A and resi 600+604+677+680+732+736+740+801+955))

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
# CL0 A 801 MG ··· HIS A 677 NE2 = 2.45 Å (Mg ligand)
distance d01_mg, scene and (chain A and resi 801 and resn CL0 and name MG), scene and (chain A and resi 677 and resn HIS and name NE2)
# CL0 A 801 O1A ··· TYR A 732 OH = 2.65 Å (polar candidate)
distance d02_polar, scene and (chain A and resi 801 and resn CL0 and name O1A), scene and (chain A and resi 732 and resn TYR and name OH)
# CL0 A 801 OBD ··· THR A 740 OG1 = 2.93 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 801 and resn CL0 and name OBD), scene and (chain A and resi 740 and resn THR and name OG1)
# CL0 A 801 O2D ··· TYR A 600 OH = 3.25 Å (polar candidate)
distance d04_polar, scene and (chain A and resi 801 and resn CL0 and name O2D), scene and (chain A and resi 600 and resn TYR and name OH)
# CL0 A 801 O2D ··· THR A 740 OG1 = 3.26 Å (polar candidate)
distance d05_polar, scene and (chain A and resi 801 and resn CL0 and name O2D), scene and (chain A and resi 740 and resn THR and name OG1)
# CL0 A 801 O2A ··· TYR A 600 OH = 3.34 Å (polar candidate)
distance d06_polar, scene and (chain A and resi 801 and resn CL0 and name O2A), scene and (chain A and resi 600 and resn TYR and name OH)
# CL0 A 801 O1A ··· TRP A 680 NE1 = 3.47 Å (polar candidate)
distance d07_polar, scene and (chain A and resi 801 and resn CL0 and name O1A), scene and (chain A and resi 680 and resn TRP and name NE1)
# HOH A 955 O ··· THR A 740 OG1 = 2.60 Å (water polar candidate)
distance d08_water, scene and (chain A and resi 955 and resn HOH and name O), scene and (chain A and resi 740 and resn THR and name OG1)
# HOH A 955 O ··· SER A 604 OG = 2.99 Å (water polar candidate)
distance d09_water, scene and (chain A and resi 955 and resn HOH and name O), scene and (chain A and resi 604 and resn SER and name OG)
# HOH A 955 O ··· TYR A 600 OH = 3.42 Å (water polar candidate)
distance d10_water, scene and (chain A and resi 955 and resn HOH and name O), scene and (chain A and resi 600 and resn TYR and name OH)
# HOH A 955 O ··· GLY A 736 O = 3.48 Å (water polar candidate)
distance d11_water, scene and (chain A and resi 955 and resn HOH and name O), scene and (chain A and resi 736 and resn GLY and name O)
# CL0 A 801 O2D ··· HOH A 955 O = 3.52 Å (longer context)
distance d12_context, scene and (chain A and resi 801 and resn CL0 and name O2D), scene and (chain A and resi 955 and resn HOH and name O)
# CL0 A 801 OBD ··· CL0 A 801 O2D = 3.60 Å (intramolecular)
distance d13_intra, scene and (chain A and resi 801 and resn CL0 and name OBD), scene and (chain A and resi 801 and resn CL0 and name O2D)
set_color cls_mg, [0.09, 0.541, 0.235]
group Mg_ligand, d01_mg
set dash_color, cls_mg, Mg_ligand
set dash_length, 0.3, Mg_ligand
set dash_gap, 0.0, Mg_ligand
set_color cls_polar, [0.114, 0.165, 0.227]
group polar_candidate, d02_polar d03_polar d04_polar d05_polar d06_polar d07_polar
set dash_color, cls_polar, polar_candidate
set dash_length, 0.25, polar_candidate
set dash_gap, 0.18, polar_candidate
set_color cls_water, [0.043, 0.498, 0.612]
group water_polar_candidate, d08_water d09_water d10_water d11_water
set dash_color, cls_water, water_polar_candidate
set dash_length, 0.25, water_polar_candidate
set dash_gap, 0.18, water_polar_candidate
set_color cls_context, [0.541, 0.573, 0.612]
group longer_context, d12_context
set dash_color, cls_context, longer_context
set dash_length, 0.08, longer_context
set dash_gap, 0.3, longer_context
set_color cls_intra, [0.478, 0.322, 0.78]
group intramolecular, d13_intra
set dash_color, cls_intra, intramolecular
set dash_length, 0.3, intramolecular
set dash_gap, 0.12, intramolecular

# --- labels (residues at the library anchor atoms, roles as plain text)
set label_font_id, 7
set label_size, 16
set float_labels, 1
label scene and (chain A and resi 600 and resn TYR and name CA), "Tyr600 A"
label scene and (chain A and resi 604 and resn SER and name CA), "Ser604 A"
label scene and (chain A and resi 677 and resn HIS and name CA), "His677 A"
label scene and (chain A and resi 732 and resn TYR and name CA), "Tyr732 A"
label scene and (chain A and resi 736 and resn GLY and name CA), "Gly736 A"
label scene and (chain A and resi 740 and resn THR and name CA), "Thr740 A"
label scene and (chain A and resi 801 and resn CL0 and name MG), "PA"
label scene and (chain A and resi 955 and resn HOH and name O), "HOH955 A"
label scene and (chain A and resi 680 and resn TRP and name NE1), "Trp680 A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (0.322369, -0.946556, -0.010446, -0.940371, -0.321489, 0.111117, -0.108537, -0.025998, -0.993752, 0.000000, 3.462895, -127.180267, 114.413544, 78.156593, 105.305098, 107.713722, 146.646805, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
