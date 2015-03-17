Provides simple, one-way synchronization between two CMIS repositories.

Dependencies:
  * Python 2.7.3 (probably works with 2.6.x as well)
  * cmislib 0.5.1

## Compatible Repositories ##

This should work with any CMIS 1.0 compliant repository. The source CMIS repository must support changes. The target repository must support direct update of the content stream.

This is known to work with the following repositories:

### Sources ###

Alfresco 4.0.d Community Edition

### Targets ###

Apache Chemistry OpenCMIS InMemory 0.8.0-SNAPSHOT

## Installation ##

See the [README file](http://code.google.com/p/cmis-sync/source/browse/README.txt) for config and installation tips.

## Limitations ##

See the [README file](http://code.google.com/p/cmis-sync/source/browse/README.txt) for a detailed listing of limitations.