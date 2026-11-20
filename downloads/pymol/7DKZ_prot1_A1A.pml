# PSI Contact Atlas — 7DKZ protomer 1, A1_A quinone
# Pisum sativum (pea) · Flowering plant, PSI-LHCI, X-ray · X-ray crystallography 2.3930 Å
#
# Run from the repository root:   pymol downloads/pymol/7DKZ_prot1_A1A.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/7DKZ_prot1_A1A.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 7DKZ, scene, type=cif
select lib_atoms, scene and ((chain A and resi 691+692+695+700+724+725+842))

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
set_bond stick_radius, 0.16, scene and ((chain A and resi 842 and resn PQN))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# PQN A 842 O4 ··· LEU A 725 N = 2.86 Å (polar candidate)
distance d01_polar, scene and (chain A and resi 842 and resn PQN and name O4), scene and (chain A and resi 725 and resn LEU and name N)
# PQN A 842 O1 ··· TRP A 700 NE1 = 3.00 Å (polar candidate)
distance d02_polar, scene and (chain A and resi 842 and resn PQN and name O1), scene and (chain A and resi 700 and resn TRP and name NE1)
# PQN A 842 O1 ··· SER A 695 OG = 3.05 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 842 and resn PQN and name O1), scene and (chain A and resi 695 and resn SER and name OG)
# PQN A 842 O1 ··· MET A 691 O = 3.10 Å (O···O, no H donor)
distance d04_acceptor_pair, scene and (chain A and resi 842 and resn PQN and name O1), scene and (chain A and resi 691 and resn MET and name O)
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
label scene and (chain A and resi 691 and resn MET and name CA), "Met691 A"
label scene and (chain A and resi 692 and resn PHE and name CA), "Phe692 A"
label scene and (chain A and resi 695 and resn SER and name CA), "Ser695 A"
label scene and (chain A and resi 700 and resn TRP and name CA), "Trp700 A"
label scene and (chain A and resi 724 and resn ALA and name CA), "Ala724 A"
label scene and (chain A and resi 725 and resn LEU and name CA), "Leu725 A"
label scene and (chain A and resi 842 and resn PQN and name C1), "A1A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (-0.369005, 0.928911, -0.030967, 0.328790, 0.161629, 0.930469, 0.869329, 0.333167, -0.365059, 0.000000, -2.016743, -84.298332, 40.836700, 62.014554, 28.628651, 58.369720, 110.226944, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
