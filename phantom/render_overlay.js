var system = require('system');
var page = require('webpage').create();
var fs = require('fs');

function pack_uint32(num){
  var s='';

  var n = num & 0xffffffff;

  s+=String.fromCharCode((n & 0xff000000) >>> 24);
  s+=String.fromCharCode((n & 0x00ff0000) >>> 16);
  s+=String.fromCharCode((n & 0x0000ff00) >>>  8);
  s+=String.fromCharCode((n & 0x000000ff));

  return s;
}

//data=atob(page.renderBase64());
//data=page.renderBase64();
//system.stdout.write(pack_uint32(data.length));
//system.stdout.write(data);
//page.render('./test_true.png');
//console.log(page.renderBase64('BMP'));


function output_image(page, filename, format) {

    if (format == "svg") {
        var outfile = fs.open(filename, 'w');
        var length = page.content.length;
        outfile.writeLine(length);
        outfile.writeLine(page.content);
        outfile.close();
    }
    else if (format == "raw") {
        var outfile = fs.open(filename, 'w');
        //var timestamp = "2GMFP4k41UE=";
        //outfile.write(atob(timestamp));
        var timestamp = 123126412.12783871523;
        outfile.writeLine(timestamp);
        var length = 4 * page.viewportSize.width * page.viewportSize.height;
        //outfile.write(pack_uint32(length));
        outfile.writeLine(length);
        outfile.close();
        page.render(filename, {format: 'raw'});

    }
    else {
        system.stderr.writeLine("ERROR: Format not supported.");
    }
}

page.viewportSize = { width: 1280, height: 720 };
page.open('images/soccer.svg', function() {
    interval = setInterval(function(){
        output_image(page, '/dev/stdout', 'raw');
        system.stderr.writeLine("OK.");
    }, 10);
});

