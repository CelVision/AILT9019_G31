# Deploy ConnectFour Connect

The application serves HTML, CSS, JavaScript, HTTP health checks and WebSockets from one origin. Players open a browser URL and do not install dependencies or supply API keys. Use one application instance and one worker: rooms and the matching queue live in process memory. Restarting the service ends active sessions.

This guide supplies runnable deployment configuration. A public deployment still requires a VPS, a domain, a trusted certificate and a successful check against the final URL. The current frontend's accessibility limitations are recorded in the [repository review](MIDTERM_REPOSITORY_REVIEW.md); deployment does not resolve them.

## Run with Docker Compose

Install Docker Engine/Desktop with Compose v2 supporting `up --wait`. From the repository root:

```bash
docker compose up --build --detach --wait --wait-timeout 120
docker compose ps
```

Open **http://127.0.0.1:8000/**. The published port is bound to loopback; public access is through Nginx below. The image runs as UID 10001; Compose gives it a read-only root filesystem, a temporary `/tmp`, no Linux capabilities and bounded logs. Docker health checks report process health; inspect unhealthy status explicitly because `restart: unless-stopped` only restarts an exited process.

Without a GLM key, the existing PvE handler uses a local legal-move fallback. To enable GLM, copy the example and edit it locally:

```bash
cp server/.env.example server/.env
# Set GLM_API_KEY in server/.env using your editor.
docker compose --env-file server/.env up --build --detach --wait --wait-timeout 120
```

Use the same `--env-file` option on subsequent deployment commands. On a VPS, use a protected file outside the checkout instead, such as `/etc/connectfour/connectfour.env`. Compose interpolates only the listed settings into the container; it does not bake the environment file into the image. The build context allowlist excludes environment files, Git history and local test data. Avoid displaying resolved Compose configuration when it contains a real key; use `docker compose config --quiet` to validate it.

Inspect logs and stop the service:

```bash
docker compose logs --tail 100 game
docker compose down
```

## Alternative native service on an Ubuntu VPS

Use either Compose or systemd on port 8000. For a native deployment, install Python 3.12+ with venv support and place a trusted checkout at `/var/www/AILT9019_G31`. Ensure `www-data` can traverse the checkout and read application files. Then:

```bash
cd /var/www/AILT9019_G31
python3 -m venv server/venv
server/venv/bin/python -m pip install -r server/requirements.txt
sudo install -d -m 750 -o root -g www-data /etc/connectfour
# Optional: create/edit /etc/connectfour/connectfour.env for GLM settings.
# Protect that file with root:www-data ownership and mode 640.
sudo install -m 644 deploy/connectfour.service /etc/systemd/system/connectfour.service
sudo systemctl daemon-reload
sudo systemctl enable --now connectfour
sudo systemctl status connectfour --no-pager
sudo journalctl -u connectfour -n 100 --no-pager
```

The environment file is optional; no key means local fallback. The service binds to `127.0.0.1:8000`, uses one worker and logs to journald without requiring a pre-created log directory. It uses `NoNewPrivileges`, a read-only system filesystem, a private temporary directory and restricted home-directory access. Keep the checkout outside user home directories, as shown above.

## Publish through Nginx HTTPS

1. Point the domain's DNS to the VPS. Allow inbound TCP 80 and 443 in both the host and provider firewall. Keep 8000 private.
2. Install Nginx and obtain a trusted certificate for the domain. Use a DNS challenge or a temporary HTTP-only site for the initial certificate: the supplied HTTPS template cannot load until its certificate files exist.
3. Copy `deploy/nginx.conf` to `/etc/nginx/sites-available/connectfour`. Replace **every** `connectfour.example.com`, including certificate paths, with the real domain. Review and resolve conflicting default sites before enabling it.
4. Enable the configuration and reload:

   ```bash
   sudo ln -s /etc/nginx/sites-available/connectfour /etc/nginx/sites-enabled/connectfour
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. Run the endpoint checker against the **final HTTPS origin**. The browser selects `wss://` automatically on HTTPS; Nginx forwards the upgrade at `/ws/game` to the application.
6. Verify certificate auto-renewal and the Nginx reload hook; with Certbot, use `sudo certbot renew --dry-run`.

## Check the deployed origin

On an operator machine with `server/requirements.txt` installed:

```bash
python deploy/check_public_url.py http://127.0.0.1:8000
python deploy/check_public_url.py https://your-real-domain.example --timeout 10
```

Use the local command for local checks and replace the example domain before a public check. The script requires healthy JSON, nonempty HTML/CSS/JS with appropriate content types, and a successful WebSocket upgrade plus ping/pong. HTTPS certificate validation remains enabled. Redirects fail deliberately: pass the final HTTPS origin so HTTP and WebSocket checks target the same service. A failed check exits with status 1. No player is registered and no LLM request is made.

The checker proves delivery/connectivity, not full game behavior. For acceptance, use synthetic nicknames and two compatible adult birth years in separate browsers; verify matchmaking, one move on both screens and a canned reaction. Separately verify the no-peer PvE path and its fallback notice. Record the tested commit, URL, date and observed result before claiming the service is live. Do not claim manual screen-reader or real-device accessibility validation from deployment checks.

## Update and roll back

Record the running commit and current image tag before an update. For Compose, tag each build with a commit ID using `CONNECTFOUR_IMAGE_TAG`:

```bash
CONNECTFOUR_IMAGE_TAG=<new-commit-id> docker compose --env-file /etc/connectfour/connectfour.env up --build --detach --wait --wait-timeout 120
```

Replace the angle-bracket placeholder before running. Preserve the previous image locally. If verification fails, restart that image without rebuilding:

```bash
CONNECTFOUR_IMAGE_TAG=<previous-commit-id> docker compose --env-file /etc/connectfour/connectfour.env up --no-build --detach --wait --wait-timeout 120
```

For native systemd, restore the previously tested application checkout and its dependency environment, restart `connectfour`, and rerun the checker. Both update and rollback interrupt active in-memory games. Keep secrets outside the checkout throughout.

## Automated verification

`.github/workflows/deployment.yml` runs Python tests, validates Compose/systemd configuration, builds the image, waits for container health, checks the non-root runtime and performs HTTP/WS checks. It also starts Nginx with the repository template and an ephemeral test certificate to verify HTTP redirection, HTTPS and WSS with certificate verification enabled. This is a CI test deployment, not publication to a real domain.

The configuration and tests adapt the deployment-only portions of historical commit `ca0b19e`. That earlier commit's UI accessibility changes remain reverted. See [CHANGELOG](../CHANGELOG.md) for scope and verification evidence.
