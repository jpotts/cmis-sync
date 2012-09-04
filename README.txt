This assumes cmislib is already in your sys.path somehow. I recommend virtualenv, but to each his own. You'll most likely need cmislib from HEAD. I think there are one or two minor issues in cmislib 0.5 related to changes.

Edit settings.py to set SOURCE and TARGET settings appropriately. This only supports one source to one target at the moment.

Your SOURCE must support changes.

Your TARGET must support ContentStreamUpdatability = anytime.

The POLL_INTERVAL dictates how often the script will check the source for changes.

Limitations:
 - Only syncs cmis:document and cmis:folder.
 - Only syncs standard metadata (cmis:name, cmis:contentStreamMimeType, and the contentStream).
 - Sync is one-way only, from SOURCE to TARGET.
 - Only supports 'created' and 'updated' change types.
 - Uses path and name to match source and target objects. Therefore, renames and path changes are not supported.
 - This script will not sync deletes.

Run the script with no arguments to start syncing. The first time it runs it will call getContentChanges with no token. It will save the latest token in lastSync.p so that on subsequent runs, it will only get what has changed since the last run.

Force the script to start syncing from a specific token by passing the token to the script as the first argument.
