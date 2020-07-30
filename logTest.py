import logging, logging.handlers

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

# file= logging.FileHandler(filename='CustomerMGMT.log')
# file.setLevel(logging.WARNING)

file2= logging.handlers.FileHandler(filename='Customer.log')


logger.addHandler(file);
logger.addHandler(file2);

logger.info('Working!')


