# MIT License

# Copyright (c) 2019 Georgios Papachristou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import subprocess
import os
import psutil
import logging

from jarvis import settings
from jarvis.utils.mongoDB import db
from jarvis.utils.console import eris_logo, start_text, OutputStyler, headerize
from jarvis.enumerations import MongoCollections, InputMode


class ConsoleManager:
    def __init__(self):
        pass

    def clear(self):
        """
        Clears stdout

        Check and make call for specific operating system
        """

        subprocess.call('tput reset' if os.name == 'posix' else 'cls', shell=True)

    def console_output(self, text='', debug_log=None, info_log=None, warn_log=None, error_log=None, refresh_console=True):

        if refresh_console:
            self.clear()

            # ----------------------------------------------------------------------------------------------------------
            # Logo sector
            # ----------------------------------------------------------------------------------------------------------
            self._stdout_print(eris_logo + start_text)
            self._stdout_print("     TIP: CTRL + C para apagar en caso de emergencia.")

            # ----------------------------------------------------------------------------------------------------------
            # General info sector
            # ----------------------------------------------------------------------------------------------------------
            settings_documents = db.get_documents(collection=MongoCollections.GENERAL_SETTINGS.value)
            if settings_documents:
                settings_ = settings_documents[0]
                print(OutputStyler.HEADER + headerize('INFORMACION') + OutputStyler.ENDC)
                enabled = OutputStyler.GREEN + 'ACTIVO' + OutputStyler.ENDC if settings_['response_in_speech'] else OutputStyler.WARNING + 'NO ACTIVADO' + OutputStyler.ENDC
                print(OutputStyler.BOLD + 'RESPUESTA AL DIALOGO: ' + enabled)
                print(OutputStyler.BOLD + 'MODO DE ENTRADA: ' + OutputStyler.GREEN + '{0}'.format(settings_['input_mode'].upper() + OutputStyler.ENDC) + OutputStyler.ENDC)
                if settings_['input_mode'] == InputMode.VOICE.value:
                    print(OutputStyler.BOLD + 'NOTA: ' + OutputStyler.GREEN + "Incluye " + "'{0}'".format(settings_['assistant_name'].upper()) + " en los comandos para activar" + OutputStyler.ENDC + OutputStyler.ENDC)

            # ----------------------------------------------------------------------------------------------------------
            # System info sector
            # ----------------------------------------------------------------------------------------------------------
            print(OutputStyler.HEADER + headerize('SYSTEM') + OutputStyler.ENDC)
            print(OutputStyler.BOLD +
                  'USO ESTIMADO DE RAM: {0:.2f} GB'.format(self._get_memory()) + OutputStyler.ENDC)

            # ----------------------------------------------------------------------------------------------------------
            # Assistant logs sector
            # ----------------------------------------------------------------------------------------------------------

            if debug_log:
                logging.debug(debug_log)

            if info_log:
                logging.info(info_log)

            if warn_log:
                logging.warning(warn_log)

            if error_log:
                logging.error(error_log)

            MAX_NUMBER_OF_LOG_LINES = 25
            log_path = settings.ROOT_LOG_CONF['handlers']['file']['filename']

            lines = subprocess.check_output(['tail', '-' + str(MAX_NUMBER_OF_LOG_LINES), log_path]).decode("utf-8")
            actual_number_of_log_lines = len(lines)
            print(OutputStyler.HEADER + headerize('LOG -{0} (Total Lines: {1})'.format(log_path,
                                                                                       actual_number_of_log_lines)
                                                  ) + OutputStyler.ENDC)
            print(OutputStyler.BOLD + lines + OutputStyler.ENDC)

            # ----------------------------------------------------------------------------------------------------------
            # Assistant input/output sector
            # ----------------------------------------------------------------------------------------------------------
            print(OutputStyler.HEADER + headerize('ASISTENTE') + OutputStyler.ENDC)
            if text:
                print(OutputStyler.BOLD + '> ' + text + '\r' + OutputStyler.ENDC)
                print(OutputStyler.HEADER + headerize() + OutputStyler.ENDC)
        else:
            if text:
                print(OutputStyler.BOLD + text + '\r' + OutputStyler.ENDC)

    @staticmethod
    def _get_memory():
        """
        Get assistant process Memory usage in GB
        """
        pid = os.getpid()
        py = psutil.Process(pid)
        return py.memory_info()[0] / 2. ** 30

    @staticmethod
    def _stdout_print(text):
        """
        Application stdout with format.
        :param text: string
        """
        print(OutputStyler.CYAN + text + OutputStyler.ENDC)
