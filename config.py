import logging
import os 


if not os.path.isdir('logs'):
    os.mkdir('logs')
if not os.path.isdir('temp'):
    os.mkdir('temp')
if not os.path.isdir('xml'):
    os.mkdir('xml')

log_format = '%(asctime)s:%(levelname)s:%(filename)s:%(message)s'# Configuracao de logs
logging.basicConfig(filename='logs\\FD_nfe_xmls.log',
                    filemode='w',
                    level=logging.INFO,
                    format=log_format,
                    encoding='UTF-8') 