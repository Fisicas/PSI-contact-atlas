# PSI Contact Atlas — 9HYU protomer 1, A1_B quinone
# Chromera velia · Alveolate, PSI-FCP with SOD heterodimer · Cryo-EM 1.84 Å
#
# Run from the repository root:   pymol downloads/pymol/9HYU_prot1_A1B.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/9HYU_prot1_A1B.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 9HYU, scene, type=cif
select lib_atoms, scene and ((chain B and resi 1070+1071+1074+1079+1107+1108+1232))

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
set_bond stick_radius, 0.16, scene and ((chain B and resi 1232 and resn PQN))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# PQN B 1232 O4 ··· LEU B 1108 N = 2.92 Å (polar candidate)
distance d01_polar, scene and (chain B and resi 1232 and resn PQN and name O4), scene and (chain B and resi 1108 and resn LEU and name N)
# PQN B 1232 O1 ··· TRP B 1079 NE1 = 3.32 Å (polar candidate)
distance d02_polar, scene and (chain B and resi 1232 and resn PQN and name O1), scene and (chain B and resi 1079 and resn TRP and name NE1)
# PQN B 1232 O1 ··· SER B 1074 OG = 3.39 Å (polar candidate)
distance d03_polar, scene and (chain B and resi 1232 and resn PQN and name O1), scene and (chain B and resi 1074 and resn SER and name OG)
# PQN B 1232 O1 ··· MET B 1070 O = 3.39 Å (O···O, no H donor)
distance d04_acceptor_pair, scene and (chain B and resi 1232 and resn PQN and name O1), scene and (chain B and resi 1070 and resn MET and name O)
set_color cls_polar, [0.114, 0.165, 0.227]
group polar_candidate, d01_polar d02_polar d03_polar
set dash_color, cls_polar, polar_candidate
set dash_length, 0.25, polar_candidate
set dash_gap, 0.18, polar_candidate
set_color cls_acceptor_pair, [0.627, 0.322, 0.478]
group OO_no_H_donor, d04_acceptor_pair
set dash_color, cls_acceptor_pair, OO_no_H_donor
set dash_length, 0.12, OO_no_H_donor
set dash_gap, 0.12, OO_no_H_donor

# --- labels (residues at the library anchor atoms, roles as plain text)
set label_font_id, 7
set label_size, 16
set float_labels, 1
label scene and (chain B and resi 1070 and resn MET and name CA), "Met1070 B"
label scene and (chain B and resi 1071 and resn PHE and name CA), "Phe1071 B"
label scene and (chain B and resi 1074 and resn SER and name CA), "Ser1074 B"
label scene and (chain B and resi 1079 and resn TRP and name CA), "Trp1079 B"
label scene and (chain B and resi 1107 and resn ALA and name CA), "Ala1107 B"
label scene and (chain B and resi 1108 and resn LEU and name CA), "Leu1108 B"
label scene and (chain B and resi 1232 and resn PQN and name C1), "A1B"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (-0.049546, -0.961563, -0.270078, -0.430847, 0.264533, -0.862782, 0.901064, 0.073614, -0.427393, 0.000000, -1.036330, -67.423325, 183.951789, 195.868283, 177.051579, 45.684242, 89.162399, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
