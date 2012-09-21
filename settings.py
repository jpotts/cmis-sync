SOURCE_REPOSITORY_URL = 'http://localhost:8080/alfresco/cmisatom'  # Alfresco 4.0
SOURCE_USERNAME = 'admin'
SOURCE_PASSWORD = 'admin'

TARGET_REPOSITORY_URL = 'http://localhost:8081/inmemory/atom'  # OpenCMIS InMemory 0.8.0 Snapshot
TARGET_USERNAME = 'admin'
TARGET_PASSWORD = 'admin'
TARGET_ROOT = '/cmis-sync'

# The number of seconds to wait before polling for changes in the source
POLL_INTERVAL = 10
