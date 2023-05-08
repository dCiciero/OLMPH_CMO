import os
basedir = os.path.abspath(os.path.dirname(__file__))
upload_folder = os.path.join(basedir, 'app/static/images/uploads')

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'olmph.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = upload_folder
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    APP_SETTINGS = os.environ.get('APP_SETTINGS')
    FLASKS3_BUCKET_NAME = 'awsogcicerobucket'

class ProductionConfig(Config):
    'Production specific config'
    DEBUG = False

class StagingConfig(Config):
    'Staging specific config'
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = False
    TESTING = True
    SECRET_KEY = 'The Quick Brown Fox Jumps Over The Lazy Dog'