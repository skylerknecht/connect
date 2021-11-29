function retrieve(path, format) {
  if ({{ variables['file-system-object'][0] }}.FileExists(path) == false){
    return path + ' does not exist.';
  }
  var stream = new ActiveXObject("ADODB.Stream");
  stream.Open();
  if(format == 'string'){
    stream.Charset = 'utf-8';
    stream.Type = 2;
    stream.LoadFromFile(path);
    stream.Position = 0;
    data = stream.ReadText();
    stream.Close();
    return data;
  }
  stream.Type = 1;
  stream.LoadFromFile(path);
  stream.Position = 0;
  data = stream.Read();
  stream.Close();
  return data;
}
