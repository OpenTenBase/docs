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


def command_log_calls(path):
    calls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if fields and fields[0] == "docker":
            calls.append(tuple(fields[1:]))
    return calls


def has_prefix(calls, prefix):
    return any(call[: len(prefix)] == prefix for call in calls)


def valid_dispatch_log(command, calls):
    if command == "status":
        return calls == [("compose", "ps")]
    if command == "up":
        return calls == [("compose", "up", "-d"), ("compose", "ps")]
    if command == "enter":
        return calls == [
            (
                "exec",
                "otb-gtm",
                "su",
                "-",
                "opentenbase",
                "-c",
                "cd /data/opentenbase && ./opentenbase_ctl status",
            ),
            (
                "exec",
                "-it",
                "-u",
                "opentenbase",
                "-w",
                "/data/opentenbase",
                "otb-gtm",
                "bash",
            ),
        ]
    if command == "build":
        required = (
            ("build", "-t", "otb-base:latest"),
            ("tag", "otb-base:latest", "otb-distributed:latest"),
            ("compose", "-f", "docker-compose.build.yml", "up", "-d"),
            (
                "exec",
                "otb-gtm",
                "su",
                "-",
                "opentenbase",
                "-c",
                "cd /data/opentenbase && "
                "./opentenbase_ctl install -c config.ini",
            ),
            ("commit", "otb-gtm", "otb-gtm:installed"),
            ("commit", "otb-cn", "otb-cn:installed"),
            ("commit", "otb-dn01", "otb-dn01:installed"),
            ("commit", "otb-dn02", "otb-dn02:installed"),
            ("images",),
        )
        return all(has_prefix(calls, prefix) for prefix in required)
    return False


def check_script_dispatches(source, bash_command):
    errors = []
    fake_docker = r"""#!/bin/sh
printf 'docker' >> "$COMMAND_LOG"
for argument in "$@"; do
    printf '\t%s' "$argument" >> "$COMMAND_LOG"
done
printf '\n' >> "$COMMAND_LOG"
if [ "${1:-}" = "images" ]; then
    printf '%s\n' \
        'otb-gtm installed' \
        'otb-cn installed' \
        'otb-dn01 installed' \
        'otb-dn02 installed'
fi
exit 0
"""
    fake_sleep = "#!/bin/sh\nexit 0\n"
    with tempfile.TemporaryDirectory(prefix="issue203-dispatch-") as temporary:
        fixture = Path(temporary) / "fixture"
        copy_fixture(Path(source), fixture)
        fakebin = Path(temporary) / "fakebin"
        fakebin.mkdir()
        docker = fakebin / "docker"
        sleep = fakebin / "sleep"
        docker.write_text(fake_docker, encoding="utf-8")
        sleep.write_text(fake_sleep, encoding="utf-8")
        docker.chmod(0o755)
        sleep.chmod(0o755)
        command_log = Path(temporary) / "commands.log"
        environment = os.environ.copy()
        environment["COMMAND_LOG"] = str(command_log)
        environment["PATH"] = f"{fakebin}{os.pathsep}{environment.get('PATH', '')}"
        script = fixture / "otb-dev.sh"
        for command in ("status", "up", "enter", "build"):
            command_log.write_text("", encoding="utf-8")
            try:
                result = subprocess.run(
                    [bash_command, str(script), command],
                    cwd=fixture,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=15,
                )
            except (OSError, subprocess.TimeoutExpired):
                errors.append(f"external: {command} dispatch")
                continue
            calls = command_log_calls(command_log)
            if result.returncode != 0 or not valid_dispatch_log(command, calls):
                errors.append(f"external: {command} dispatch")
    return errors


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
            and port.get("host_ip") in (None, "", "0.0.0.0", "127.0.0.1")
            for port in ports
            if isinstance(port, dict)
        )
        need(errors, cn_port, "external: CN port")

    syntax_ok = False
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
        syntax_ok = syntax.returncode == 0
        need(errors, syntax_ok, "external: script syntax")
    if syntax_ok:
        errors.extend(check_script_dispatches(root, bash_command))

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
            "CN port IPv6 only",
            "docker-compose.yml",
            (('"11000:11000"', '"[::]:11000:11000"'),),
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
            "nested up dispatch",
            "otb-dev.sh",
            (
                ("\n        up)", "\n        up-broken)"),
                (
                    "\n        build)\n            shift\n",
                    "\n        build)\n"
                    "            cat <<'FORGED_USAGE' >/dev/null\n"
                    "up)\n"
                    "FORGED_USAGE\n"
                    '            case "$2" in\n'
                    "                up)\n"
                    "                    :\n"
                    "                    ;;\n"
                    "                *)\n"
                    "                    :\n"
                    "                    ;;\n"
                    "            esac\n"
                    "            shift\n",
                ),
            ),
            "external: up dispatch",
        ),
        (
            "status routed through up",
            "otb-dev.sh",
            (
                ("\n        status|ps)", "\n        status-broken|ps)"),
                ("\n        up)", "\n        up|status)"),
            ),
            "external: status dispatch",
        ),
        (
            "enter routed through build",
            "otb-dev.sh",
            (
                ("\n        enter|exec)", "\n        enter-broken|exec)"),
                ("\n        build)", "\n        build|enter)"),
            ),
            "external: enter dispatch",
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
        fixture = Path(temporary) / "fixture"
        copy_fixture(Path(source), fixture)
        replace_once(
            fixture / "docker-compose.yml",
            '"11000:11000"',
            '"127.0.0.1:11000:11000"',
        )
        found = check_devenv(fixture)
        need(errors, found == [], f"self-test: CN port IPv4 loopback: {found}")
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
