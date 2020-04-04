# Homotypus
This repository contains the source code for the Homotypus blog.

## Setup
* [Miniconda][miniconda] 4.7.12.1 w/ Python 3.8\[.2\] (see the
  [spec file][conda] for environment)
* Python packages (`pip` will take care of dependencies; see the
  [spec file][pip] for details)
  * Pelican 4.2.0
  * Markdown 3.1.1
* [Sass][sass] (Dart Sass 1.25.0 works)

The setup could be done as follows:
1. Install Miniconda.
2. Start a conda prompt.
3. Navigate to the root of the repository.
4. Run the following commands in a conda prompt:
   ```
   conda create --name homotypus --file spec\conda.txt
   conda activate homotypus
   pip install --requirement spec\pip.txt
   ```
   This creates a conda environment `homotypus` with the right packages
   installed.
5. Install Sass.

[miniconda]: https://docs.conda.io/en/latest/miniconda.html
    "Download page for Miniconda"
[conda]: spec/conda.txt
[pip]: spec/pip.txt
[sass]: https://sass-lang.com/install
    "Download page for Sass"

## Instructions
Once the conda environment is set up and activated, navigate to the root of the
repository and run
```
python build.py site
python build.py serve
```

The site will open up at http://localhost:8000/.

## Notes
The file [`homotypus.scss`][scss] is heavily based on the themes [Poole][poole]
and [Lanyon][lanyon] for Jekyll.

[scss]: extra/homotypus.scss
[poole]: https://github.com/poole/poole
    "The Poole GitHub repository"
[lanyon]: https://github.com/poole/lanyon
    "The Lanyon GitHub repository"
