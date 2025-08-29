#!/bin/bash
# Usage: ./prove_edhoc.sh <input_file> <lemmas> <s>
# Example: ./prove_edhoc.sh proverif edhoc_psk_proverif.spthy "exe*" 10

INPUT=$1                # .spthy file
LEMMAS=${2:-exe*}       # e.g. exe*, secrecy*, agreement*
S=${3:-10}              # step bound (e.g. 10)

if [[ -z "$INPUT" || -z "$LEMMAS" ]]; then
    echo "Usage: $0 <input_file> <lemmas> <s>"
    exit 1
fi

echo "Running $LEMMAS on $INPUT with s=$S..."

tamarin-prover --prove="$LEMMAS" "$INPUT" --derivcheck-timeout=0 -s="${S:-10}"
