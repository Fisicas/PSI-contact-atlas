# PSI Contact Atlas — 9UH3 protomer 1, P_A network
# Chrysotila roscoffensis · Haptophyte, PSI-9 FCPI · Cryo-EM 1.74 Å
#
# Run from the repository root:   pymol downloads/pymol/9UH3_prot1_P_A.pml
# Distances are Euclidean heavy-atom separations (Å). Short N/O···O pairs are hydrogen-bond CANDIDATES:
# hydrogens, protonation and angles are not modelled. Pairs in group OO_no_H_donor are two oxygen
# acceptors (neither carries a hydrogen), so they are not hydrogen-bond candidates.
# Chain IDs are case-sensitive author IDs.

reinitialize
# chain IDs such as 'a' and 'A' are different chains. Use author chain/residue numbering as the library does.
set ignore_case, 0
set cif_use_auth, 1
load downloads/cif/9UH3_prot1_P_A.cif, scene
# To start from the full deposited entry instead, replace the line above with:
#   fetch 9UH3, scene, type=cif
select lib_atoms, scene and ((chain A and resi 589+593+666+721+725+729+849+961))

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
set_bond stick_radius, 0.16, scene and ((chain A and resi 849 and resn CL0))

# --- measured pairs (the comment above each line gives the library value, PyMOL recomputes it)
set dash_radius, 0.035
set label_distance_digits, 2
set label_size, 18
set label_color, black
# CL0 A 849 MG ··· HIS A 666 NE2 = 2.12 Å (Mg ligand)
distance d01_mg, scene and (chain A and resi 849 and resn CL0 and name MG), scene and (chain A and resi 666 and resn HIS and name NE2)
# CL0 A 849 O1A ··· TYR A 721 OH = 2.75 Å (polar candidate)
distance d02_polar, scene and (chain A and resi 849 and resn CL0 and name O1A), scene and (chain A and resi 721 and resn TYR and name OH)
# CL0 A 849 OBD ··· THR A 729 OG1 = 2.92 Å (polar candidate)
distance d03_polar, scene and (chain A and resi 849 and resn CL0 and name OBD), scene and (chain A and resi 729 and resn THR and name OG1)
# CL0 A 849 O2D ··· THR A 729 OG1 = 3.30 Å (polar candidate)
distance d04_polar, scene and (chain A and resi 849 and resn CL0 and name O2D), scene and (chain A and resi 729 and resn THR and name OG1)
# CL0 A 849 O2D ··· TYR A 589 OH = 3.39 Å (polar candidate)
distance d05_polar, scene and (chain A and resi 849 and resn CL0 and name O2D), scene and (chain A and resi 589 and resn TYR and name OH)
# HOH A 961 O ··· THR A 729 OG1 = 2.75 Å (water polar candidate)
distance d06_water, scene and (chain A and resi 961 and resn HOH and name O), scene and (chain A and resi 729 and resn THR and name OG1)
# HOH A 961 O ··· SER A 593 OG = 2.83 Å (water polar candidate)
distance d07_water, scene and (chain A and resi 961 and resn HOH and name O), scene and (chain A and resi 593 and resn SER and name OG)
# HOH A 961 O ··· TYR A 589 OH = 3.23 Å (water polar candidate)
distance d08_water, scene and (chain A and resi 961 and resn HOH and name O), scene and (chain A and resi 589 and resn TYR and name OH)
# HOH A 961 O ··· GLY A 725 O = 3.27 Å (water polar candidate)
distance d09_water, scene and (chain A and resi 961 and resn HOH and name O), scene and (chain A and resi 725 and resn GLY and name O)
# CL0 A 849 O2D ··· HOH A 961 O = 3.29 Å (water polar candidate)
distance d10_water, scene and (chain A and resi 849 and resn CL0 and name O2D), scene and (chain A and resi 961 and resn HOH and name O)
# CL0 A 849 OBD ··· CL0 A 849 O2D = 3.65 Å (intramolecular)
distance d11_intra, scene and (chain A and resi 849 and resn CL0 and name OBD), scene and (chain A and resi 849 and resn CL0 and name O2D)
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
label scene and (chain A and resi 589 and resn TYR and name CA), "Tyr589 A"
label scene and (chain A and resi 593 and resn SER and name CA), "Ser593 A"
label scene and (chain A and resi 666 and resn HIS and name CA), "His666 A"
label scene and (chain A and resi 721 and resn TYR and name CA), "Tyr721 A"
label scene and (chain A and resi 725 and resn GLY and name CA), "Gly725 A"
label scene and (chain A and resi 729 and resn THR and name CA), "Thr729 A"
label scene and (chain A and resi 849 and resn CL0 and name MG), "PA"
label scene and (chain A and resi 961 and resn HOH and name O), "HOH961 A"

# --- the reviewed starting orientation used by the library (orthoscopic)
set_view (0.939112, 0.144181, 0.311898, 0.295942, 0.121860, -0.947401, -0.174605, 0.982019, 0.071771, 0.000000, 3.462895, -127.180267, 229.780350, 213.500555, 206.223911, 107.713722, 146.646805, 20.000000)
zoom lib_atoms, 2, complete=1
deselect
