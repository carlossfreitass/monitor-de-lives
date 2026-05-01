import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado com formato estruturado.
    Todos os logs vão para stdout com timestamp e nível.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Evita duplicar handlers em reloads

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger