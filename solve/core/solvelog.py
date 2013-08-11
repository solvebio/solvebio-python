import logging
import os

LOGLEVEL = os.environ.get('SOLVE_LOGLEVEL', 'ERROR').upper()


def _init_logging():
    base_logger = logging.getLogger("solve")
    base_logger.setLevel(LOGLEVEL)

    #clear handlers if any exist
    handlers = base_logger.handlers[:]
    for handler in handlers:
        base_logger.removeHandler(handler)
        handler.close()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOGLEVEL)
    stream_fmt = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler.setFormatter(stream_fmt)
    base_logger.addHandler(stream_handler)

    # TODO: move this too a generalized config module
    config_path = os.path.expanduser('~/.solve')
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    logfile_path = os.path.join(config_path, 'solve.log')
    file_handler = logging.FileHandler(logfile_path)
    file_handler.setLevel(LOGLEVEL)
    file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_fmt)
    base_logger.addHandler(file_handler)

    return base_logger

solvelog = _init_logging()
