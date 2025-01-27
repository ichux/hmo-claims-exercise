import os


class Config(object):
    """
    Common configurations
    """
    SECRET_KEY = os.urandom(16)
    ASSETS_DEBUG = True
    CSRF_ENABLED = True

class IntronConfig(Config):
    """
    Configurations
    """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = True
    test_directory_path = os.path.dirname(os.path.realpath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(test_directory_path, 'intron_db.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_BINDS = {
        "test": 'sqlite:///' + os.path.join(test_directory_path, 'intron_db.db')
    }

class TestConfig(IntronConfig):
    """
    Configurations for unit testing
    """
    DEBUG = False
    TESTING = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_BINDS = {
        "test": 'sqlite:///:memory:'
    }
    CSRF_ENABLED = False
    SECRET_KEY = Config.SECRET_KEY

app_config = {
    'config': IntronConfig,
    'test': TestConfig
}

