var system = require('system');
var fs = require('fs');
var casper_module = require("casper");
var pageSettings = {
    userAgent: 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    loadImages: false
};
var casper = casper_module.create({
        pageSettings: pageSettings
});
var x = require('casper').selectXPath;
var url = casper.cli.get("url");
//var name = 'xxxx'
//var passwd = 'xxxx'
var name = 'xxxx'
var passwd = 'xxxx'
var need_login = false
var login_url = ''
var debugOn = false
//url = 'https://login.taobao.com/member/login.jhtml?style=b2b&amp;css_style=b2b&amp;from=b2b&amp;newMini2=true&amp;full_redirect=true&amp;redirect_url=https%3A%2F%2Flogin.1688.com%2Fmember%2Fjump.htm%3Ftarget%3Dhttps%253A%252F%252Flogin.1688.com%252Fmember%252FmarketSigninJump.htm%253FDone%253Dhttp%25253A%25252F%25252Fmember.1688.com%25252Fmember%25252Foperations%25252Fmember_operations_jump_engine.htm%25253Ftracelog%25253Dlogin%252526operSceneId%25253Dafter_pass_from_taobao_new%252526defaultTarget%25253Dhttp%2525253A%2525252F%2525252Fwork.1688.com%2525252F%2525253Ftracelog%2525253Dlogin_target_is_blank_1688&amp;reg=http%3A%2F%2Fmember.1688.com%2Fmember%2Fjoin%2Fenterprise_join.htm%3Flead%3Dhttp%253A%252F%252Fmember.1688.com%252Fmember%252Foperations%252Fmember_operations_jump_engine.htm%253Ftracelog%253Dlogin%2526operSceneId%253Dafter_pass_from_taobao_new%2526defaultTarget%253Dhttp%25253A%25252F%25252Fwork.1688.com%25252F%25253Ftracelog%25253Dlogin_target_is_blank_1688%26leadUrl%3Dhttp%253A%252F%252Fmember.1688.com%252Fmember%252Foperations%252Fmember_operations_jump_engine.htm%253Ftracelog%253Dlogin%2526operSceneId%253Dafter_pass_from_taobao_new%2526defaultTarget%253Dhttp%25253A%25252F%25252Fwork.1688.com%25252F%25253Ftracelog%25253Dlogin_target_is_blank_1688%26tracelog%3Dlogin_s_reg'

var print = function(msg){
    if (debugOn){
       console.log(msg);
    }
}
    

casper.start(url, function() {
    this.wait(1000)
    this.capture("first_cap.png");
    content = casper.page.content;
    fs.write('first_page.html', content, "w");
    if (content.search('name="TPL_username"') && content.search('name="TPL_password"')){
        login_url = this.getElementAttribute(x("//div[@id='tblogin']/iframe"), 'src');
        if (login_url){
            need_login = true;
            print("need to login.");
            print('login_url:')
            print(login_url)
        }
    }

});

casper.then(function () {
    if (need_login){

        this.open(login_url).then(function() {
            this.wait(500);
            this.capture('login_page.png');
            fs.write('login_page.html', content, "w");
        });
    }
});

//为登录准备
casper.then(function () {
    if (need_login){
        print("try to login");

        this.sendKeys('#TPL_username_1', name, { keepFocus: false });

        this.wait(100)

        this.sendKeys('#TPL_password_1', passwd, { keepFocus: false });

        this.wait(100)

        this.capture("wait_to_login.png");
        print("wait to login");
        this.click(x('//*[@id="J_SubmitStatic"]'));
        this.wait(500)
        this.wait(5000, function () {
            this.capture("login_success.png");
            print("登录成功");
            content = casper.page.content;
            fs.write('login_success.html', content, "w");
        });
    }

});

casper.then(function () {
    if (need_login){
        this.open(url).then(function() {
            this.wait(500)
        });
    }
    this.capture("real_page.png");
    console.log(casper.page.content);

});
casper.run();
