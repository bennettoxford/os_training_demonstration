# What does post release mean?

Within OpenSAFELY, most work exists *inside* the OS pipeline - where each stage will run on the jobs server - or will be contributing to the development of that pipeline, e.g., a folder for dummy data.

However, the best practice approach to handling the results of this pipeline is to request the release of results as early into the pipeline as possible. Once the results are safe to release - aggregated, un-identifiable, and statistical disclosure control has been performed - the results should be requested for release. They then enter a *post release* stage.

# What happens post release?

The most common stage for release is before visualisation has been performed, this allows researchers to spend time changing the way the want to visualise their results - with data that has already been checked for disclosivity. 

In this folder, we have some scripts which can be used to visualise results after they have been released, these scripts are not run within the OpenSAFELY Command Line Interface (CLI). 