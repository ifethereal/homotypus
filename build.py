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

class ArgName:
    DEBUG = "debug"
    PORT = "port"

class SubCmd:
    _SUBCMD = "subcommand"

    SITE = "site"
    HTML = "html"
    CSS = "css"
    CLEAN = "clean"
    SERVE_PELICAN = "serve-pelican"
    SERVE_PYTHON = "serve"

class PelicanArgLabel:
    INPUT = "Content directory"
    OUTPUT = "Output directory"
    SETTINGS = "Settings file"

class SassArgLabel:
    INPUT = "Input source file"
    OUTPUT = "Output file"

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# LOGGER SUPPORT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def create_logger(name = LOGGER_NAME, level = logging.INFO):
    archivist = logging.getLogger(name)
    archivist.setLevel(logging.DEBUG)

    # Set up logging to terminal
    terminal = logging.StreamHandler(sys.stdout)
    terminal.setLevel(level)
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


def build_pelican_input_paths(dpCur = os.getcwd()):
    FP_PELICAN_SETUP = "settings.py"
    fpSettings = op.abspath(op.join(dpCur, FP_PELICAN_SETUP))
    dpIn = op.abspath(op.join(dpCur, get_pel_input_dir()))

    result = {
        PelicanArgLabel.INPUT: dpIn,
        PelicanArgLabel.SETTINGS: fpSettings
    }

    return result


def build_pelican_output_paths(dpCur = os.getcwd()):
    dpOut = op.abspath(op.join(dpCur, get_pel_output_dir()))

    result = {PelicanArgLabel.OUTPUT: dpOut}

    return result


def build_pelican_paths(dpCur = os.getcwd(), wantIn = True, wantOut = True):
    result = {}

    if wantIn:
        dtPelInPath = build_pelican_input_paths()
        result.update(dtPelInPath)

    if wantOut:
        dtPelOutPath = build_pelican_output_paths()
        result.update(dtPelOutPath)

    return result


def check_valid_pel_dir_structure(
    dpCur = os.getcwd(), wantIn = True, wantOut = False
):
    lstPassCheck = []
    lstFailMsg = []

    if not op.isdir(dpCur):
        raise ValueError("No such directory [{}] exists".format(dpCur))

    p = build_pelican_paths(dpCur, wantIn, wantOut)

    archivist = logging.getLogger(LOGGER_NAME)
    if not wantIn and not wantOut:
        archivist.debug("No Pelican paths being checked")

    if wantIn:
        fpSettings = p[PelicanArgLabel.SETTINGS]
        lstPassCheck.append(op.isfile(fpSettings))
        lstFailMsg.append(
            "The expected Pelican settings file [{}] does not exist" \
            .format(fpSettings)
        )

        dpIn = p[PelicanArgLabel.INPUT]
        lstPassCheck.append(op.isdir(dpIn))
        lstFailMsg.append(
            "The expected Pelican content directory [{}] does not exist" \
            .format(dpIn)
        )

    if wantOut:
        dpOut = p[PelicanArgLabel.OUTPUT]
        lstPassCheck.append(op.isdir(dpOut))
        lstFailMsg.append([
            "The Pelican output directory [{}] does not exist".format(dpOut),
            "Make sure Pelican has been used to generate the site"
        ])

    for (m, passed) in zip(lstFailMsg, lstPassCheck):
        if not passed:
            if isinstance(m, list):
                lstMsg = m
            else:
                lstMsg = [m]
            for msg in lstMsg:
                archivist.error(msg)

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


def build_sass_paths(dpCur = os.getcwd(), wantIn = True, wantOut = True):
    result = {}

    if wantIn:
        fpIn = op.abspath(op.join(dpCur, get_sass_input_file()))
        result[SassArgLabel.INPUT] = fpIn

    if wantOut:
        fpOut = op.abspath(op.join(dpCur, get_sass_output_file()))
        result[SassArgLabel.OUTPUT] = fpOut

    return result


def check_valid_sass_file_structure(
    dpCur = os.getcwd(), wantIn = True, wantOut = False
):
    lstPassCheck = []
    lstFailMsg = []

    if not op.isdir(dpCur):
        raise ValueError("No such directory [{}] exists".format(dpCur))

    p = build_sass_paths(dpCur)

    archivist = logging.getLogger(LOGGER_NAME)
    if not wantIn and not wantOut:
        archivist.debug("No Sass paths being checked")

    if wantIn:
        fpIn = p[SassArgLabel.INPUT]
        lstPassCheck.append(op.isfile(fpIn))
        lstFailMsg.append(
            "The expected Sass source file [{}] does not exist".format(fpIn)
        )

    if wantOut:
        fpOut = p[SassArgLabel.OUTPUT]
        lstPassCheck.append(op.isfile(fpOut))
        lstFailMsg.append([
            "The Sass output file [{}] does not exist".format(fpOut),
            "Make sure Sass has been used to generate the CSS file"
        ])

    for (m, passed) in zip(lstFailMsg, lstPassCheck):
        if not passed:
            if isinstance(m, list):
                lstMsg = m
            else:
                lstMsg = [m]
            for msg in lstMsg:
                archivist.error(msg)

    return all(lstPassCheck)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def create_cmd_line_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description = "A build script for developing the {} website" \
        .format(PROJECT_NAME)
    )
    parser.add_argument(
        "--debug",
        dest = ArgName.DEBUG, action = "store_true",
        help = "Specify this to see more diagnostic output"
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

    DEFAULT_PORT = 8000

    parserServe = subparsers.add_parser(
        name = SubCmd.SERVE_PYTHON,
        help = "Serve site locally with Python [3.x]"
    )
    parserServe.add_argument(
        "-p", "--port",
        dest = ArgName.PORT, type = int, default = DEFAULT_PORT,
        help = "Port at which to serve the site"
    )

    parserServePel = subparsers.add_parser(
        name = SubCmd.SERVE_PELICAN, help = "Serve site locally using Pelican"
    )
    parserServePel.add_argument(
        "-p", "--port",
        dest = ArgName.PORT, type = int, default = DEFAULT_PORT,
        help = "Port at which to serve the site"
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
    archivist.debug("Executed the following command as PID %d", proc.pid)
    archivist.debug("    %r", args)

    for line in iter(proc.stdout.readline, ""):
        archivist.info(line.rstrip('\n'))

    retcode = proc.wait()
    if retcode == 0:
        archivist.info("Pelican finished successfully")
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
    archivist.debug("Executed the following command as PID %d", proc.pid)
    archivist.debug("    %r", args)

    for line in iter(proc.stdout.readline, ""):
        archivist.info(line.rstrip('\n'))

    retcode = proc.wait()
    if retcode == 0:
        archivist.info("Sass finished successfully")
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
                archivist.info("    %s", desc)

        archivist.info("")
    else:
        archivist.info("Nothing to remove")

    if op.isdir(dpPelOut):
        try:
            import shutil
            shutil.rmtree(dpPelOut)
            archivist.info("Removed Pelican output directory")
        except:
            archivist.error("Could not remove Pelican output directory")
            raise

    if op.isfile(fpSassOut):
        try:
            os.remove(fpSassOut)
            archivist.info("Removed Sass output file")
        except:
            archivist.error("Could not remove Sass output file")
            raise


def serve_pelican(cmdLineArgs, dtPelPath):
    # This method won't return until the user stops the server
    archivist = logging.getLogger(LOGGER_NAME)
    archivist.info("Serving Pelican site using Pelican...")

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

    # Let the server communicate in a separate console window
    proc = sp.Popen(args, creationflags = sp.CREATE_NEW_CONSOLE)
    archivist.debug("Executed the following command as PID %d:", proc.pid)
    archivist.debug("    %r", args)

    import webbrowser
    strUrl = "http://localhost:{}/".format(str(port))
    webbrowser.open_new_tab(strUrl)
    proc.wait()
    archivist.info("Server stopped")


def serve_python(cmdLineArgs, dtPelOutPath):
    archivist = logging.getLogger(LOGGER_NAME)
    archivist.info("Serving Pelican site using Python...")

    dpOut = dtPelOutPath[PelicanArgLabel.OUTPUT]

    port = getattr(cmdLineArgs, ArgName.PORT)
    args = [
        "python", "-m", "http.server", str(port), "--bind", "localhost",
        "--directory", dpOut
    ]

    # Let the server communicate in a separate console window
    proc = sp.Popen(args, creationflags = sp.CREATE_NEW_CONSOLE)
    archivist.debug("Executed the following command as PID %d:", proc.pid)
    archivist.debug("    %r", args)

    import webbrowser
    strUrl = "http://localhost:{}/".format(str(port))
    webbrowser.open_new_tab(strUrl)
    proc.wait()
    archivist.info("Server stopped")


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
    parser = create_cmd_line_parser()
    args = parser.parse_args()

    flagDebug = getattr(args, ArgName.DEBUG)
    terminalLogLevel = logging.DEBUG if flagDebug else logging.INFO

    archivist = create_logger(level = terminalLogLevel)

    subcmd = getattr(args, SubCmd._SUBCMD)
    archivist.info("Running in \"%s\" mode", subcmd)
    archivist.info("")

    # Decide dependencies

    # Do Pelican input files need to exist?
    flagNeedPelIn = subcmd in [SubCmd.HTML, SubCmd.SITE, SubCmd.SERVE_PELICAN]

    # Does Pelican need to be executed?
    flagNeedPelUse = flagNeedPelIn

    # Do Pelican output files need to exist?
    flagNeedPelOut = subcmd in [SubCmd.SERVE_PELICAN, SubCmd.SERVE_PYTHON]

    # Do Pelican output destinations need to be specified?
    # Only use is for deciding if we should remind the user what the output
    # destinations are.
    flagNeedPelOutSpec = flagNeedPelOut or subcmd in [SubCmd.HTML, SubCmd.SITE]

    # Do Sass input files need to exist?
    flagNeedSassIn = subcmd in [SubCmd.CSS, SubCmd.SITE]

    # Does Sass need to be executed?
    flagNeedSassUse = flagNeedSassIn

    # Do Sass output files need to exist?
    flagNeedSassOut = subcmd in [SubCmd.HTML]

    # Do Sass output destinations need to be specified?
    # Only use is for deciding if we should remind the user what the output
    # destinations are. Note that if Pelican is building the site, it already
    # knows where to find the Sass output file, and the user does not need to
    # know.
    flagNeedSassOutSpec = subcmd in [SubCmd.CSS, SubCmd.SITE]

    # Sass creates any necessary directories needed for writing to the
    # destination, so no need to check if the parent directory of the
    # destination file exists

    try:
        # Validate existing resources depending on required dependencies
        assert check_valid_pel_dir_structure(
            wantIn = flagNeedPelIn, wantOut = flagNeedPelOut
        )
        assert not flagNeedPelUse or check_valid_ext(get_pel_cmd(), "Pelican")

        assert check_valid_sass_file_structure(
            wantIn = flagNeedSassIn, wantOut = flagNeedSassOut
        )
        assert not flagNeedSassUse or check_valid_ext(get_sass_cmd(), "Sass")

        if flagNeedPelUse or flagNeedSassUse:
            archivist.info("")
    except AssertionError:
        destroy_logger()
        raise

    if flagNeedPelIn or flagNeedPelOutSpec:
        dtPelPath = build_pelican_paths(
            wantIn = flagNeedPelIn, wantOut = flagNeedPelOutSpec
        )
        dump_path_diagnostic(dtPelPath, "Pelican arguments")

    if flagNeedSassIn or flagNeedSassOutSpec:
        dtSassPath = build_sass_paths(
            wantIn = flagNeedSassIn, wantOut = flagNeedSassOutSpec
        )
        dump_path_diagnostic(dtSassPath, "Sass arguments")

    try:
        # Execute commands
        if subcmd == SubCmd.HTML:
            build_html(dtPelPath)
        elif subcmd == SubCmd.CSS:
            build_css(dtSassPath)
        elif subcmd == SubCmd.SITE:
            build_css(dtSassPath)
            archivist.info("")
            build_html(dtPelPath)
        elif subcmd == SubCmd.CLEAN:
            clean()
        elif subcmd == SubCmd.SERVE_PELICAN:
            serve_pelican(args, dtPelPath)
        elif subcmd == SubCmd.SERVE_PYTHON:
            serve_python(args, dtPelPath)
    except:
        archivist.error("Could not finish successfully")
        destroy_logger()
        raise

    archivist.info("")
    archivist.info("Finished")

    destroy_logger()
    return 0


if __name__ == "__main__":
    sys.exit(main())
