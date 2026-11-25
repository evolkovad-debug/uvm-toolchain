#!/bin/sh
case "$1" in
  asm) shift; python3 -m src.asm_cli "$@" ;;
  vm) shift; python3 -m src.vm_cli "$@" ;;
  *) echo "Использование: ./run.sh asm|vm ..." >&2; exit 1 ;;
esac
