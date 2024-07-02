# Email Settings
EMAIL_SERVICE_NAME = "Cloudforet"
EMAIL_SEND_RETRY_INTERVAL = 180

# Database Settings
DATABASES = {
    "default": {
        "db": "board",
        "host": "localhost",
        "port": 27017,
        "username": "",
        "password": "",
    }
}

# Cache Settings
CACHES = {
    "default": {
        # Redis Example
        # 'backend': 'spaceone.core.cache.redis_cache.RedisCache',
        # 'host': '<host>',
        # 'port': 6379,
        # 'db': 0
    }
}

# Handler Configuration
HANDLERS = {
    "authentication": [
        # Default Authentication Handler
        # {
        #     'backend': 'spaceone.core.handler.authentication_handler.AuthenticationGRPCHandler',
        #     'uri': 'grpc://identity:50051/v1/Domain/get_public_key'
        # }
    ],
    "authorization": [
        # Default Authorization Handler
        # {
        #     'backend': 'spaceone.core.handler.authorization_handler.AuthorizationGRPCHandler',
        #     'uri': 'grpc://identity:50051/v1/Authorization/verify'
        # }
    ],
    "mutation": [],
    "event": [],
}

# Connector Settings
CONNECTORS = {
    "SpaceConnector": {
        "backend": "spaceone.core.connector.space_connector:SpaceConnector",
        "endpoints": {
            "identity": "grpc://identity:50051",
            "file_manager": "grpc://file-manager:50051",
            "config": "grpc://config:50051",
        },
    },
    "SMTPConnector": {
        # "host": "smtp.mail.com",
        # "port": "1234",
        # "user": "cloudforet",
        # "password": "1234",
        # "from_email": "support@cloudforet.com",
    },
}

# Log Settings
LOG = {}

# System Token Settings
TOKEN = ""
