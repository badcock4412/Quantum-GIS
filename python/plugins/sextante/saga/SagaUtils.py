# -*- coding: utf-8 -*-

"""
***************************************************************************
    SagaUtils.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from sextante.core.SextanteUtils import SextanteUtils
import subprocess
from sextante.core.SextanteConfig import SextanteConfig
from sextante.core.SextanteLog import SextanteLog
import stat

class SagaUtils:

    SAGA_LOG_COMMANDS = "SAGA_LOG_COMMANDS"
    SAGA_LOG_CONSOLE = "SAGA_LOG_CONSOLE"
    SAGA_AUTO_RESAMPLING = "SAGA_AUTO_RESAMPLING"
    SAGA_RESAMPLING_REGION_XMIN = "SAGA_RESAMPLING_REGION_XMIN"
    SAGA_RESAMPLING_REGION_YMIN = "SAGA_RESAMPLING_REGION_YMIN"
    SAGA_RESAMPLING_REGION_XMAX = "SAGA_RESAMPLING_REGION_XMAX"
    SAGA_RESAMPLING_REGION_YMAX = "SAGA_RESAMPLING_REGION_YMAX"
    SAGA_RESAMPLING_REGION_CELLSIZE = "SAGA_RESAMPLING_REGION_CELLSIZE"
    SAGA_FOLDER = "SAGA_FOLDER"

    @staticmethod
    def sagaBatchJobFilename():

        if SextanteUtils.isWindows():
            filename = "saga_batch_job.bat";
        else:
            filename = "saga_batch_job.sh";

        batchfile = SextanteUtils.userFolder() + os.sep + filename

        return batchfile

    @staticmethod
    def sagaPath():
        folder = SextanteConfig.getSetting(SagaUtils.SAGA_FOLDER)
        if folder == None:
            folder =""

        return folder

    @staticmethod
    def sagaDescriptionPath():
        return os.path.join(os.path.dirname(__file__),"description")

    @staticmethod
    def createSagaBatchJobFileFromSagaCommands(commands):

        fout = open(SagaUtils.sagaBatchJobFilename(), "w")
        if SextanteUtils.isWindows():
            fout.write("set SAGA=" + SagaUtils.sagaPath() + "\n");
            fout.write("set SAGA_MLB=" + SagaUtils.sagaPath()+ os.sep + "modules" + "\n");
            fout.write("PATH=PATH;%SAGA%;%SAGA_MLB%\n");
        else:
            pass
        for command in commands:
            fout.write("saga_cmd " + command.encode("utf8") + "\n")

        fout.write("exit")
        fout.close()

    @staticmethod
    def executeSaga(progress):
        if SextanteUtils.isWindows():
            command = ["cmd.exe", "/C ", SagaUtils.sagaBatchJobFilename()]
        else:
            os.chmod(SagaUtils.sagaBatchJobFilename(), stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
            command = [SagaUtils.sagaBatchJobFilename()]
        loglines = []
        loglines.append("SAGA execution console output")
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).stdout
        for line in iter(proc.readline, ""):
            if "%" in line:
                s = "".join([x for x in line if x.isdigit()])
                try:
                    progress.setPercentage(int(s))
                except:
                    pass
            else:
                line = line.strip()
                if line!="/" and line!="-" and line !="\\" and line!="|":
                    loglines.append(line)
                    progress.setConsoleInfo(line)
        if SextanteConfig.getSetting(SagaUtils.SAGA_LOG_CONSOLE):
            SextanteLog.addToLog(SextanteLog.LOG_INFO, loglines)





