#!/usr/bin/env python3
"""Extract the retail Battle AI archive and ExeFS .code from a decrypted 3DS ROM.

The extractor is intentionally read-only with respect to the ROM.  It writes a
small, reviewable artifact directory containing the source GARC, its numbered
members, a manifest, and the raw ExeFS ``.code`` section.  With
``--cros-output`` it also extracts the 132 root-level retail CRO modules used
by the whole-program verifier.  ``pyctr`` is the only non-standard dependency.

The supplied ROM is already decrypted, so the zero-valued key material below is
used together with ``assume_decrypted=True``.  This is not a key-recovery tool
and must not be used as evidence for an encrypted image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


KNOWN_LABELS = (
    "allowanceAI",
    "bandAI",
    "basicAI",
    "doubleAI",
    "expertAI",
    "movingAI",
    "pokechangeAI",
    "royalAI",
    "strongAI",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def configure_decrypted_crypto():
    try:
        from pyctr.crypto.engine import CryptoEngine, Keyslot
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise SystemExit(
            "pyctr is required; install it in the active Python environment"
        ) from exc

    crypto = CryptoEngine(setup_b9_keys=False)
    # NCCHReader still consults the key slots while opening a decrypted
    # partition.  Zero material is sufficient when encryption is disabled.
    for slot in (
        Keyslot.NCCH,
        Keyslot.NCCHExtraKey,
        Keyslot.NCCH70,
        Keyslot.NCCH93,
        Keyslot.NCCH96,
    ):
        crypto.key_x[slot] = 0
        crypto.key_y[slot] = 0
        crypto.key_normal[slot] = b"\0" * 16
    return crypto


def open_romfs_and_exefs(rom_path: Path):
    from pyctr.fileio import SubsectionIO
    from pyctr.type.ncch import NCCHReader, NCCHSection
    from pyctr.type.romfs import RomFSReader

    crypto = configure_decrypted_crypto()
    handle = rom_path.open("rb")
    handle.seek(0x100)
    ncsd = handle.read(0x100)
    partition_offset = u32(ncsd, 0x20) * 0x200
    partition_size = u32(ncsd, 0x24) * 0x200
    ncch = NCCHReader(
        SubsectionIO(handle, partition_offset, partition_size),
        crypto=crypto,
        assume_decrypted=True,
        load_sections=False,
    )
    romfs = RomFSReader(ncch._open_section_generic(NCCHSection.RomFS, encryption=False))
    exefs = ncch._open_section_generic(NCCHSection.ExeFS, encryption=False)
    # Keep the NCCHReader alive while its section-backed file objects are
    # consumed.  Its destructor closes the underlying subsection otherwise.
    return handle, ncch, romfs, exefs


def extract_exefs_code(exefs) -> bytes:
    header = exefs.read(0x200)
    if len(header) != 0x200:
        raise ValueError("ExeFS header is truncated")
    for index in range(10):
        entry = index * 0x10
        name = header[entry : entry + 8].split(b"\0", 1)[0].decode("ascii", "replace")
        offset = u32(header, entry + 8)
        size = u32(header, entry + 12)
        if name == ".code":
            exefs.seek(0x200 + offset)
            code = exefs.read(size)
            if len(code) != size:
                raise ValueError("ExeFS .code entry is truncated")
            return code
    raise ValueError("ExeFS does not contain a .code entry")


def embedded_labels(payload: bytes) -> list[str]:
    found: set[str] = set()
    for encoding in ("ascii", "utf-16le"):
        text = payload.decode(encoding, errors="ignore")
        for label in KNOWN_LABELS:
            if label in text:
                found.add(label)
    return sorted(found)


def split_garc(garc: bytes, output: Path) -> list[dict[str, object]]:
    if garc[:4] != b"CRAG":
        raise ValueError(f"unexpected GARC magic: {garc[:4]!r}")

    btaf_offset = garc.find(b"BTAF")
    bmif_offset = garc.find(b"BMIF")
    if btaf_offset < 0 or bmif_offset < 0:
        raise ValueError("GARC is missing BTAF or BMIF")
    count = u32(garc, btaf_offset + 8)
    data_start = bmif_offset + 12
    members: list[dict[str, object]] = []
    for index in range(count):
        record = btaf_offset + 12 + index * 16
        flags, start, end, declared_size = struct.unpack_from("<IIII", garc, record)
        if flags == 0 or end < start:
            raise ValueError(f"invalid BTAF record {index}")
        payload = garc[data_start + start : data_start + end]
        if len(payload) != end - start:
            raise ValueError(f"truncated GARC member {index}")
        if payload[4:8] != bytes.fromhex("e0f10a0a"):
            raise ValueError(f"member {index} is not a Pawn AMX program")
        name = f"{index:02d}.amx"
        (output / name).write_bytes(payload)
        members.append(
            {
                "index": index,
                "file": name,
                "start": start,
                "end": end,
                "raw_size": len(payload),
                "declared_amx_size": declared_size,
                "sha256": sha256(payload),
                "labels": embedded_labels(payload),
            }
        )
    return members


def extract_root_cros(romfs, output: Path) -> list[dict[str, object]]:
    """Extract the root-level CRO modules used by the retail verifier."""
    output.mkdir(parents=True, exist_ok=True)
    root = romfs.get_info_from_path("/")
    rows: list[dict[str, object]] = []
    for name in sorted(root.contents):
        if not name.endswith(".cro"):
            continue
        payload = romfs.open("/" + name).read()
        path = output / name
        path.write_bytes(payload)
        rows.append(
            {
                "file": name,
                "size": len(payload),
                "sha256": sha256(payload),
            }
        )
    if len(rows) != 132:
        raise ValueError(f"expected 132 root CROs, found {len(rows)}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path, help="decrypted .3ds image")
    parser.add_argument("output", type=Path, help="artifact directory to create")
    parser.add_argument(
        "--romfs-path",
        default="/a/0/8/4",
        help="RomFS path of the Battle AI GARC (default: /a/0/8/4)",
    )
    parser.add_argument(
        "--cros-output",
        type=Path,
        help="also extract all 132 root-level retail CRO modules to this directory",
    )
    args = parser.parse_args()
    if not args.rom.is_file():
        parser.error(f"ROM does not exist: {args.rom}")
    args.output.mkdir(parents=True, exist_ok=True)
    amx_dir = args.output / "amx"
    amx_dir.mkdir(exist_ok=True)

    handle, ncch, romfs, exefs = open_romfs_and_exefs(args.rom)
    cros: list[dict[str, object]] = []
    try:
        garc = romfs.open(args.romfs_path).read()
        code = extract_exefs_code(exefs)
        if args.cros_output is not None:
            cros = extract_root_cros(romfs, args.cros_output)
    finally:
        romfs.close()
        ncch.close()
        handle.close()

    garc_path = args.output / "battle-ai.garc"
    code_path = args.output / "code.bin"
    garc_path.write_bytes(garc)
    code_path.write_bytes(code)
    members = split_garc(garc, amx_dir)

    manifest = {
        "rom": str(args.rom),
        "romfs_path": args.romfs_path,
        "garc": {
            "file": garc_path.name,
            "size": len(garc),
            "sha256": sha256(garc),
            "member_count": len(members),
        },
        "exefs_code": {
            "file": code_path.name,
            "size": len(code),
            "sha256": sha256(code),
            "va_base": "0x100000",
        },
        "members": members,
    }
    if args.cros_output is not None:
        manifest["cros"] = {
            "directory": str(args.cros_output),
            "count": len(cros),
            "files": cros,
        }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
