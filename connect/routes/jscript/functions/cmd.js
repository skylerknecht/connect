function cmd(command) {
  stdout_path = 'C:\\Windows\\Temp\\HFEWIFDKASD.txt';
  fs = new ActiveXObject("Scripting.FileSystemObject")
  if (fs.FileExists(stdout_path)) {
    return stdout_path + ' already exists, please remove before running commands.';
  }
  command = 'cmd.exe /q /c ' + command + ' 1> ' + stdout_path + ' 2>&1';
  try {
    wscriptshell.Run(command, 0, true);
    results = 'Executed ( ' + command + ' )\n\n';
    results = results + retrieve(stdout_path, 'string');
    delfile(stdout_path);
    return results;
  } catch (e) {
    return 'Failed to run ' + command + ': ' + e.message;
  }
}