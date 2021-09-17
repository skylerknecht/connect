function mvfile(source, destination) {
  if ({{ variables['file-system-object'][0] }}.FileExists(source) == false){
    return 'Source file does not exist.';
  }
  if ({{ variables['file-system-object'][0] }}.FileExists(destination) == true){
    return 'Destination file already exists.';
  }
  {{ variables['file-system-object'][0] }}.MoveFile(source, destination);
  return 'Successfully moved file.'
}
