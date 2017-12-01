---
title: mdshare • alanine dipeptide
layout: default
permalink: /ALA2/
---

# Alanine dipeptide

| Property | Value |
|:---------|------:|
| Code | ACEMD |
| Forcefield | AMBER ff-99SB-ILDN |
| Integrator | Langevin |
| Integrator time step | 2 fs |
| Simulation time | 250 ns |
| Frame spacing | 1 ps |
| Temperature | 300 K |
| Volume | (2.3222 nm)^3 periodic box |
| Solvation | 651 TIP3P waters |
| Electrostatics | PME |
| PME real-space cutoff | 0.9 nm |
| PME grid spacing | 0.1 nm |
| PME updates | every two time steps |
| Constraints | all bonds between hydrogens and heavy atoms |

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>

## Contents
### Featurized data
Each file contains three **numpy.ndarray(shape=[250000, n_features], dtype=numpy.float32)** objects (keys: **arr_0**, **arr_1**, **arr_2**) from three independent simulations.
-  [alanine-dipeptide-3x250ns-backbone-dihedrals.npz](http://ftp.imp.fu-berlin.de/pub/cmb-data/alanine-dipeptide-3x250ns-backbone-dihedrals.npz)
-  [alanine-dipeptide-3x250ns-heavy-atom-distances.npz](http://ftp.imp.fu-berlin.de/pub/cmb-data/alanine-dipeptide-3x250ns-heavy-atom-distances.npz)
-  [alanine-dipeptide-3x250ns-heavy-atom-positions.npz](http://ftp.imp.fu-berlin.de/pub/cmb-data/alanine-dipeptide-3x250ns-heavy-atom-positions.npz)

## Citations
-  F. N&uuml;ske, *et al*: [Markov State Models from short non-Equilibrium Simulations - Analysis and Correction of Estimation Bias](http://arxiv.org/abs/1701.01665), *J. Chem. Phys.* **146** (2017), 094104.
-  C. Wehmeyer and F. No&eacute;: [Time-lagged autoencoders: Deep learning of slow collective variables for molecular kinetics](https://arxiv.org/abs/1710.11239) (2017), arXiv:1710.11239 [stat.ML]

<div style="text-align: right"><a href="../">back</a></div>
