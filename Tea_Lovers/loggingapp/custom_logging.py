import logging


class Logger: 
    """
    Class for logger funcionality across project
    
    Params:
    - name (str): Name of the module/file using this class. Default is 'root'
    
    Exception:
    ValueError: If no name provided and not called from __init__ method
    
    Returns:
    None
    """ 
    _logger_initialized = False  
    def __init__(self):
        if not Logger._logger_initialized:            
            self.logger = logging.getLogger('scraper')
            self.logger.setLevel(logging.INFO)

            c_handler = logging.StreamHandler()
            f_handler = logging.FileHandler('scraper.log')

            c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            c_handler.setFormatter(c_format)
            f_handler.setFormatter(f_format)

            self.logger.addHandler(c_handler)
            self.logger.addHandler(f_handler)

            Logger._logger_initialized = True  # Mark as initialized
        else:
            self.logger = logging.getLogger('scraper')