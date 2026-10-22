# Deploy to svp.walterslabs.dev

The inspected VPS is Ubuntu 24.04 with Python 3.12, Nginx and Certbot, about
1 GiB RAM and 16 GiB free disk. Docker is not installed. Use the native service
below; port 8010 was unused when inspected. These instructions do not modify
other sites. Resolve CaseSumm's conflicting published license statements before
public hosting; see CASESUMM_REVIEW.md. No deployment has been performed.

## Prepare locally

```sh
make test
make release
```

This produces `artifacts/scvpublic-release.tar.gz`, containing the package,
pinned serving requirements, deployment configurations, acceptance script,
license, SQLite artifact and SHA256SUMS. Raw sources, tokens, notebooks and
scientific dependencies are excluded. The artifact is copied with mode 0644
for the unprivileged service. The bundle is private build output, not a Git asset.

Local acceptance on the full artifact: 160 Flask test-client requests, two
threads, approximately 47 MiB peak process RSS and under 20 ms maximum request
latency on the development Mac. This excludes Gunicorn's master and Linux
filesystem cache, and is not a VPS capacity measurement. Repeat the check on
Linux and inspect the systemd memory total under real HTTP load.

## Install a release

Choose a unique release directory, for example `20261022-1`. Never replace
files inside a running release. Transfer the bundle:

```sh
scp artifacts/scvpublic-release.tar.gz application_server:/tmp/scvpublic-release.tar.gz
ssh application_server
```

On the VPS (commands requiring root use sudo):

```sh
sudo apt-get install python3-venv
sudo install -d -m 755 /opt/scvpublic/releases/20261022-1
sudo tar -xzf /tmp/scvpublic-release.tar.gz -C /opt/scvpublic/releases/20261022-1
cd /opt/scvpublic/releases/20261022-1
sha256sum -c SHA256SUMS
sudo python3 -m venv .venv
sudo .venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=. .venv/bin/python scripts/check_serving.py artifacts/search.sqlite
sudo ln -s /opt/scvpublic/releases/20261022-1 /opt/scvpublic/current.next
sudo mv -Tf /opt/scvpublic/current.next /opt/scvpublic/current
sudo cp deploy/scvpublic.service /etc/systemd/system/scvpublic.service
sudo systemd-analyze verify /etc/systemd/system/scvpublic.service
sudo systemctl daemon-reload
sudo systemctl enable --now scvpublic
# For subsequent releases, restart even if already running:
sudo systemctl restart scvpublic
curl --fail http://127.0.0.1:8010/healthz
curl --fail 'http://127.0.0.1:8010/?q1=gun+control' -o /dev/null
sudo systemctl show scvpublic -p MemoryCurrent -p MemoryPeak -p NRestarts
sudo journalctl -u scvpublic -n 50 --no-pager
```

The service uses a dynamic non-root identity, read-only system access, private
temporary files, one worker and two threads. MemoryHigh=160M and MemoryMax=192M
are initial budgets, not validated VPS limits. Check host memory alongside the
other services before exposing the site. Do not raise worker count by default.

## DNS and HTTPS activation

Create an A record for `svp.walterslabs.dev` pointing to the VPS IPv4 address.
Add AAAA only if IPv6 is configured and reachable. After DNS resolves correctly:

```sh
sudo cp /opt/scvpublic/current/deploy/svp.walterslabs.dev.conf /etc/nginx/sites-available/svp.walterslabs.dev
sudo ln -s /etc/nginx/sites-available/svp.walterslabs.dev /etc/nginx/sites-enabled/svp.walterslabs.dev
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d svp.walterslabs.dev --redirect
curl --fail https://svp.walterslabs.dev/healthz
curl --fail 'https://svp.walterslabs.dev/?q1=gay+marriage' -o /dev/null
sudo certbot renew --dry-run
```

Install the Nginx file only on first setup; subsequent application releases must
not overwrite Certbot's generated TLS configuration. Verify the chart and both
result lists in a browser, including abortion, gay marriage, gun control, empty
and unmatched searches. Broad terms may be absent from the Court vocabulary
because of the original maximum-document-frequency filter.

## Updates and rollback

Keep the previous release directory. Build and verify a new bundle locally,
extract to a new directory, install its venv and run its acceptance check. Switch
`current` with the temporary symlink and atomic `mv -Tf` above, then restart the
service and check health. Rollback uses the same operation pointing to the
previous release, followed by restart. This keeps code and artifact together.
Do not rebuild the matrix on the VPS or modify an active SQLite file in place.
Keep raw sources, mapping versions and provenance manifests backed up locally.

## Optional Docker deployment

The checked-in Dockerfile and Compose configuration remain supported by CI.
Docker is not required on this VPS. For a local container smoke test:

```sh
make demo
chmod 644 artifacts/demo.sqlite
SCVPO_ARTIFACT_PATH=./artifacts/demo.sqlite docker compose up --build -d --wait
curl --fail http://127.0.0.1:8000/healthz
docker compose down
```

For real data, set SCVPO_ARTIFACT_PATH to the absolute artifact path and ensure
UID 10001 can read it. Compose binds localhost:8000 and caps memory at 384 MiB;
choose one deployment route. Recreate the container after replacing a mounted
artifact because a bind mount can retain the old inode. The base image is
version-tagged rather than digest-locked. Local Docker validation requires a
Docker installation; the native acceptance check does not validate containers.
