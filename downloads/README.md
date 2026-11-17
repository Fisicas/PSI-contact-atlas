# Downloads: file and column guide

All distances are in ångström (Å), computed between deposited heavy-atom coordinates at full precision and written with five (contact tables) or four (comparison tables) decimals. That is computational precision, not experimental accuracy; the site shows 0.01 Å. Hydrogens, protonation states and angles are not modelled, so no row is a confirmed hydrogen bond.

**Atom identifiers** have the form `COMP:chain:residue:atom` with the deposited component name and **author** chain and residue numbering (as PyMOL reads mmCIF by default). Chain IDs are case-sensitive (`A` and `a` are different chains); an insertion code, if any, follows the residue number. Example: `PQN:A:2001:O4`. Only model 1 is used; where an atom has alternate locations the highest-occupancy position is used (none of the scene atoms has one).

## Which file to use

| File | One row per | Use it to |
|---|---|---|
| `tables/atlas_unique_contacts.csv` | physical atom pair (691) | count or cite observations |
| `tables/atlas_table_<environment>.csv` | homologous contact × protomer | compare one contact across entries (`PA_network`, `special_pair`, `A1A`, `A1B`) |
| `compare_matrix.csv` | the four environment tables together | the same, in one file |
| `all_contacts.csv`, `contacts/<scene>_contacts.csv` | atom pair as shown in a scene (865 rows) | reproduce what a scene shows |

## Contact tables (`all_contacts.csv`, `contacts/`, `tables/atlas_unique_contacts.csv`)

| Column | Meaning |
|---|---|
| `contact_id` | Stable ID of the physical pair: `<PDB>.p<protomer>.<atom>~<atom>` with the two atoms in sorted order. The same pair shown in two scenes has one ID. |
| `view` / `scenes` | Scene name(s), `<PDB>_prot<n>_<environment>`. |
| `pdb`, `protomer`, `part` | PDB entry, protomer number and environment (`special_pair`, `P_A`, `A1A`, `A1B`). |
| `atom_1`, `atom_2` | The two atoms (format above). |
| `label_asym_1`, `label_asym_2` | mmCIF `label_asym_id` of each atom. |
| `distance_A` | Separation in Å. |
| `contact_class` | One of the classes below. |
| `chemical_basis` | What the two atom types allow: `donor–acceptor compatible`, `acceptor–acceptor; neither atom carries a hydrogen`, `water-involved; water can donate or accept`, `unresolved; depends on protonation state or tautomer` (His N, Asp/Glu O), or the class restated for Mg, same-residue, beyond-screen and C/S pairs. Not a hydrogen-bond assignment. |
| `curated_annotation` | Free-text annotation from the earlier curated build, kept for traceability; `derived by homology` for rule-derived scenes. |
| `occupancy_1`, `occupancy_2`, `B_iso_1`, `B_iso_2` | Deposited occupancy and isotropic B-factor (Å²). Context only; they are not distance error bars. |

### Contact classes

Assigned by one rule, in this order: Mg involved → `mg`; same residue → `intra`; C or S involved → `cs_contact`; more than 3.5 Å → `context`; water involved → `water`; both atoms are oxygens that cannot carry a hydrogen (any cofactor oxygen; a backbone or Asn/Gln amide C=O) → `acceptor_pair`; otherwise → `polar`. Carboxylate O and His N stay `polar` because their protonation state is not known; the `chemical_basis` column says so.

| Class | Meaning | Scene rows | Unique pairs |
|---|---|---|---|
| `mg` | Mg–ligand atom separation (coordination geometry not assessed) | 95 | 64 |
| `polar` | Polar heavy-atom candidate (N/O···N/O ≤ 3.5 Å; see chemical basis) | 465 | 348 |
| `water` | Water-involved polar candidate (≤ 3.5 Å) | 156 | 131 |
| `acceptor_pair` | Two oxygen acceptors (carbonyl, ester or backbone C=O) ≤ 3.5 Å; neither carries a hydrogen, so not a hydrogen-bond candidate | 51 | 51 |
| `context` | Longer polar context (> 3.5 Å) | 51 | 50 |
| `intra` | Intramolecular separation | 32 | 32 |
| `cs_contact` | Separation involving carbon or sulfur; element-based only, not evidence of an attractive interaction | 15 | 15 |

## Comparison tables (`compare_matrix.csv`, `tables/atlas_table_*.csv`)

| Column | Meaning |
|---|---|
| `comparison_id` | Stable ID of the homologous contact, e.g. `A1A.A1_A.carbonyl_O~PsaA688.O`. Cite a value as `comparison_id` + `pdb` + `protomer`. |
| `part`, `cofactor_role`, `cofactor_atom` | Environment, functional role (`P_A`, `P_B`, `A1_A`, `A1_B`, or `site water`) and atom. For the quinones, `carbonyl O` is the shorter separation from either carbonyl oxygen; the native atom used is in `atom_1`. |
| `partner_subunit`, `1JB0_position`, `1JB0_residue`, `partner_atom` | Partner in 1JB0 numbering (`hydroxyl O` = Ser OG / Thr OG1 / Tyr OH; `O` = backbone C=O oxygen; `N` = backbone N–H). |
| `pdb`, `protomer`, `native_partner` | Entry, protomer and the partner residue as deposited (`Tyr599.1` = Tyr599 in chain 1). |
| `atom_1`, `atom_2`, `distance_A` | The deposited atoms used and their separation. |
| `missing_reason` | Why a cell is empty: residue differs, atom not modelled, position not aligned, or no deposited water meets the site rule. Blank when a distance is given. |

## Other files

- `cif/<scene>.cif` — mmCIF crop of each scene with deposited names, numbering, chains and coordinates.
- `pymol/<scene>.pml` — PyMOL script that loads the crop and draws every measured pair, grouped by class.
