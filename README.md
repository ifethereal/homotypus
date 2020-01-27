# Homotypus
This repository contains the source code for the Homotypus blog.

## Setup
* Miniconda 4.8.1 w/ Python 2.7[.17] (see the [spec file][conda] for
  environment)
* Python packages (`pip` will take care of dependencies; see the
  [spec file][pip] for details)
  * Pelican 4.2.0
  * Markdown 3.1.1
* [Sass][sass] (Dart Sass 1.25.0 works)

[conda]: spec/conda.txt
[pip]: spec/pip.txt
[sass]: https://sass-lang.com/install
    "Download page for Sass"

## Instructions
Once the conda environment is set up and activated, navigate to the root of the
repository and run
```
make fresh
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
