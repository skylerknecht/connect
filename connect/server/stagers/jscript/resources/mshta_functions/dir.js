function dir(path) {
  try {
    fs = new ActiveXObject("Scripting.FileSystemObject");
    if (fs.FolderExists(path) == false) {
      return b64e('Folder does not exist.');
    }
    folder = fs.GetFolder(path);

    results = results + '  Directory of ' + path + '\n\n';

    files = folder.files;
    var enumerator = new Enumerator(files);
    enumerator.moveFirst();
    while (enumerator.atEnd() == false) {
      var file = enumerator.item();

      try {
        date = new Date(file.datecreated)
        results = results + date.getMonth() + '/' + date.getDay() + '/' + date.getYear() +  ' ' + date.toLocaleTimeString() + '\t';
      } catch (e) {
        results = results + 'X\t'
      }

      try {
        results = results + '<FILE>\t'
      } catch (e) {
        results = results + '<X>\t'
      }

      try {
        results = results + '(' + (file.size / 1000000).toFixed(3) + ' MB)\t'
      } catch (e) {
        results = results + '(X)\t\t'
      }

      try {
        results = results + file.name + '\n';
      } catch (e) {
        results = results + 'X\n'
      }

      enumerator.moveNext();
    }

    folders = folder.subFolders;
    var enumerator = new Enumerator(folders);
    enumerator.moveFirst();
    while (enumerator.atEnd() == false) {
      var sub_folder = enumerator.item();

      try {
        date = new Date(sub_folder.datecreated)
        results = results + date.getMonth() + '/' + date.getDay() + '/' + date.getYear() +  ' ' + date.toLocaleTimeString()  + '\t';
      } catch (e) {
        results = results + 'X\t'
      }
      
      try {
        results = results + '<DIR>\t'
      } catch (e) {
        results = results + '<X>\t'
      }

      try {
        results = results + '(' + (sub_folder.size / 1000000).toFixed(3) + ' MB)\t'
      } catch (e) {
        results = results + '(X)\t\t'
      }

      try {
        results = results + sub_folder.name + '\n';
      } catch (e) {
        results = results + 'X\n'
      }

      enumerator.moveNext();
    }
    return b64e(results);
  } catch (e) {
    return b64e(e.message);
  }
}