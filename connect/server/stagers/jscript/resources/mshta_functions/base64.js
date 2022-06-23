function str2bin(data) {
  var istream = new ActiveXObject("ADODB.Stream");
  istream.Type = 2
  istream.CharSet = "us-ascii"
  istream.Open()
  istream.WriteText(data)
  istream.Position = 0
  istream.Type = 1
  return istream.Read()
}

function b64e(data) {
  var xml = new ActiveXObject("MSXml2.DOMDocument");
  var element = xml.createElement("Base64Data");
  element.dataType = "bin.base64";
  if(typeof(data) == "string") {
    element.nodeTypedValue = str2bin(data);
  }
  else {
    element.nodeTypedValue = data;
  }
  return element.text.replace(/\n/g, "");
}

function bin2str(data) {
  var istream = new ActiveXObject("ADODB.Stream")
  istream.Type = 1
  istream.Open()
  istream.Write(data)
  istream.Position = 0
  istream.Type = 2
  istream.CharSet = "us-ascii"
  return istream.ReadText()
}

function b64d(data, type) {
  var xml = new ActiveXObject("MSXml2.DOMDocument");
  var element = xml.createElement("Base64Data");
  element.dataType = "bin.base64"
  element.text = data
  if(type == "bin") {
    return element.nodeTypedValue
  }
  else {
    return bin2str(element.nodeTypedValue)
  }
}





