<img width="3840" height="2120" alt="image" src="https://github.com/user-attachments/assets/d5bd2fd2-d9da-407c-a367-bb977becf03d" />

# InnovaPower: Project MitDev-Eletrica

Here are all the deliverables from the project "Enhancement of wind power potential through the study and mitigation of generation deviations and failures" (MitDev) developed by the Power Systems Innovation Hub (InnovaPower) of the University of São Paulo (USP).

## Datasets

Currently, the repository has three datasets of generators operating under short-circuit conditions and for different operating points:

- [**Generators-Dataset**](https://github.com/InnovaPower/MitDev-Eletrica/tree/master/Generators-Dataset): Rafael Noboro Tominaga, et al., Electrical signals dataset from fixed-speed and variable-speed synchronous generators under healthy and faulty conditions, Data Brief. 57 (2024) 111018. https://doi.org/doi:10.1016/j.dib.2024.111018.

- [**PMSG-3phase-Dataset**](https://github.com/InnovaPower/MitDev-Eletrica/tree/master/PMSG-3phase-Dataset): Rafael Noboro Tominaga, et al., A benchmark dataset of electrical signals from a permanent magnet synchronous generator for condition monitoring, Data in Brief. 62 (2025) 112040. https://doi.org/10.1016/j.dib.2025.112040.

- [**SCIG-3phase-Dataset**](https://github.com/InnovaPower/MitDev-Eletrica/tree/master/SCIG-3phase-Dataset): Rafael Noboro Tominaga, et al., A condition monitoring dataset based on electrical signals for a squirrel cage induction generator, Data in Brief. In Review.

The short-circuits in the generators were performed in a controlled environment using experimental benches designed for this purpose.

### Features

The dataset includes the following key measurements:

- Time reference, with fixed sampling intervals.
- Generator currents and voltages, measured via dedicated transducers for each generator.
- Fault current, very useful for short-circuit analysis.
- Mechanical measurements, such as rotor speed and torque.
- Control variables, available in setups with converters.

## Acknowledgments

We gratefully acknowledge the support of the RCGI – Research Centre for Greenhouse Gas Innovation (23.1.8493.1.9), hosted by the University of São Paulo (USP) and sponsored by FAPESP – São Paulo Research Foundation (2020/15230-5), and sponsored by TotalEnergies, and the strategic importance of the support given by ANP (Brazil’s National Oil, Natural Gas and Biofuels Agency) through the R&DI levy regulation.

## Licence

[![License: CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

All datasets are licensed under CC-BY-4.0 license.
