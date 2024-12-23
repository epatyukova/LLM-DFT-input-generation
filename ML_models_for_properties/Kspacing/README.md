# Models to predict Kspacing from composition

Here some models for predicting kspacing from composition are collected. At the moment kspacing data are taken from Jarvis 3d_dft dataset.

## Random Forrest
<p align="center">
  <img src="figures/RF-composition.png" width="300"/>
</p>

R2=0.524, MAE=10.626

## CrabNet
<p align="center">
  <img src="figures/CrabNet-composition.png" width="300"/>
</p>

R2=0.500, MAE=10.534

## CrabNet transfer from formation energy per one atom

## CrabNet transfer from total energy per one atom

## CrabNet transfer from density

## Conclusion

All these models have approximately the same performance. And we would like to have something better.

Best trained models can be found in the goldilocks folder on sharepoint
