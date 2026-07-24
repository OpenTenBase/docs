#!/usr/bin/env python3
import argparse
import configparser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = {
    "zh": ROOT / "docs/guide/15-docker-deploy.md",
    "en": ROOT / "docs/guide/15-docker-deploy.en.md",
}
DEVENV_FILES = ("README.md", "config.ini", "docker-compose.yml", "otb-dev.sh")
SERVICES = {"gtm", "cn", "dn01", "dn02"}
IPS = {
    "gtm": "172.20.0.2",
    "cn": "172.20.0.3",
    "dn01": "172.20.0.4",
    "dn02": "172.20.0.5",
}
COMMANDS = (
    "git clone https://github.com/OpenTenBase/OpenTenBase-DevEnv.git",
    "cd OpenTenBase-DevEnv",
    "git checkout example-distributed",
    "./otb-dev.sh build",
    "./otb-dev.sh up",
)


def need(errors, condition, label):
    if not condition:
        errors.append(label)


def ordered(text, values):
    position = -1
    for value in values:
        position = text.find(value, position + 1)
        if position < 0:
            return False
    return True


def check_guides():
    errors = []
    for language, path in GUIDES.items():
        text = path.read_text(encoding="utf-8")
        prefix = f"{language}:"
        for value in (
            "https://github.com/OpenTenBase/OpenTenBase-DevEnv",
            "example-distributed",
            "./otb-dev.sh build",
            "./otb-dev.sh up",
            "./otb-dev.sh status",
            "./otb-dev.sh enter",
            "1 GTM + 1 CN + 2 DN",
            "127.0.0.1",
            "11000",
            "config.ini",
            "opentenbase_ctl",
            "5.2 GiB",
            "pgxc_ctl.conf",
            "pgxc.conf",
        ):
            need(errors, value in text, f"{prefix} missing {value}")
        platform_claim = "仅支持 x86_64" if language == "zh" else "requires x86_64"
        need(errors, platform_claim in text, f"{prefix} missing x86_64-only statement")
        no_rename = "无需重命名" if language == "zh" else "no rename"
        need(errors, no_rename in text.lower(), f"{prefix} missing no-rename statement")
        need(errors, ordered(text, COMMANDS), f"{prefix} command order")
        for stale in (
            "example/1c_2d_cluster",
            "copy-ssh-keys",
            "opentenbaseCN",
            "${SOURCECODE_PATH}/docker",
        ):
            need(errors, stale not in text, f"{prefix} stale {stale}")
    return errors


def parse_config(path, errors):
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as source:
            parser.read_file(source)
    except (OSError, configparser.Error) as exc:
        errors.append(f"external: config parse: {exc}")
        return None
    return parser


def direct_section_value(parser, section, option):
    values = parser._sections.get(section)
    if values is None:
        return ""
    return values.get(parser.optionxform(option), "")


def parse_compose(path, errors):
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", str(path), "config", "--format", "json"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        errors.append(f"external: compose command: {exc}")
        return None
    if result.returncode != 0:
        errors.append(f"external: compose parse: {result.stderr.strip()}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"external: compose JSON: {exc}")
        return None


def main_dispatch_case(script):
    function = re.search(
        r"(?ms)^main\(\)[ \t]*\{[ \t]*\n(?P<body>.*?)^\}[ \t]*$",
        script,
    )
    if function is None:
        return None
    case = re.search(
        r'(?ms)^(?P<indent>[ \t]*)case[ \t]+"\$1"[ \t]+in[ \t]*\n'
        r"(?P<body>.*?)^(?P=indent)esac(?:[ \t]*#.*)?$",
        function.group("body"),
    )
    return None if case is None else case.group("body")


def dispatches(script, label):
    case_body = main_dispatch_case(script)
    if case_body is None:
        return False
    return re.search(
        rf"(?m)^[ \t]*{re.escape(label)}(?:\|[a-z]+)*\)",
        case_body,
    ) is not None


def check_devenv(directory, bash_command="bash"):
    errors = []
    root = Path(directory)
    paths = {name: root / name for name in DEVENV_FILES}
    for name, path in paths.items():
        need(errors, path.is_file(), f"external: missing {name}")
    if errors:
        return errors
    need(errors, os.access(paths["otb-dev.sh"], os.X_OK), "external: script executable")

    config = parse_config(paths["config.ini"], errors)
    if config is not None:
        package = direct_section_value(config, "instance", "package")
        need(
            errors,
            direct_section_value(config, "instance", "type") == "distributed",
            "external: distributed type",
        )
        need(
            errors,
            package.endswith(".x86_64.tar.gz"),
            "external: x86 package",
        )
        need(
            errors,
            direct_section_value(config, "gtm", "master") == IPS["gtm"],
            "external: GTM address",
        )
        need(
            errors,
            direct_section_value(config, "coordinators", "master") == IPS["cn"],
            "external: CN address",
        )
        datanodes = direct_section_value(config, "datanodes", "master").replace(" ", "")
        need(
            errors,
            datanodes == f'{IPS["dn01"]},{IPS["dn02"]}',
            "external: DN addresses",
        )

    compose = parse_compose(paths["docker-compose.yml"], errors)
    if compose is not None:
        services = compose.get("services", {})
        need(errors, set(services) == SERVICES, "external: service set")
        for service, address in IPS.items():
            network = services.get(service, {}).get("networks", {}).get("otb-net", {})
            need(
                errors,
                network.get("ipv4_address") == address,
                f"external: {service} address",
            )
        ports = services.get("cn", {}).get("ports", [])
        cn_port = any(
            port.get("target") == 11000
            and str(port.get("published")) == "11000"
            and port.get("protocol") == "tcp"
            and port.get("host_ip") in (None, "", "0.0.0.0", "::")
            for port in ports
            if isinstance(port, dict)
        )
        need(errors, cn_port, "external: CN port")

    script = paths["otb-dev.sh"].read_text(encoding="utf-8")
    try:
        syntax = subprocess.run(
            [bash_command, "-n", str(paths["otb-dev.sh"])],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        errors.append("external: script syntax")
    else:
        need(errors, syntax.returncode == 0, "external: script syntax")
    for label in ("build", "up", "enter", "status"):
        need(errors, dispatches(script, label), f"external: {label} dispatch")

    readme = paths["README.md"].read_text(encoding="utf-8")
    need(errors, "1 GTM + 1 CN + 2 DN" in readme, "external: README topology")
    need(
        errors,
        "127.0.0.1" in readme and "11000" in readme,
        "external: README host connection",
    )
    need(errors, "config.ini" in readme, "external: README config")
    need(
        errors,
        re.search(r"5[.]2[ \t]+GiB", readme) is not None,
        "external: memory",
    )
    return errors


def copy_fixture(source, target):
    target.mkdir()
    for name in DEVENV_FILES:
        shutil.copy2(source / name, target / name)


def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"self-test source text absent: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def self_test(source):
    errors = []
    known_good = check_devenv(source)
    need(errors, not known_good, f"self-test: known good: {known_good}")
    mutations = (
        (
            "CN port",
            "docker-compose.yml",
            (('"11000:11000"', '"11001:11000"'),),
            "external: CN port",
        ),
        (
            "CN port UDP",
            "docker-compose.yml",
            (('"11000:11000"', '"11000:11000/udp"'),),
            "external: CN port",
        ),
        (
            "CN port loopback alias",
            "docker-compose.yml",
            (('"11000:11000"', '"127.0.0.2:11000:11000"'),),
            "external: CN port",
        ),
        (
            "x86 package",
            "config.ini",
            ((".x86_64.tar.gz", ".aarch64.tar.gz"),),
            "external: x86 package",
        ),
        (
            "inherited x86 package",
            "config.ini",
            (
                (
                    "package=/data/opentenbase/opentenbase-5.21.8-i.x86_64.tar.gz\n",
                    "",
                ),
                (
                    "# 分布式集群配置",
                    "[DEFAULT]\n"
                    "package=/data/opentenbase/"
                    "opentenbase-5.21.8-i.x86_64.tar.gz\n\n"
                    "# 分布式集群配置",
                ),
            ),
            "external: x86 package",
        ),
        (
            "up dispatch",
            "otb-dev.sh",
            (
                ("\n        up)", "\n        up-broken)"),
                ("Commands:\n", "Commands:\nup)\n"),
            ),
            "external: up dispatch",
        ),
        (
            "memory",
            "README.md",
            (("5.2 GiB", "memory requirement unknown"),),
            "external: memory",
        ),
    )
    for name, filename, replacements, expected in mutations:
        with tempfile.TemporaryDirectory(prefix="issue203-") as temporary:
            fixture = Path(temporary) / "fixture"
            copy_fixture(Path(source), fixture)
            for old, new in replacements:
                replace_once(fixture / filename, old, new)
            found = check_devenv(fixture)
            need(errors, expected in found, f"self-test: {name}: {found}")
    with tempfile.TemporaryDirectory(prefix="issue203-") as temporary:
        unavailable_bash = str(Path(temporary) / "unavailable-bash")
        found = check_devenv(source, bash_command=unavailable_bash)
        need(
            errors,
            found == ["external: script syntax"],
            f"self-test: bash command: {found}",
        )
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--devenv-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test and args.devenv_dir is None:
        parser.error("--self-test requires --devenv-dir")
    errors = check_guides()
    if args.devenv_dir is not None:
        errors.extend(check_devenv(args.devenv_dir))
        if args.self_test:
            errors.extend(self_test(args.devenv_dir))
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: Docker 1C2D documentation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
