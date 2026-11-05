# GeoLite2 Country database

Place the MaxMind binary country database at:

```text
backend/geoip/GeoLite2-Country.mmdb
```

Install the Python reader in every local or production environment:

```text
python -m pip install geoip2
```

Alternatively, set `GEOIP_COUNTRY_DB` to an absolute `.mmdb` path before
starting Django.

The database must be downloaded from the MaxMind account portal using an
account ID and an active license key. Do not commit the database archive,
database file, account ID, or license key to Git.

After replacing or updating the database, restart the Django process so the
cached GeoIP reader reopens the new file.
