import logging
from logging.handlers import RotatingFileHandler
import os
import sys

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")

# Configuração do logger
logger = logging.getLogger("SoundBot")  
logger.setLevel(logging.INFO)            

# Formatter (formato da mensagem)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))
logger.addHandler(console_handler)

# Handler para arquivo com rotação (5 arquivos de 1MB cada)
file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)