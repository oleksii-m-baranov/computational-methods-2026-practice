import logging
import sys

def custom_logger(name, overwrite=False):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        
        mode = 'w' if overwrite else 'a'
        fh = logging.FileHandler(f"{name}.log", mode=mode, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
