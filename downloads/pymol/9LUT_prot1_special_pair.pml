# PSI Contact Atlas — 9LUT protomer 1, special pair
# Marchantia polymorpha · Liverwort, PSI-LHCI monomer · Cryo-EM 1.94 Å
#
# Run from the repository root:   pymol downloads/pymol/9LUT_prot1_special_pair.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/9LUT_prot1_special_pair.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 9LUT, scene, type=cif
select lib_atoms, scene and ((chain A and resi 598+602+606+675+730+734+738+741+802+938) or (chain B and resi 592+654+657+717+720+721+724+803))

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
set_bond stick_radius, 0.16, scene and ((chain A and resi 802 and resn CL0) or (chain B and resi 803 and resn CLA))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# CL0 A 802 MG ··· HIS A 675 NE2 = 2.01 Å (Mg ligand)
distance d01_mg, scene and (chain A and resi 802 and resn CL0 and name MG), scene and (chain A and resi 675 and resn HIS and name NE2)
# CLA B 803 MG ··· HIS B 654 NE2 = 2.06 Å (Mg ligand)
distance d02_mg, scene and (chain B and resi 803 and resn CLA and name MG), scene and (chain B and resi 654 and resn HIS and name NE2)
# CL0 A 802 O1A ··· TYR A 730 OH = 2.93 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 802 and resn CL0 and name O1A), scene and (chain A and resi 730 and resn TYR and name OH)
# CL0 A 802 OBD ··· THR A 738 OG1 = 3.03 Å (polar candidate)
distance d04_polar, scene and (chain A and resi 802 and resn CL0 and name OBD), scene and (chain A and resi 738 and resn THR and name OG1)
# CLA B 803 O1D ··· TYR B 721 N = 3.08 Å (polar candidate)
distance d05_polar, scene and (chain B and resi 803 and resn CLA and name O1D), scene and (chain B and resi 721 and resn TYR and name N)
# CL0 A 802 O2D ··· TYR A 598 OH = 3.18 Å (polar candidate)
distance d06_polar, scene and (chain A and resi 802 and resn CL0 and name O2D), scene and (chain A and resi 598 and resn TYR and name OH)
# CL0 A 802 O2D ··· THR A 738 OG1 = 3.34 Å (polar candidate)
distance d07_polar, scene and (chain A and resi 802 and resn CL0 and name O2D), scene and (chain A and resi 738 and resn THR and name OG1)
# CL0 A 802 O2D ··· HOH A 938 O = 3.53 Å (longer context)
distance d08_context, scene and (chain A and resi 802 and resn CL0 and name O2D), scene and (chain A and resi 938 and resn HOH and name O)
# CLA B 803 O2A ··· TYR B 717 OH = 3.75 Å (longer context)
distance d09_context, scene and (chain B and resi 803 and resn CLA and name O2A), scene and (chain B and resi 717 and resn TYR and name OH)
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
set_color cls_context, [0.541, 0.573, 0.612]
group longer_context, d08_context d09_context
set dash_color, cls_context, longer_context
set dash_length, 0.08, longer_context
set dash_gap, 0.3, longer_context

# --- labels (residues at the library anchor atoms, roles as plain text)
set label_font_id, 7
set label_size, 16
set float_labels, 1
label scene and (chain A and resi 598 and resn TYR and name CA), "Tyr598 A"
label scene and (chain A and resi 602 and resn SER and name CA), "Ser602 A"
label scene and (chain A and resi 606 and resn PHE and name CA), "Phe606 A"
label scene and (chain A and resi 675 and resn HIS and name CA), "His675 A"
label scene and (chain A and resi 730 and resn TYR and name CA), "Tyr730 A"
label scene and (chain A and resi 734 and resn GLY and name CA), "Gly734 A"
label scene and (chain A and resi 738 and resn THR and name CA), "Thr738 A"
label scene and (chain A and resi 741 and resn PHE and name CA), "Phe741 A"
label scene and (chain A and resi 802 and resn CL0 and name MG), "PA"
label scene and (chain B and resi 592 and resn PHE and name CA), "Phe592 B"
label scene and (chain B and resi 654 and resn HIS and name CA), "His654 B"
label scene and (chain B and resi 657 and resn TRP and name CA), "Trp657 B"
label scene and (chain B and resi 717 and resn TYR and name CA), "Tyr717 B"
label scene and (chain B and resi 720 and resn THR and name CA), "Thr720 B"
label scene and (chain B and resi 721 and resn TYR and name CA), "Tyr721 B"
label scene and (chain B and resi 724 and resn PHE and name CA), "Phe724 B"
label scene and (chain B and resi 803 and resn CLA and name MG), "PB"
label scene and (chain A and resi 938 and resn HOH and name O), "HOH938 A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (0.994895, 0.098863, -0.020226, -0.028094, 0.078857, -0.996490, -0.096921, 0.991971, 0.081232, 0.000000, -2.058625, -124.535011, 195.898466, 168.881008, 180.249998, 105.042145, 144.027878, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
