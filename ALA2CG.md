---
title: mdshare • alanine dipeptide coarse grained with forces
layout: default
permalink: /ALA2CG/
---

# Alanine dipeptide (coarse grained, with forces)

| Property | Value |
|:---------|------:|
| Code | OpenMM |
| Forcefield | AMBER ff-99SB-ILDN |
| Integrator | Langevin |
| Integrator time step | 2 fs |
| Simulation time | 4x500 ns |
| Frame spacing | 2 ps |
| Temperature | 300 K |
| Volume | (2.3222 nm)^3 periodic box |
| Solvation | 651 TIP3P waters |
| Electrostatics | PME |
| PME real-space cutoff | 0.9 nm |
| PME grid spacing | 0.1 nm |
| Constraints | all bonds between hydrogens and heavy atoms |

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>

## Contents
The molecule and system setup is essentially the same as in [the other alanine dipeptide dataset](../ALA2#alanine-dipeptide). The major difference is that we cropped out the five backbone atoms (ACE-C ALA-N ALA-CA ALA-C NME-N) and recorded the coordinates and forces of them. The dataset contains four independent simulations, each of which consists of 250,000 frames (500 ns sampled with a 2-ps interval).
Therefore, for cross-validation it is recommended to separate the data into four folds by indexing the arrays with **[250000 * i_fold:250000 * (i_fold + 1)]**.

### Raw data
Shared PDB topology file, coordinates (key **coords**) and forces (key **aaFs**) on the five backbone atoms from four independent simulations (four trajectories were concatenated together **numpy.ndarray(shape=[1000000, 5, 3], dtype=numpy.float32)**). The unit of coordinates is Angstrom (0.1 nm) and for the forces kcal/(mol&middot;Angstrom).
-  [ala2_cg.pdb](http://ftp.imp.fu-berlin.de/pub/cmb-data/ala2_cg.pdb)
-  [ala2_cg_2fs_Hmass_2_HBonds.npz](http://ftp.imp.fu-berlin.de/pub/cmb-data/ala2_cg_2fs_Hmass_2_HBonds.npz)

## Citations
This dataset was used in the following publication for the first time.
-  J. K&ouml;hler et al.: [Flow-Matching: Efficient Coarse-Graining of Molecular Dynamics without Forces](https://doi.org/10.1021/acs.jctc.3c00016), *J. Chem. Theory Comput.* **19** (2023), 942.

<div style="text-align: right"><a href="../">back</a></div>
