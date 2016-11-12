var page = require('webpage').create();
var system = require('system');
var fs = require('fs');
page.settings.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36';
url = system.args[1];
page.open(url, function(status) {
//  console.log("Status: " + status);
  if(status === "success") {
    page.render('example.png');
    fs.write('phantom.html', page.content, 'w');
    console.log(page.content);
  } else {
//    console.log('no example.png');
  }
  phantom.exit();
});
