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

class ArgName:
    PORT = "port"

class SubCmd:
    _SUBCMD = "subcommand"

    SITE = "site"
    HTML = "html"
    CSS = "css"
    CLEAN = "clean"
    SERVE = "serve"

class PelicanArgLabel:
    INPUT = "Content directory"
    OUTPUT = "Output directory"
    SETTINGS = "Settings file"

class SassArgLabel:
    INPUT = "Input source file"
    OUTPUT = "Output file"

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


# PELICAN SUPPORTING FUNCTIONALITY >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_pel_input_dir():
    return "content"


def get_pel_output_dir():
    return "output"


def get_pel_cmd():
    return "pelican"


def build_pelican_paths(dpCur = os.getcwd()):
    fpSettings = op.abspath(op.join(dpCur, FP_PELICAN_SETUP))
    dpIn = op.abspath(op.join(dpCur, get_pel_input_dir()))
    dpOut = op.abspath(op.join(dpCur, get_pel_output_dir()))

    result = {
        PelicanArgLabel.INPUT: dpIn,
        PelicanArgLabel.OUTPUT: dpOut,
        PelicanArgLabel.SETTINGS: fpSettings
    }

    return result


def check_valid_pel_dir_structure(dpCur = os.getcwd()):
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
    for (m, passed) in zip(lstFailMsg, lstPassCheck):
        if not passed:
            archivist.error(m)

    return all(lstPassCheck)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# SASS SUPPORTING FUNCTIONALITY>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_sass_input_file():
    return op.join("extra", "homotypus.scss")


def get_sass_output_file():
    return op.join("theme", "static", "css", "homotypus.css")


def get_sass_cmd():
    if os.name == "nt":
        # Windows
        return ["cmd", "/C", "sass"]
    elif os.name == "posix":
        # UNIX
        return "sass"
    else:
        raise NotImplementedError


def build_sass_paths(dpCur = os.getcwd()):
    fpIn = op.abspath(op.join(dpCur, get_sass_input_file()))
    fpOut = op.abspath(op.join(dpCur, get_sass_output_file()))

    result = {SassArgLabel.INPUT: fpIn, SassArgLabel.OUTPUT: fpOut}

    return result


def check_valid_sass_file_structure(dpCur = os.getcwd()):
    if not op.isdir(dpCur):
        raise ValueError("No such directory [{}] exists".format(dpCur))

    p = build_sass_paths(dpCur)

    archivist = logging.getLogger(LOGGER_NAME)
    fpIn = p[SassArgLabel.INPUT]
    if not op.isfile(fpIn):
        archivist.error(
            "The expected Sass source file [%s] does not exist", fpIn
        )
        return False

    return True


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def create_cmd_line_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description = "A build script for developing the {} website" \
        .format(PROJECT_NAME)
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
        name = SubCmd.CLEAN, help = "Remove existing HTML and CSS files"
    )

    parserServe = subparsers.add_parser(
        name = SubCmd.SERVE, help = "Serve Pelican site locally"
    )
    parserServe.add_argument(
        "-p", "--port",
        dest = ArgName.PORT, type = int, default = 8000
    )

    return parser


def check_valid_ext(lstCmd, strLabel):
    """
    Generic function to check if a certain external dependency exists and can
    be executed.
    """

    if not isinstance(lstCmd, list):
        return check_valid_ext([lstCmd], strLabel)

    archivist = logging.getLogger(LOGGER_NAME)

    try:
        # Attempt to get the installed version number
        strOut = sp.check_output(
            lstCmd + ["--version"], universal_newlines = True
        ).strip()
        archivist.info("Detected %s %s", strLabel, strOut)
        return True
    except:
        # Pelican probably not installed or not using conda etc.
        archivist.error("Could not call %s", strLabel)
        return False


def build_html(dtPelPath):
    archivist = logging.getLogger(LOGGER_NAME)
    archivist.info("Generating HTML using Pelican into output directory")

    fpSettings = dtPelPath[PelicanArgLabel.SETTINGS]
    dpIn = dtPelPath[PelicanArgLabel.INPUT]
    dpOut = dtPelPath[PelicanArgLabel.OUTPUT]

    cmdPel = get_pel_cmd()
    if not isinstance(cmdPel, list):
        cmdPel = [cmdPel]
    args = cmdPel + [dpIn, "--output", dpOut, "--settings", fpSettings]
    proc = sp.Popen(
        args, stdout = sp.PIPE, stderr = sp.STDOUT, universal_newlines = True
    )
    archivist.debug("Executed the following command as PID %d:", proc.pid)
    archivist.debug("%r", args)

    for line in iter(proc.stdout.readline, ""):
        archivist.info(line.rstrip('\n'))

    retcode = proc.wait()
    if retcode == 0:
        archivist.info("Pelican finished successfully")
        archivist.info("")
    else:
        strErrMsg = "Pelican did not finish successfully"
        archivist.error(strErrMsg)
        raise Exception(strErrMsg)


def build_css(dtSassPath):
    archivist = logging.getLogger(LOGGER_NAME)
    archivist.info("Generating CSS files using Sass")

    fpIn = dtSassPath[SassArgLabel.INPUT]
    fpOut = dtSassPath[SassArgLabel.OUTPUT]

    if op.isfile(fpOut):
        archivist.info("Existing file [%s] will be overwritten by Sass", fpOut)

    cmdSass = get_sass_cmd()
    if not isinstance(cmdSass, list):
        cmdSass = [cmdSass]
    args = cmdSass + ["--no-quiet", "--embed-source-map", fpIn, fpOut]
    proc = sp.Popen(
        args, stdout = sp.PIPE, stderr = sp.STDOUT, universal_newlines = True
    )
    archivist.debug("Executed the following command as PID %d:", proc.pid)
    archivist.debug("%r", args)

    for line in iter(proc.stdout.readline, ""):
        archivist.info(line.rstrip('\n'))

    retcode = proc.wait()
    if retcode == 0:
        archivist.info("Sass finished successfully")
        archivist.info("")
    else:
        strErrMsg = "Sass did not finish successfully"
        archivist.error(strErrMsg)
        raise Exception(strErrMsg)


def clean():
    archivist = logging.getLogger(LOGGER_NAME)

    dpPelOut = get_pel_output_dir()
    flagRmPel = op.isdir(dpPelOut)

    fpSassOut = get_sass_output_file()
    flagRmSass = op.isfile(fpSassOut)

    lstFlagRm = [flagRmPel, flagRmSass]
    lstDesc = [
        "Pelican output directory [{}]".format(dpPelOut),
        "Sass output CSS file [{}]".format(fpSassOut)
    ]
    flagRmAny = any(lstFlagRm)
    if flagRmAny:
        archivist.info("The following will be removed:")
        for (desc, flagRm) in zip(lstDesc, lstFlagRm):
            if flagRm:
                archivist.info("    " + desc)

        archivist.info("")
    else:
        archivist.info("Nothing to remove")

    if op.isdir(dpPelOut):
        try:
            import shutil
            shutil.rmtree(dpPelOut)
            archivist.info("Removed Pelican output directory")
        except e:
            archivist.error("Could not remove Pelican output directory")
            raise e

    if op.isfile(fpSassOut):
        try:
            os.remove(fpSassOut)
            archivist.info("Removed Sass output file")
        except e:
            archivist.error("Could not remove Sass output file")
            raise e

    archivist.info("")


def serve(cmdLineArgs, dtPelPath):
    # This method won't return until the user stops the server
    archivist = logging.getLogger(LOGGER_NAME)
    archivist.info("Serving Pelican site...")

    fpSettings = dtPelPath[PelicanArgLabel.SETTINGS]
    dpIn = dtPelPath[PelicanArgLabel.INPUT]
    dpOut = dtPelPath[PelicanArgLabel.OUTPUT]

    port = getattr(cmdLineArgs, ArgName.PORT)
    flagDebug = getattr(cmdLineArgs, ArgName.DEBUG)

    cmdPel = get_pel_cmd()
    if not isinstance(cmdPel, list):
        cmdPel = [cmdPel]
    args = cmdPel + [
        dpIn, "--output", dpOut, "--settings", fpSettings,
        "--port", str(port), "--listen"
    ]
    if flagDebug:
        args.append("--debug")

    archivist.debug("About to execute the following command:")
    archivist.debug("    %r", args)

    proc = sp.Popen(args, creationflags = sp.CREATE_NEW_CONSOLE)
    proc.wait()


def dump_path_diagnostic(dtPath, strHead = None):
    labelColWidth = 0
    for (k, v) in dtPath.items():
        labelColWidth = max(labelColWidth, len(k))

    archivist = logging.getLogger(LOGGER_NAME)

    NUM_CHAR_HEADER = 80

    flagHead = not strHead is None and isinstance(strHead, str)
    if flagHead:
        archivist.info((strHead + ' ').ljust(NUM_CHAR_HEADER, '>').rstrip())

    for (k, v) in dtPath.items():
        archivist.info("{label:<{width}}    {value}".format(
            label = k + ":", width = labelColWidth + 1, value = v
        ))

    if flagHead:
        archivist.info('<' * NUM_CHAR_HEADER)
        archivist.info("")


def main():
    archivist = create_logger()
    # create_logger()

    parser = create_cmd_line_parser()
    args = parser.parse_args()
    subcmd = getattr(args, SubCmd._SUBCMD)

    archivist.info("Running in \"%s\" mode", subcmd)

    flagNeedPel = subcmd in [SubCmd.HTML, SubCmd.SITE, SubCmd.SERVE]
    flagNeedSass = subcmd in [SubCmd.CSS, SubCmd.SITE]
    flagNeedExt = any([flagNeedPel, flagNeedSass])

    try:
        if flagNeedPel:
            assert check_valid_pel_dir_structure()
            assert check_valid_ext(get_pel_cmd(), "Pelican")

        if flagNeedSass:
            assert check_valid_sass_file_structure()
            assert check_valid_ext(get_sass_cmd(), "Sass")
    except AssertionError:
        destroy_logger()
        return 1

    if flagNeedExt:
        archivist.info("")

    if flagNeedPel:
        dtPelPath = build_pelican_paths()
        dump_path_diagnostic(dtPelPath, "Pelican arguments")

    if flagNeedSass:
        dtSassPath = build_sass_paths()
        dump_path_diagnostic(dtSassPath, "Sass arguments")

    try:
        if subcmd == SubCmd.HTML:
            build_html(dtPelPath)
        elif subcmd == SubCmd.CSS:
            build_css(dtSassPath)
        elif subcmd == SubCmd.SITE:
            build_css(dtSassPath)
            build_html(dtPelPath)
        elif subcmd == SubCmd.CLEAN:
            clean()
        elif subcmd == SubCmd.SERVE:
            serve(args, dtPelPath)
    except:
        destroy_logger()
        return 1

    archivist.info("Finished")

    destroy_logger()
    return 0


if __name__ == "__main__":
    sys.exit(main())
