from cmislib.model import CmisClient
from cmislib.exceptions import ObjectNotFoundException
from time import sleep
import sys
import os
import pickle

import settings

SAVE_FILE = 'lastSync.p'


def main():
    while True:
        sync()
        print "Polling for changes every %d seconds" % settings.POLL_INTERVAL
        print "Use ctrl+c to quit"
        print "Sleeping..."
        sleep(settings.POLL_INTERVAL)


def sync():
    # Connect to the source repo
    sourceClient = CmisClient(settings.SOURCE_REPOSITORY_URL,
                          settings.SOURCE_USERNAME,
                          settings.SOURCE_PASSWORD)
    sourceRepo = sourceClient.defaultRepository
    dumpRepoHeader(sourceRepo, "SOURCE")

    # Make sure it supports changes, bail if it does not
    if sourceRepo.getCapabilities()['Changes'] == None:
        print "Source repository does not support changes"
        sys.exit(-1)
    latestChangeToken = sourceRepo.info['latestChangeLogToken']
    print "Latest change token: %s" % latestChangeToken

    # Connect to the target repo
    targetClient = CmisClient(settings.TARGET_REPOSITORY_URL,
                          settings.TARGET_USERNAME,
                          settings.TARGET_PASSWORD)
    targetRepo = targetClient.defaultRepository
    dumpRepoHeader(targetRepo, "TARGET")

    # Make sure target supports contentStreamUpdatability
    if (targetRepo.getCapabilities()['ContentStreamUpdatability'] !=
        'anytime'):
        print "Target repository must have ContentStreamUpdatability=anytime"
        sys.exit(-1)

    # Get last token synced from savefile
    # Using the repository IDs so that you can use this script against
    # multiple source-target pairs and it will remember where you are
    syncKey = "%s><%s" % (sourceRepo.id, targetRepo.id)
    lastChangeSynced = {}
    changeToken = None
    if (os.path.exists(SAVE_FILE)):
        lastChangeSynced = pickle.load(open(SAVE_FILE, "rb" ))
        if lastChangeSynced.has_key(syncKey):
            print "Last change synced: %s" % lastChangeSynced[syncKey]
            changeToken = lastChangeSynced[syncKey]
        else:
            print "First sync..."
    else:
        print "First sync..."

    if changeToken == latestChangeToken:
        print "No changes since last sync so no work to do"
        return

    # Ask the source repo for changes
    changes = None
    if changeToken != None:
        changes = sourceRepo.getContentChanges(changeLogToken=changeToken)
    else:
        changes = sourceRepo.getContentChanges()

    # Process each change
    for change in changes:
        if change.changeType == 'created' or change.changeType == 'updated':
            processChange(change, sourceRepo, targetRepo)

    lastChangeSynced[syncKey] = latestChangeToken
    pickle.dump(lastChangeSynced, open(SAVE_FILE, "wb"))
    return


def processChange(change, sourceRepo, targetRepo):
    """
    Processes a given change by replicating the change from the source
    to the target repository.
    """

    print "Processing: %s" % change.objectId

    # Grab the object
    sourceObj = None
    try:
        sourceObj = sourceRepo.getObject(change.objectId,
                                         getAllowableActions=True)
    except ObjectNotFoundException:
        print "Warning: Change log included an object that no longer exists"
        return

    if (sourceObj.properties['cmis:objectTypeId'] != 'cmis:document' and
        sourceObj.properties['cmis:objectTypeId'] != 'cmis:folder'):
        return

    sourcePath = sourceObj.getPaths()[0]  # Just deal with one path for now
    print "Path: %s" % sourcePath

    # Determine if the object exists in the target
    targetObj = None
    try:
        targetObj = targetRepo.getObjectByPath(sourcePath)

        # If it does, update its properties

        # As only the name and type are being migrated, and because name
        # is part of the path, this part is really not needed
        #targetObj.updateProperties(props)

    except ObjectNotFoundException:
        print "Object does not exist in TARGET"
        sourceProps = sourceObj.properties
        props = {'cmis:name': sourceProps['cmis:name'],
                 'cmis:objectTypeId': sourceProps['cmis:objectTypeId']}
        targetObj = createNewObject(targetRepo, sourcePath, props)

    # Then, update its content if that is possible
    targetObj.reload()
    if (sourceObj.allowableActions['canGetContentStream'] == True and
        targetObj.allowableActions['canSetContentStream'] == True):
        print "Updating content stream in target object"
        targetObj.setContentStream(
            sourceObj.getContentStream(),
            contentType=sourceObj.properties['cmis:contentStreamMimeType'])


def createNewObject(targetRepo, path, props):
    """
    Creates a new object given a target repo, the full path of the
    object, and a bundle of properties. If any elements of the
    specified path do not already exist as folders, they are created.
    """

    print "Creating new object in: %s" % path
    parentPath = '/'.join(path.split('/')[0:-1])

    parentFolder = getParentFolder(targetRepo, parentPath)
    targetObj = None
    if (props['cmis:objectTypeId'] == 'cmis:document'):
        targetObj = parentFolder.createDocumentFromString(
            props['cmis:name'],
            props,
            contentString='')
    else:
        targetObj = parentFolder.createFolder(props['cmis:name'], props)
    return targetObj


def getParentFolder(targetRepo, parentPath):
    """
    Gets the folder at the parent path specified, or creates it if it
    does not exists. Recursively calls createNewObject so that the
    folders in the entire path are created if necessary.
    """

    print "Getting parent folder: %s" % parentPath
    if parentPath == '':
        return targetRepo.rootFolder
    parentFolder = None
    pathList = parentPath.split('/')
    try:
        parentFolder = targetRepo.getObjectByPath(parentPath)
    except ObjectNotFoundException:
        props = {'cmis:name': pathList[-1],
             'cmis:objectTypeId': 'cmis:folder'}        
        parentFolder = createNewObject(targetRepo, parentPath, props)
    return parentFolder


def dumpRepoHeader(repo, label):
    print "=================================="
    print "%s repository info:" % label
    print "----------------------------------"
    print "    Name: %s" % repo.name
    print "      Id: %s" % repo.id
    print "  Vendor: %s" % repo.info['vendorName']
    print " Version: %s" % repo.info['productVersion']


def setLastSync(changeToken):
    sourceClient = CmisClient(settings.SOURCE_REPOSITORY_URL,
                          settings.SOURCE_USERNAME,
                          settings.SOURCE_PASSWORD)
    sourceRepo = sourceClient.defaultRepository

    targetClient = CmisClient(settings.TARGET_REPOSITORY_URL,
                          settings.TARGET_USERNAME,
                          settings.TARGET_PASSWORD)
    targetRepo = targetClient.defaultRepository

    syncKey = "%s><%s" % (sourceRepo.id, targetRepo.id)
    lastChangeSynced = {syncKey: changeToken}
    pickle.dump(lastChangeSynced, open(SAVE_FILE, "wb"))
    print "Forced last sync to: %s" % changeToken

if __name__ == "__main__":
    if len(sys.argv) > 1:
        setLastSync(sys.argv[1])
    main()
