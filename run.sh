#!/bin/sh
case "$1" in
  asm)
    shift
    python3 -m src.asm_cli "$@"
    ;;
  run)
    shift
    python3 -m src.interp_cli "$@"
    ;;
  *)
    echo "Использование:" >&2
    echo "  ./run.sh asm  ИСХОДНИК ВЫХОД [--test]" >&2
    echo "  ./run.sh run  БИНАРНИК ДАМП START:END" >&2
    exit 1
    ;;
esac
