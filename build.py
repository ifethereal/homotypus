################################################################################
#     __  __                      __
#    / / / /___  ____ ___  ____  / /___  ______  __  _______
#   / /_/ / __ \/ __ `__ \/ __ \/ __/ / / / __ \/ / / / ___/
#  / __  / /_/ / / / / / / /_/ / /_/ /_/ / /_/ / /_/ (__  )
# /_/ /_/\____/_/ /_/ /_/\____/\__/\__, / .___/\__,_/____/
#                                 /____/_/
#
# Build script
#
# This script automates some of the common procedures when developing, including
# asking Pelican to generate the .html files, asking Sass to generate the .css
# file, serving the website locally etc.
################################################################################

import sys
import logging
import os
import os.path as op
import subprocess as sp

# CONSTANTS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PROJECT_NAME = "Homotypus"
LOGGER_NAME = "Bob"
FP_PELICAN_SETUP = "settings.py"
CMD_PELICAN = "pelican"

class ArgName:
    pass

class SubCmd:
    _SUBCMD = "subcommand"

    SITE = "site"
    HTML = "html"
    CSS = "css"
    CLEAN = "clean"

class PelicanArgLabel:
    INPUT = "Content directory"
    OUTPUT = "Output directory"
    SETTINGS = "Settings file"

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# LOGGER SUPPORT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def create_logger(name = LOGGER_NAME):
    archivist = logging.getLogger(name)
    archivist.setLevel(logging.DEBUG)

    # Set up logging to terminal
    terminal = logging.StreamHandler(sys.stdout)
    terminal.setLevel(logging.INFO)
    archivist.addHandler(terminal)

    # Want the timestamp to be formatted like 'Thu 28 Mar 2019 13:23:28'
    strDateFmt = "%a %d %b %Y %H:%M:%S"
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)8s] %(message)s", strDateFmt
    )
    terminal.setFormatter(formatter)

    return archivist


def destroy_logger(name = LOGGER_NAME):
    archivist = logging.getLogger(name)
    for handler in archivist.handlers:
        handler.flush()
        handler.close()
        archivist.removeHandler(handler)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def create_cmd_line_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description = "A build script for developing the Homotypus website"
    )
    subparsers = parser.add_subparsers(
        description = "Different build modes", dest = SubCmd._SUBCMD
    )
    subparsers.required = True

    subparsers.add_parser(
        name = SubCmd.SITE, help = "Regenerate the HTML and CSS files"
    )
    subparsers.add_parser(
        name = SubCmd.HTML, help = "Regenerate the HTML files"
    )
    subparsers.add_parser(
        name = SubCmd.CSS, help = "Regenerate the CSS files"
    )
    subparsers.add_parser(
        name = SubCmd.CLEAN, help = "Regenerate the CSS files"
    )

    return parser


def get_input_dir():
    return "content"


def get_output_dir():
    return "output"


def build_pelican_paths(dpCur = os.getcwd()):
    fpSettings = op.abspath(op.join(dpCur, FP_PELICAN_SETUP))
    dpIn = op.abspath(op.join(dpCur, get_input_dir()))
    dpOut = op.abspath(op.join(dpCur, get_output_dir()))

    result = {
        PelicanArgLabel.INPUT: dpIn,
        PelicanArgLabel.OUTPUT: dpOut,
        PelicanArgLabel.SETTINGS: fpSettings
    }

    return result


def check_valid_dir_structure(dpCur = os.getcwd()):
    lstPassCheck = []
    lstFailMsg = []

    if not op.isdir(dpCur):
        raise ValueError("No such directory [{}] exists".format(dpCur))

    p = build_pelican_paths(dpCur)

    fpSettings = p[PelicanArgLabel.SETTINGS]
    lstPassCheck.append(op.isfile(fpSettings))
    lstFailMsg.append(
        "The expected Pelican settings file [{}] does not exist" \
        .format(dpCur, FP_PELICAN_SETUP)
    )

    dpIn = p[PelicanArgLabel.INPUT]
    lstPassCheck.append(op.isdir(dpIn))
    lstFailMsg.append(
        "The expected Pelican content directory [{}] does not exist" \
        .format(dpIn)
    )

    archivist = logging.getLogger(LOGGER_NAME)
    for (m, p) in zip(lstFailMsg, lstPassCheck):
        if not p:
            archivist.error(m)

    return all(lstPassCheck)


def check_valid_pelican():
    archivist = logging.getLogger(LOGGER_NAME)

    try:
        # Attempt to get the installed version number of Pelican
        strOut = sp.check_output(
            [CMD_PELICAN, "--version"], universal_newlines = True
        ).strip()
        archivist.info("Detected Pelican %s", strOut)
        return True
    except:
        # Pelican probably not installed or not using conda etc.
        archivist.error("Could not call Pelican")
        return False


def build_html(dtPelPath):
    archivist = logging.getLogger(LOGGER_NAME)
    archivist.info("Generating HTML using Pelican into output directory")

    fpSettings = dtPelPath[PelicanArgLabel.SETTINGS]
    dpIn = dtPelPath[PelicanArgLabel.INPUT]
    dpOut = dtPelPath[PelicanArgLabel.OUTPUT]

    proc = sp.Popen(
        [CMD_PELICAN, dpIn, "--output", dpOut, "--settings", fpSettings],
        stdout = sp.PIPE, stderr = sp.STDOUT, universal_newlines = True
    )

    for line in iter(proc.stdout.readline, ""):
        archivist.info(line.rstrip('\n'))

    proc.wait()


def dump_diagnostic(dtPelPath):
    labelColWidth = 0
    for (k, v) in dtPelPath.items():
        labelColWidth = max(labelColWidth, len(k))

    archivist = logging.getLogger(LOGGER_NAME)
    for (k, v) in dtPelPath.items():
        archivist.info("{label:<{width}}    {value}".format(
            label = k + ":", width = labelColWidth + 1, value = v
        ))


def main():
    archivist = create_logger()
    # create_logger()

    parser = create_cmd_line_parser()
    args = parser.parse_args()
    subcmd = getattr(args, SubCmd._SUBCMD)

    archivist.info("Running in \"%s\" mode", subcmd)

    try:
        assert check_valid_dir_structure()
        assert check_valid_pelican()
    except AssertionError:
        destroy_logger()
        return 1

    dtPelPath = build_pelican_paths()

    dump_diagnostic(dtPelPath)

    if subcmd == SubCmd.HTML:
        build_html(dtPelPath)
    elif subcmd == SubCmd.CSS:
        pass
    elif subcmd == SubCmd.SITE:
        pass
    elif subcmd == SubCmd.CLEAN:
        pass

    destroy_logger()

    return 0


if __name__ == "__main__":
    sys.exit(main())
