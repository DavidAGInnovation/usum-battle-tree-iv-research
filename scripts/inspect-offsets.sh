#!/bin/sh
set -eu

echo "USUM Battle Tree IV inspection points (VA base 0x100000)"
printf '%s\n' \
  'normal trainer branch : VA 0x159790 / raw 0x59790' \
  'generic partner       : VA 0x1581a8 / raw 0x581a8' \
  'ScoutLilie            : VA 0x157a1c / raw 0x57a1c' \
  'common helper         : VA 0x15faf4 / raw 0x5faf4' \
  'special selector      : VA 0x158760 / raw 0x58760'

if [ "$#" -eq 0 ]; then
  exit 0
fi

CODE_BIN=$1
if [ ! -f "$CODE_BIN" ]; then
  echo "error: file not found: $CODE_BIN" >&2
  exit 2
fi
if ! command -v radare2 >/dev/null 2>&1; then
  echo "error: radare2 is required for disassembly" >&2
  exit 3
fi

exec radare2 -a arm -b 32 -m 0x100000 -c \
  's 0x159790; pd 24; s 0x1581a8; pd 20; s 0x157a1c; pd 24; s 0x158760; pd 180' \
  "$CODE_BIN"
