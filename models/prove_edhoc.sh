#!/bin/bash
# Usage: ./prove_edhoc.sh <input_file> <lemmas> <s>
# Example: ./prove_edhoc.sh proverif edhoc_psk_proverif.spthy "exe*" 10 10 DFS s 0 4 false

INPUT=$1                                      # .spthy file
LEMMAS=${2:-exe*}                             # e.g. exe*, secrecy*, agreement*
S=${3:-10}                                    # step bound (e.g. 10)
GLOBAL_BOUND=${4:-10}                         # Global autoprover bound
STOP_ON_TRACE=${5:-DFS}                       # DFS, BFS, SEQDFS, NONE
HEURISTIC=${6:-s}                             # Parallel heuristic (for paralell p): C|I|O|P|S|c|i|o|p|s
DERIVCHECK_TIMEOUT=${7:-0}                    # derivation check timeout (0 = no limit)
THREADS=${8:-4}                               # number of threads for parallelism (default: 4)
VERBOSE=${9:-false}                           # true/false

# --- Check input file existence ---
if [[ ! -f "$INPUT" ]]; then
    echo "Error: Input file '$INPUT' does not exist."
    echo "Usage: $0 <input_file> <lemmas> <step_bound> <global_bound> <stop_on_trace> <heuristic> <derivation_timeout> <threads> <verbose>"
    exit 1
fi

echo "Running Tamarin on $INPUT with:"
echo "  Lemmas            = $LEMMAS"
echo "  Step bound        = $S"
echo "  Global bound      = $GLOBAL_BOUND"
echo "  Stop on trace     = $STOP_ON_TRACE"
echo "  Heuristic         = $HEURISTIC"
echo "  Deriv. timeout    = $DERIVCHECK_TIMEOUT"
echo "  Threads           = $THREADS"
echo "  Verbose           = $VERBOSE"

tamarin-prover --prove="$LEMMAS" \
    "$INPUT" \
    -s="${S:-10}" \
    --bound="${GLOBAL_BOUND:-10}" \
    --stop-on-trace="$STOP_ON_TRACE" \
    --heuristic="$HEURISTIC" \
    --derivcheck-timeout="$DERIVCHECK_TIMEOUT" \
    $VERBOSE_OPT \
    +RTS -N"$THREADS" -RTS \
    -DLeakShare -DLeakPSK -DLeakSessionKey

# tamarin-prover --prove=pfs*  edhoc_psk_sapic_debug.spthy --derivcheck-timeout=0 -DLeakShare -DLeakPSK -DLeakSessionKey