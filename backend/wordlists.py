"""
Malleable C2 Wordlists & High-Reputation Catalog
Provides authentic user-agents, URI paths, headers, and metadata for polymorphic generation.
"""

USER_AGENTS = [
    # Modern Chrome on Windows 11 / 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Modern Edge on Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.80",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
    # Modern Firefox on Windows 11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    # Safari on macOS Sonoma
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

SERVICE_TEMPLATES_DATA = {
    "amazon_cloudfront": {
        "service_name": "Amazon CloudFront CDN",
        "description": "Emulates high-speed static CDN edge distributions and video manifests.",
        "server_header": "CloudFront",
        "host": "d1v8l4e9k0r2.cloudfront.net",
        "get_uris": [
            "/cf/v2/stream/hls/live.m3u8",
            "/content/v1/assets/manifest.json",
            "/media/static/chunk_04.ts",
            "/api/cdn/v3/metrics/beacon.gif"
        ],
        "post_uris": [
            "/cf/v2/telemetry/report",
            "/analytics/event/collector",
            "/api/v1/feedback/log"
        ],
        "params": ["cf_id", "session_key", "sig", "token", "exp"],
        "headers": [
            ("Accept", "*/*"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("Sec-Fetch-Site", "cross-site"),
            ("Sec-Fetch-Mode", "no-cors"),
            ("Sec-Fetch-Dest", "empty")
        ],
        "cert": {
            "CN": "*.cloudfront.net",
            "O": "Amazon.com, Inc.",
            "OU": "CloudFront Infrastructure",
            "C": "US",
            "ST": "Washington",
            "L": "Seattle"
        }
    },
    "microsoft_onedrive": {
        "service_name": "Microsoft 365 & OneDrive Sync",
        "description": "Emulates enterprise SharePoint, MS Graph API and OneDrive delta synchronization.",
        "server_header": "Microsoft-IIS/10.0",
        "host": "api.onedrive.live.com",
        "get_uris": [
            "/v1.0/drive/root/delta",
            "/v2.0/users/me/drive/items",
            "/personal/sync/v3/changes",
            "/_api/v2.1/drives/syncFeed"
        ],
        "post_uris": [
            "/v1.0/drive/items/uploadSession",
            "/v2.0/telemetry/heartbeat",
            "/personal/sync/v3/batchCommit"
        ],
        "params": ["token", "drive_id", "filter", "client_request_id", "api-version"],
        "headers": [
            ("Accept", "application/json;odata.metadata=minimal"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("Sec-Ch-Ua-Mobile", "?0"),
            ("Sec-Ch-Ua-Platform", '"Windows"'),
            ("client-request-id", "b40d6c70-9d57-41fb-9921-2e650d0322bf")
        ],
        "cert": {
            "CN": "onedrive.live.com",
            "O": "Microsoft Corporation",
            "OU": "Microsoft 365 Core",
            "C": "US",
            "ST": "WA",
            "L": "Redmond"
        }
    },
    "google_analytics": {
        "service_name": "Google Analytics & Tag Manager",
        "description": "Disguises Beacon command channel inside standard gtag / GA4 telemetry beacons.",
        "server_header": "gws",
        "host": "www.google-analytics.com",
        "get_uris": [
            "/g/collect",
            "/gtag/js",
            "/j/collect",
            "/analytics/v2/measurement"
        ],
        "post_uris": [
            "/g/collect/batch",
            "/analytics/v2/events",
            "/gtm/debug/sync"
        ],
        "params": ["v", "tid", "cid", "sid", "_p", "en"],
        "headers": [
            ("Accept", "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("Cache-Control", "no-cache"),
            ("Sec-Fetch-Dest", "image")
        ],
        "cert": {
            "CN": "google-analytics.com",
            "O": "Google LLC",
            "OU": "Google Infrastructure",
            "C": "US",
            "ST": "California",
            "L": "Mountain View"
        }
    },
    "slack_api": {
        "service_name": "Slack Enterprise Webhooks & Polling",
        "description": "Blends seamlessly into Slack workplace real-time polling and message updates.",
        "server_header": "Apache",
        "host": "slack.com",
        "get_uris": [
            "/api/conversations.history",
            "/api/users.info",
            "/api/rtm.connect",
            "/api/client.counts"
        ],
        "post_uris": [
            "/api/chat.postMessage",
            "/api/views.publish",
            "/api/apps.event.authorizations.list"
        ],
        "params": ["token", "channel", "ts", "cursor", "limit"],
        "headers": [
            ("Accept", "application/json, text/javascript, */*; q=0.01"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("X-Slack-Req-Id", "9b8e23f1-33cb-4dbb-8215-618451892182")
        ],
        "cert": {
            "CN": "*.slack.com",
            "O": "Slack Technologies LLC",
            "OU": "Engineering",
            "C": "US",
            "ST": "CA",
            "L": "San Francisco"
        }
    },
    "cloudflare_cdn": {
        "service_name": "Cloudflare Edge Workers & Ray ID",
        "description": "Imitates Cloudflare CDN caching, Worker script endpoints and Ray-ID headers.",
        "server_header": "cloudflare",
        "host": "workers.cloudflare.com",
        "get_uris": [
            "/cdn-cgi/trace",
            "/api/v4/client/v4/accounts",
            "/edge/v1/cache/sync",
            "/cdn-cgi/rum"
        ],
        "post_uris": [
            "/cdn-cgi/beacon/performance",
            "/api/v4/graphql",
            "/edge/v1/telemetry/submit"
        ],
        "params": ["cf_chl_prog", "ray_id", "sitekey", "version"],
        "headers": [
            ("Accept", "*/*"),
            ("Accept-Language", "en-US,en;q=0.5"),
            ("CF-Device-Type", "desktop")
        ],
        "cert": {
            "CN": "*.cloudflare.com",
            "O": "Cloudflare, Inc.",
            "OU": "Edge Security",
            "C": "US",
            "ST": "California",
            "L": "San Francisco"
        }
    },
    "github_api": {
        "service_name": "GitHub REST API v3",
        "description": "Emulates developer activity against the GitHub REST API and raw file assets.",
        "server_header": "GitHub.com",
        "host": "api.github.com",
        "get_uris": [
            "/repos/octocat/Hello-World/commits",
            "/user/notifications",
            "/rate_limit",
            "/meta"
        ],
        "post_uris": [
            "/repos/octocat/Hello-World/dispatches",
            "/collector/activity",
            "/telemetry/agent/logs"
        ],
        "params": ["per_page", "page", "since", "token"],
        "headers": [
            ("Accept", "application/vnd.github.v3+json"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("X-GitHub-Media-Type", "github.v3; format=json")
        ],
        "cert": {
            "CN": "*.github.com",
            "O": "GitHub, Inc.",
            "OU": "Production Operations",
            "C": "US",
            "ST": "California",
            "L": "San Francisco"
        }
    }
}

SAFE_SPAWNTO_X86 = [
    "%windir%\\syswow64\\werfault.exe",
    "%windir%\\syswow64\\svchost.exe",
    "%windir%\\syswow64\\runtimebroker.exe",
    "%windir%\\syswow64\\dllhost.exe",
    "%windir%\\syswow64\\gpupdate.exe"
]

SAFE_SPAWNTO_X64 = [
    "%windir%\\sysnative\\werfault.exe",
    "%windir%\\sysnative\\svchost.exe",
    "%windir%\\sysnative\\runtimebroker.exe",
    "%windir%\\sysnative\\dllhost.exe",
    "%windir%\\sysnative\\gpupdate.exe"
]

NAMED_PIPES = [
    "msagent_##",
    "spoolss_##",
    "win_security_##",
    "wkssvc_##",
    "eventlog_##",
    "samr_##"
]
