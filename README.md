# Cookie Munger
<img src="img/CookieMunger.png" style="float:right" width=25%>

This is a stupid idea.

It came about because of [a tweet](https://twitter.com/jrconlin/status/1369435923037970434) about sites that force you to accept cookies.

I looked at [a site](https://www.acehardware.com/) and noticed a bunch of fairly complicated cookies being stuffed into my browser. Since I work on backend stuff and know exactly how folks love to screw with anything you hand them, I decided to create something that screws with what they've given me.

Ideally, you give it a URL, it fetches and analyzes the cookies the site gave you, then
turns around and dumps random crap back at the site, that are almost, but not quite like what it just got.

Because cookies are delicious and edible.

So why not let some site's demographic and analytic database enjoy a few edibles?

## Installing

It's a python thing.

You probably want to run 
```
$ python3 -m venv venv
$ venv/bin/python3 setup.py develop
```
If you don't know what `venv` is, you can look or python virtualenv

After that...
```
venv/bin/munge -h
```
which will show he options.
