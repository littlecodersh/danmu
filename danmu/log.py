import os, logging

if not os.path.exists('config'): os.mkdir('config')
log = logging.getLogger('danmu')
log.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(os.path.join('config', 'run.log'), encoding = 'utf8')
fileHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)-17s <%(message)s> %(levelname)s %(filename)s[%(lineno)d]',
    datefmt='%Y%m%d %H:%M:%S')
fileHandler.setFormatter(formatter)
log.addHandler(fileHandler)

if __name__ == '__main__':
    log.debug('This is debug')
    log.info('This is info')
