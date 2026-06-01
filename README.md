# WhiteDns TG

WhiteDns TG is an Android Telegram MTProto proxy client with English and Farsi interfaces. It opens a local proxy on the phone and can route Telegram through a rotating Smart CDN list, an operator-controlled private front domain, an experimental Google-backed compatible domain, or direct Telegram data-center addresses.

> WhiteDns TG is not a full-device VPN. It only handles Telegram traffic after the proxy link is applied inside Telegram.

## Start Here

For normal users:

1. Install the APK from the GitHub Releases page.
2. Open WhiteDns TG and leave `Smart CDN` selected.
3. Tap the large logo to start the local proxy.
4. Tap `Check`.
5. When the app reports `Route works`, tap `Apply in Telegram`.
6. Confirm the proxy inside Telegram.

For complete instructions, settings explanations, custom-domain setup, and troubleshooting:

- [English user guide](docs/USER_GUIDE_EN.md)
- [راهنمای کامل فارسی](GUIDE_FA.md)

## Important Custom-Domain Rule

A purchased domain is not automatically a working front domain. Private and Google-front modes require a domain that you own or are authorized to manage, working DNS for `kws1` through `kws5` and `kws203`, TLS, WebSocket support, and a compatible `/apiws` endpoint.

Do not enter `google.com`, `youtube.com`, or unrelated third-party hostnames. WhiteDns TG does not discover or deploy front servers automatically.

## Main Features

- Local Telegram MTProto proxy on `127.0.0.1:1443`.
- One-tap Telegram proxy link.
- Smart CDN routing with WebSocket/TLS and direct fallback.
- Private front mode for user-controlled compatible domains.
- Experimental Google-front mode for authorized Google-backed compatible domains.
- Direct Telegram DC mode for comparison and fallback testing.
- Active route validation, repair, and automatic health checks.
- English and Farsi interface.
- Foreground service, optional autostart, and diagnostic logs.

## How It Works

```text
Telegram -> 127.0.0.1:1443 -> WhiteDns TG native Go core
         -> TLS WebSocket front (/apiws) or direct Telegram DC
```

`Connected` means the local Android proxy process is running. It does not prove the internet route is usable. Press `Check` and wait for `Route works` before applying the link in Telegram.

## Build From Source

Requirements:

- Android SDK with NDK `28.2.13676358`
- Java compatible with the Gradle wrapper
- Go toolchain when rebuilding native libraries

Build the Android APK:

```powershell
.\gradlew.bat assembleDebug
```

Universal APK output:

```text
app/build/outputs/apk/debug/app-universal-debug.apk
```

## Security and Responsible Use

- Use only domains and infrastructure you own or are authorized to configure.
- Keep private domains and proxy secret keys private.
- Test routes on the networks where they will be used. No front provider is guaranteed to work on every ISP.
- Review the terms and acceptable-use policies of your domain, CDN, and hosting providers.

## License and Provenance

This project is distributed under GPLv3. The original `tg-ws-proxy` core by Flowseal is MIT licensed. WhiteDns TG includes substantial Android UI, routing diagnostics, localization, branding, and stability changes.
