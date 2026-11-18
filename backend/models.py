"""
Malleable C2 Data Models and AST Structures
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple


@dataclass
class Header:
    name: str
    value: str


@dataclass
class Parameter:
    name: str
    value: str


@dataclass
class TransformAction:
    action: str  # e.g., 'base64', 'base64url', 'netbios', 'netbiosu', 'mask', 'prepend', 'append'
    arg: str = ""  # argument if action is prepend/append


@dataclass
class TerminationAction:
    target: str  # 'print', 'header', 'parameter', 'uri-append'
    name: str = ""  # header name or parameter name


@dataclass
class TransformBlock:
    block_type: str  # 'metadata', 'id', 'output'
    transforms: List[TransformAction] = field(default_factory=list)
    termination: Optional[TerminationAction] = None


@dataclass
class ClientSubBlock:
    headers: List[Header] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    transform_blocks: Dict[str, TransformBlock] = field(default_factory=dict)  # 'metadata', 'id', 'output'


@dataclass
class ServerSubBlock:
    headers: List[Header] = field(default_factory=list)
    output: Optional[TransformBlock] = None


@dataclass
class HttpTransaction:
    verb: str = "GET"  # GET or POST
    uris: List[str] = field(default_factory=list)
    client: ClientSubBlock = field(default_factory=ClientSubBlock)
    server: ServerSubBlock = field(default_factory=ServerSubBlock)


@dataclass
class StageBlock:
    checksum: int = 0
    cleanup: bool = True
    sleep_mask: bool = True
    smartinject: bool = True
    stomppe: bool = True
    obfuscate: bool = True
    userwx: bool = False
    compile_time: str = ""
    magic_mz_x86: str = "MZRE"
    magic_mz_x64: str = "MZRE"
    magic_pe: str = "PE"
    transform_x86_prepend: str = ""
    transform_x86_append: str = ""
    transform_x64_prepend: str = ""
    transform_x64_append: str = ""
    raw_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessInjectBlock:
    allocator: str = "VirtualAllocEx"  # VirtualAllocEx or NtMapViewOfSection
    min_alloc: int = 4096
    startrwx: bool = False
    userwx: bool = False
    transform_x86: List[TransformAction] = field(default_factory=list)
    transform_x64: List[TransformAction] = field(default_factory=list)
    execute_order: List[str] = field(default_factory=lambda: [
        "CreateThread", "SetThreadContext", "CreateRemoteThread", "RtlCreateUserThread"
    ])
    raw_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PostExBlock:
    spawnto_x86: str = "%windir%\\syswow64\\werfault.exe"
    spawnto_x64: str = "%windir%\\sysnative\\werfault.exe"
    amsi_disable: bool = True
    keylogger: str = "GetAsyncKeyState"
    raw_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HttpsCertificate:
    CN: str = "microsoft.com"
    O: str = "Microsoft Corporation"
    OU: str = "Cloud Services"
    C: str = "US"
    ST: str = "WA"
    L: str = "Redmond"
    validity: int = 365
    raw_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Profile:
    name: str = "Untitled_Profile"
    sleeptime: int = 5000  # ms
    jitter: int = 20  # %
    data_jitter: int = 10  # %
    useragent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    pipename: str = "msagent_##"
    pipename_stager: str = "status_##"
    sample_name: str = "SecurityUpdate.exe"
    global_settings: Dict[str, Any] = field(default_factory=dict)

    http_get: HttpTransaction = field(default_factory=lambda: HttpTransaction(verb="GET"))
    http_post: HttpTransaction = field(default_factory=lambda: HttpTransaction(verb="POST"))
    http_stager: Optional[HttpTransaction] = None
    stage: StageBlock = field(default_factory=StageBlock)
    process_inject: ProcessInjectBlock = field(default_factory=ProcessInjectBlock)
    post_ex: PostExBlock = field(default_factory=PostExBlock)
    https_cert: HttpsCertificate = field(default_factory=HttpsCertificate)
    raw_blocks: Dict[str, str] = field(default_factory=dict)


@dataclass
class AuditIssue:
    rule_id: str
    category: str  # OPSEC, SYNTAX, EVASION, BEST_PRACTICE
    severity: str  # INFO, WARNING, CRITICAL
    message: str
    suggestion: str


@dataclass
class AuditReport:
    profile_name: str
    score: int  # 0 to 100
    grade: str  # A+, A, B, C, F
    issues: List[AuditIssue] = field(default_factory=list)
    passed_rules: List[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "CRITICAL")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "WARNING")

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "INFO")
