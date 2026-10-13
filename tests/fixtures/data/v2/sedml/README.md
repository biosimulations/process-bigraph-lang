# SED-ML corpus

Each folder holds the SED-ML, the model it references and the archive's `manifest.xml`, unzipped so diffs stay
readable; the tests zip a folder into an `.omex` when they need an archive. Figures, PDFs and other members are left
out.

- `BIOMD0000000012/`: the repressilator (Elowitz and Leibler 2000), from EBI BioModels
  (`https://www.ebi.ac.uk/biomodels/model/download/BIOMD0000000012`, fetched 2026-10-12; BioModels content is CC0).
  SED-ML L1V4: one uniform time course (`numberOfSteps`), the generic ODE solver term `KISAO:0000694`, a report of
  every species, parameter, compartment and reaction, one plot.
- `Ciliberto2003/`: the morphogenesis checkpoint model (BIOMD0000000297) as the biosimulations.org project
  `Morphogenesis-checkpoint-continuous-Ciliberto-J-Cell-Biol-2003` (run `61fea4948edd56f301e6a7fc`, fetched
  2026-10-12). SED-ML L1V3: an attribute change, CVODE (`KISAO:0000019`), `numberOfPoints`, a data generator that sums
  four species, four plots.
- `out_of_scope.sedml`: written for the tests; every feature version 1 does not translate, once.
