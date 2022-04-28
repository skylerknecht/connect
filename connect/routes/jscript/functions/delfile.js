function delfile(path) {
    fs = new ActiveXObject("Scripting.FileSystemObject")
    if (fs.FileExists(path) == false){
        return 'File does not exist.';
    }
    fs.DeleteFile(path);
    return 'Successfully deleted file.';
}