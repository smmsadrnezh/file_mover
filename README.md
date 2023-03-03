This program has two functions:

- It recursively finds all files with some specific extension in a source directory.
Then it hashes their path and copies them to the destination path with the new name.
The new name is hashed version of the file path. Also, It saves the original path and hash name in the database.
- It Copies all files in the destination folder with their original names into their source path.