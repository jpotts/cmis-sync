# cmis-sync

Provides simple, one-way synchronization between two CMIS repositories.

## Dependencies

* Python 2.7.3 (probably works with 2.6.x as well)
* cmislib 0.5.1 

## Compatible Repositories

This should work with any CMIS 1.0 compliant repository. The source CMIS repository must support changes. The target repository must support direct update of the content stream.

This is known to work with the following repositories:

### Sources

* Alfresco 4.0.d Community Edition

### Targets

* Apache Chemistry OpenCMIS InMemory? 0.8.0-SNAPSHOT

## Installation

These instructions assume cmislib is already in your sys.path somehow. I recommend virtualenv, but to each his own. You'll most likely need cmislib from HEAD. I think there are one or two minor issues in cmislib 0.5 related to changes.

Edit settings.py to set SOURCE and TARGET settings appropriately. This only supports one source to one target at the moment.

Your SOURCE must support changes.

Your TARGET must support ContentStreamUpdatability = anytime.

The POLL_INTERVAL dictates how often the script will check the source for changes.

## Limitations

* Only syncs cmis:document and cmis:folder.
* Only syncs standard metadata (cmis:name, cmis:contentStreamMimeType, and the contentStream).
* Sync is one-way only, from SOURCE to TARGET.
* Only supports 'created' and 'updated' change types.
* Uses path and name to match source and target objects. Therefore, renames and path changes are not supported.
* This script will not sync deletes.

## Running

Run the script with no arguments to start syncing. The first time it runs it will call getContentChanges with no token. It will save the latest token in lastSync.p so that on subsequent runs, it will only get what has changed since the last run.

Force the script to start syncing from a specific token by passing the token to the script as the first argument.
