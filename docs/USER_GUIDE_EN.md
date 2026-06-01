# WhiteDns TG User Guide

This guide explains installation, every setting, custom front domains, route checking, and troubleshooting. It is written for users who do not already understand proxies or DNS.

## 1. What the App Does

WhiteDns TG creates a local Telegram MTProto proxy on your Android phone:

```text
Telegram -> 127.0.0.1:1443 -> WhiteDns TG
         -> TLS WebSocket front or direct Telegram DC
```

It is not a full-device VPN. Other applications do not use this route.

## 2. Normal Installation and First Connection

1. Install the APK from the GitHub Releases page.
2. Open WhiteDns TG.
3. Open `Settings`.
4. Select `Smart CDN`.
5. Keep port `1443` and `WS pool` value `2` or `4`.
6. Return to `Proxy`.
7. Tap the large WhiteDns TG logo.
8. Wait for `Connected`.
9. Tap `Check`.
10. When you see `Route works`, tap `Apply in Telegram`.
11. Confirm the proxy inside Telegram.

`Connected` only means the local proxy started. The separate `Check` button tests whether an outbound route is currently usable.

## 3. Route Modes

### Smart CDN

Recommended for most users. The app rotates through its built-in WebSocket front list and can fall back to direct Telegram data centers. No personal domain is required.

If DNS resolves a Smart CDN hostname but that Cloudflare edge times out, `Check` automatically tests a small bounded set of official Cloudflare IPv4 candidates. A working candidate is cached temporarily. Failed candidates are quarantined briefly and scans are rate-limited to protect battery and avoid unnecessary traffic. This is automatic; users do not need to enter Cloudflare IP addresses.

### Private Front

For operators who control a compatible domain. This can be more stable than shared public fronts because the operator controls the DNS and can rotate domains when needed.

### Google Front

Experimental. This is for an authorized custom domain attached to a Google-backed setup that actually supports the required TLS WebSocket endpoint. It is not a method for entering a public Google hostname.

### Direct DC

Connects directly to Telegram data-center addresses. Use this to compare routes or when front domains are unstable.

## 4. Every Setting

| Setting | Meaning | Recommended value |
| --- | --- | --- |
| Route provider | Chooses Smart CDN, Private front, Google front, or Direct DC | Start with Smart CDN |
| Port | Local Android proxy port used by Telegram | `1443` |
| WS pool | Number of prepared WebSocket connections | `2` for lower resource use, `4` for balance |
| Secret key | Local MTProto proxy key used in the Telegram link | Keep the generated value unless intentionally invalidating an old link |
| Autostart | Starts the proxy again after device restart | Optional |
| Validate domain | Tests DNS and the TLS WebSocket handshake for a custom domain | Use before starting Private or Google front |

## 5. What a Custom Front Domain Is

A domain name by itself is not enough. WhiteDns TG expects a compatible TLS WebSocket route at:

```text
wss://kws2.example.com/apiws
```

For Telegram data centers, prepare these hostnames under your base domain:

```text
kws1.example.com
kws2.example.com
kws3.example.com
kws4.example.com
kws5.example.com
kws203.example.com
```

When the app asks for the base domain, enter:

```text
example.com
```

Do not enter:

```text
kws2.example.com
https://example.com
https://kws2.example.com/apiws
```

The repository contains the Android client. It does not contain a one-click server-side front deployment. The domain must already lead to a compatible `/apiws` endpoint.

## 6. How to Obtain a Domain

Use a domain you own or are authorized to manage:

1. Buy a domain from any reputable registrar, or use an existing domain you control.
2. Confirm that you can edit DNS records.
3. Decide where the compatible WebSocket `/apiws` endpoint will run.
4. Create the required `kws` DNS records.
5. Validate the base domain inside WhiteDns TG.

Do not search for random public domains to reuse. A third-party hostname can stop working without notice, may violate the provider's rules, and does not become a compatible route merely because it is hosted by a large provider.

## 7. Private Cloudflare Front Setup

Cloudflare is suitable only when your origin or edge worker already handles the required `/apiws` WebSocket path.

1. Add your domain to Cloudflare and complete nameserver activation.
2. In the Cloudflare dashboard open `DNS` -> `Records`.
3. Create `A`, `AAAA`, or `CNAME` records for:

```text
kws1
kws2
kws3
kws4
kws5
kws203
```

4. Point each record to your compatible origin or edge endpoint.
5. Enable Cloudflare proxying for the web-traffic records. Cloudflare calls this `Proxied` or orange-cloud status.
6. In Cloudflare open `Network` and ensure `WebSockets` is enabled.
7. Confirm TLS is valid for the required hostnames.
8. In WhiteDns TG open `Settings`.
9. Stop the proxy before changing modes.
10. Select `Private front`.
11. Enter only your base domain, such as `example.com`.
12. Tap `Validate domain`.
13. Start the proxy, return to `Proxy`, and tap `Check`.

Cloudflare documents that proxied WebSockets are supported and that proxied DNS records cause Cloudflare to receive requests before the origin:

- [Cloudflare WebSockets documentation](https://developers.cloudflare.com/network/websockets/)
- [Cloudflare DNS record documentation](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/)

## 8. Google Front Setup

Google front is experimental because Google-hosted products differ in WebSocket behavior, custom-domain features, and routing behavior. WhiteDns TG does not bypass those differences.

Use this mode only when:

- You own or are authorized to manage the base domain.
- Your Google-backed architecture supports TLS WebSockets.
- The domain exposes the compatible `/apiws` endpoint.
- The required `kws` hostnames resolve correctly.
- `Validate domain` succeeds in the app.

Do not enter:

```text
google.com
youtube.com
firebaseapp.com
run.app
```

Public provider domains are not personal front domains. For a Google-backed deployment, configure your own custom domain according to the service you operate. Google Cloud documents several custom-domain options for Cloud Run, including a global external Application Load Balancer, Firebase Hosting, and limited Cloud Run domain mapping:

- [Google Cloud Run custom-domain documentation](https://docs.cloud.google.com/run/docs/mapping-custom-domains)

After your own compatible endpoint exists:

1. Stop WhiteDns TG.
2. Select `Google front`.
3. Enter your base domain only.
4. Tap `Validate domain`.
5. Start the proxy and tap `Check`.

If validation fails, the route is not compatible. Use Smart CDN, Direct DC, or repair the server-side setup.

## 9. How to Test and Compare Domains

For each authorized custom domain:

1. Test the domain with `Validate domain`.
2. Start the proxy.
3. Tap `Check`.
4. Apply the link in Telegram only after `Route works`.
5. Test message delivery and media loading.
6. Repeat on the networks where users will connect.

Keep notes for each ISP and domain. A route that works on Wi-Fi may fail on mobile data, and provider behavior can change over time.

## 10. Common Messages

### `Local port is not responding`

The local Android proxy did not start correctly.

1. Tap `Repair`.
2. Stop and start the proxy.
3. If needed, change port `1443` to another unused port such as `2083`.
4. Restart the app.

### `Local proxy is ready. Press Check to test the route.`

This is not an error. Tap `Check`.

### `Route failed`

The local proxy started, but the outbound route failed.

1. Tap `Repair`.
2. Try another network.
3. Try `Direct DC`.
4. If using a custom domain, validate the domain and review DNS, TLS, and `/apiws`.

### `Enter a front domain first`

Private and Google-front modes require a base domain.

### Telegram does not connect after `Route works`

1. Tap `Apply in Telegram`.
2. Confirm the new proxy in Telegram.
3. Remove stale proxy entries if needed.
4. Close and reopen Telegram.

## 11. Security Checklist

- Use only infrastructure you own or are allowed to manage.
- Do not publish your secret key.
- Do not claim a route is guaranteed to work on every ISP.
- Keep backup domains for private deployments.
- Review provider acceptable-use policies.
- Validate routes after DNS or backend changes.

## 12. Recommended Starting Values

Normal user:

```text
Route provider: Smart CDN
Port: 1443
WS pool: 2 or 4
```

Private operator:

```text
Route provider: Private front
Front base domain: your authorized compatible domain
Port: 1443
WS pool: 4
```
