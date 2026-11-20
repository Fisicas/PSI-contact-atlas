# PSI Contact Atlas — 9KZ9 protomer 1, A1_B quinone
# Rhodomonas sp. NIES-2332 · Cryptophyte, PSI-14 ACPI · Cryo-EM 2.08 Å
#
# Run from the repository root:   pymol downloads/pymol/9KZ9_prot1_A1B.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/9KZ9_prot1_A1B.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 9KZ9, scene, type=cif
select lib_atoms, scene and ((chain B and resi 661+662+665+670+698+699+843))

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
set_bond stick_radius, 0.16, scene and ((chain B and resi 843 and resn PQN))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# PQN B 843 O4 ··· LEU B 699 N = 2.87 Å (polar candidate)
distance d01_polar, scene and (chain B and resi 843 and resn PQN and name O4), scene and (chain B and resi 699 and resn LEU and name N)
# PQN B 843 O1 ··· SER B 665 OG = 2.91 Å (polar candidate)
distance d02_polar, scene and (chain B and resi 843 and resn PQN and name O1), scene and (chain B and resi 665 and resn SER and name OG)
# PQN B 843 O1 ··· TRP B 670 NE1 = 3.29 Å (polar candidate)
distance d03_polar, scene and (chain B and resi 843 and resn PQN and name O1), scene and (chain B and resi 670 and resn TRP and name NE1)
# PQN B 843 O1 ··· MET B 661 O = 2.92 Å (O···O, no H donor)
distance d04_acceptor_pair, scene and (chain B and resi 843 and resn PQN and name O1), scene and (chain B and resi 661 and resn MET and name O)
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
label scene and (chain B and resi 661 and resn MET and name CA), "Met661 B"
label scene and (chain B and resi 662 and resn PHE and name CA), "Phe662 B"
label scene and (chain B and resi 665 and resn SER and name CA), "Ser665 B"
label scene and (chain B and resi 670 and resn TRP and name CA), "Trp670 B"
label scene and (chain B and resi 698 and resn ALA and name CA), "Ala698 B"
label scene and (chain B and resi 699 and resn LEU and name CA), "Leu699 B"
label scene and (chain B and resi 843 and resn PQN and name C1), "A1B"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (0.281467, -0.956091, -0.081641, -0.724619, -0.156004, -0.671260, 0.629049, 0.248096, -0.736713, 0.000000, -1.036330, -67.423325, 209.522902, 229.458781, 242.599712, 45.684242, 89.162399, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
