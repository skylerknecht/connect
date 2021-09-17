function dir(path){
  if({{ variables['file-system-object'][0] }}.FolderExists(path) == false){
    return 'Folder does not exist.';
  }

  folder = {{ variables['file-system-object'][0] }}.GetFolder(path);

  results = 'Directory is in the ' + folder.drive + ' drive\n';
  results = results + 'Directory of ' + path + '\n\n';

  files = folder.files;
  var enumerator = new Enumerator(files);
  enumerator.moveFirst();
  while(enumerator.atEnd() == false){
    var file = enumerator.item();
    try {
      results = results + file.datecreated + '\t<' + file.type.toUpperCase().slice(0,13) + '>\t(' + (file.size/1000000).toFixed(3) + ' MB)\t' + file.name + '\n';
    } catch (e) {
      results = results;
    }
    enumerator.moveNext();
  }

  folders = folder.subFolders;
  var enumerator = new Enumerator(folders);
  enumerator.moveFirst();
  while(enumerator.atEnd() == false){
    var sub_folder = enumerator.item();
    try {
      results = results + sub_folder.datecreated + '\t<' + sub_folder.type.toUpperCase().slice(0,13) + '>\t(' + (sub_folder.size/1000000).toFixed(3) + ' MB)\t' + sub_folder.name + '\n';
    } catch (e) {
      results = results;
    }
    enumerator.moveNext();
  }

  return results;
}
