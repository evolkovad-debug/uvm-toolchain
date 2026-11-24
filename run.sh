#!/bin/sh
case "$1" in
  asm) shift; python3 -m src.asm_cli "$@" ;;
  *) echo "Использование: ./run.sh asm ИСХОДНИК ВЫХОД [--test]" >&2; exit 1 ;;
esac
