import logging

class Logger:
    def __init__(self, name='default'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Prevent adding multiple handlers of the same type
        if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
            f_handler = logging.FileHandler(f'{name}.log', mode='a')
            f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            f_handler.setFormatter(f_format)
            logger.addHandler(f_handler)

        self.logger = logger
