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

## What the hell does this do?

Cookies are little bits of data that a site wants you to hold for it. When you come back, your browser is supposed to send back the same bits of data.

Cookie munger, well, munges the values that get returned.

I could have just made up a bunch of random crap and returned that. But, well, that's no fun. I mean it is, but it's not really fun.

No, cookie munger is a bit more clever about things. 

If a cookie looks like a date, cookie_munger picks a random date from the UNIX EPOCH and returns it.

If it's a number, cookie munger returns a random number of equal digits.

If a it looks like base64 encoded JSON blob, cookie munger decodes, analyzes the JSON and returns appropriately munged values for each of the associated key values, then re-encodes it back into base64.

etc. (because it definitely does etc.)

It will then return new, randomly generated values as many times as you tell it because, yeah, why not?

The idea is basically to provide "interesting" results to whatever analytics engine may be accepting the data from the parsed cookie it just got back. Maybe then sites might not be quite as quick to dole out cookies to folks when they first show up, because who knows what sort of fun things they might get back?
