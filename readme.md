Philippines cash infrastructure
===
In order to distribute cash usefully, we want to know what the
cash infrastructure looks like. We're starting with
[post offices](https://www.phlpost.gov.ph/post-office-location.php)
because those tend to be available in even rural areas.

Run like so.

```sh
git submodule init
git submodule update
./post.py
ls data/postoffices/*/postoffices.csv
```

> hey tom, you'll notice we have some administrative units underneath
> municipality. these are barangays. the problem is that I can't geocode
> these guys based on muni because there are some repeating muni names -- see
> Davao city. Hence the need for a breakout. Think you can get teh barangays
> (adm4)?
