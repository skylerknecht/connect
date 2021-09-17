function delfile(path) {
  if ({{ variables['file-system-object'][0] }}.FileExists(path) == false){
    return 'File does not exist.';
  }
  {{ variables['file-system-object'][0] }}.DeleteFile(path);
  return 'Successfully deleted file.';
}
