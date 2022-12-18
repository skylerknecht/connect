$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:6900/', {"sync disconnect on unload": true });

    socket.on('implants', function(msg) {
        console.log('implant from server');
        console.log(msg);
    });

    socket.on('connect', function(){
        console.log('On connect');
        var implant = {
            "implant_name":"CSHARP_EXE",
            "language":"CSHARP"
        };
        socket.emit('implants', implant);
    });

    $("#authbutton").on("click", function(){
        var auth = {
            "connection": true,
            "token": "4666325248"
        }
        socket.emit('authenticate', auth);
    });
});