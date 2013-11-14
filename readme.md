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
