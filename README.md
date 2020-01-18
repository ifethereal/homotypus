# Homotypus
This repository contains the source code for the Homotypus blog.

## Setup
* Miniconda 4.8.1 w/ Python 2.7[.17] (see the [spec file][conda] for
  environment)
* Python packages (`pip` will take care of dependencies; see the
  [spec file][pip] for details)
  * Pelican 4.2.0
  * Markdown 3.1.1

[conda]: spec/conda.txt
[pip]: spec/pip.txt

## Instructions
Once the conda environment environment is set up and activated, navigate to the
root of the repository and run
```
make html
make serve
```

The site should then be viewable at http://localhost:8000/.
