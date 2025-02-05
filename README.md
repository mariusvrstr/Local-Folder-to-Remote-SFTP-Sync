# Sync local folder to remote SFTP server

- Files that were created in the last 10min will go through a check to see if file size changes before being transferred
- Completed files will be archived
- If the file exists it will either override it (When it is smaller) or it will skip the attempt to upload (If the filesize is the same)
- If the local folder structure does not yet exist it will create it on the server side

## Configurations

- SFTP Destination and creds
- The local folder that needs to be replicated
- Which folders to ignore e.g. Archive
  
