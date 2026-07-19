#!/usr/bin/env python3
"""Generate ProVerif .pv files from edhoc_psk_sapic.spthy.

Trace properties are exported with `tamarin-prover -m=proverif` using the
lemma-group flag (-DSecrecy, -DFullAgreement, -DPFS) and every leak
combination (none, -DLeakShare, -DLeakSKey, both). For -DPQDL, one file per
group is generated under proverif/quantum/ with no leak crossings.

Observational-equivalence properties (anonymity / linkability) are exported
with `tamarin-prover -m=proverifequiv` using the diff-equivalence flags
(-DdiffEquiv{Anonymity,Linkability}{Initiator,Responder}), once per attacker
mode (active / passive), under proverif/diffequiv/.

Naming matches the existing layout:
    proverif/edhoc_psk_<group>[_LeakShare][_LeakSKey].pv
    proverif/quantum/edhoc_psk_quantum_<group>.pv
    proverif/diffequiv/edhoc_psk_proverif_diffEquiv_<prop>_<role>_<mode>_attacker.pv
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SPTHY_FILE = BASE_DIR / "edhoc_psk_sapic.spthy"
PROVERIF_DIR = BASE_DIR / "proverif"
QUANTUM_DIR = PROVERIF_DIR / "quantum"
DIFFEQUIV_DIR = PROVERIF_DIR / "diffequiv"

# group stem -> lemma-group preprocessor flag
GROUPS = {
    "sanity":        "-DSanityChecks",
    "secrecy":       "-DSecrecy",
    "fullagreement": "-DFullAgreement",
    "pfs":           "-DPFS",
}

# diff-equivalence stem -> preprocessor flag. Each maps to a `diffEquivLemma`
# process in the sapic source guarded by the matching #ifdef. Exported with
# `-m=proverifequiv`, which renders `diff(a,b)` as ProVerif `choice[a,b]`.
#
# Attacker modes are per property: (stem suffix, is_passive).
ACTIVE = ("active", False)
PASSIVE = ("passive", True)

DIFFEQUIV = {
    "anonymity_Initiator":   ("-DdiffEquivAnonymityInitiator",   [ACTIVE]),
    "anonymity_Responder":   ("-DdiffEquivAnonymityResponder",   [ACTIVE]),
    "linkability_Initiator": ("-DdiffEquivLinkabilityInitiator", [ACTIVE, PASSIVE]),
    "linkability_Responder": ("-DdiffEquivLinkabilityResponder", [ACTIVE, PASSIVE]),
}


# ProVerif rejects time inequalities between two premise events. The sapic
# source uses `i < c` in the pfs lemmas to express "compromise happens after
# acceptance" (PFS-style temporal ordering). Tamarin handles this fine, but
# `tamarin-prover -m=proverif` carries the inequality into the .pv where it
# is unsupported. Strip it post-export so ProVerif accepts the file.
TIME_INEQ_RE = re.compile(r"\s*&&\s*\(\s*i\s*<\s*c\s*\)")

def postprocess_pfs(pv_text: str) -> str:
    return TIME_INEQ_RE.sub("", pv_text)

SECRECY_INEQ_RE = re.compile(r"\s*&&\s*\(\s*i\s*<\s*j\s*\)")

def postprocess_secrecy(pv_text: str) -> str:
    return SECRECY_INEQ_RE.sub("", pv_text)


# Quantum builds need a phase-1 DL oracle as a parallel branch of the main
# process. The DL function itself is already declared via Headers.splib's
# `#ifdef PQDL` export-queries block; we only need to inject the oracle
# process. Hook point: the `compromise(<psk>)` sub-process *invocation* in the
# main process (e.g. `compromise(psk_2)`). Tamarin renames `~psk`, so match the
# generated variable name; the type-annotated `let compromise(psk_2:bitstring)`
# definition is skipped because the invocation has no `:type` suffix.
PQDL_HOOK_RE = re.compile(r"(compromise\([A-Za-z_][A-Za-z0-9_]*\))")
PQDL_BRANCH = "\n      |\n      phase 1; in(att, G:bitstring); out(att, DL(G,g))"


def postprocess_quantum(pv_text: str) -> str:
    new_text, n = PQDL_HOOK_RE.subn(r"\1" + PQDL_BRANCH, pv_text, count=1)
    if n == 0:
        print("WARNING: could not find hook; "
              "phase-1 DL oracle NOT injected", file=sys.stderr)
    return new_text


# `-m=proverifequiv` already emits `set preciseActions=true.` but not the
# other directives the diff-equivalence proofs rely on. Insert them right
# after that line so the ordering matches the hand-written references:
#   active : preciseActions, simplifyProcess, reconstructTrace
#   passive: preciseActions, attacker=passive, simplifyProcess, reconstructTrace
PRECISE_RE = re.compile(r"(set preciseActions=true\.)")


def make_postprocess_diffequiv(is_passive: bool):
    extra = ""
    if is_passive:
        extra += "\nset attacker=passive."
    extra += "\nset simplifyProcess = false.\nset reconstructTrace = false."

    def postprocess(pv_text: str) -> str:
        new_text, n = PRECISE_RE.subn(r"\1" + extra, pv_text, count=1)
        if n == 0:
            print("WARNING: could not find `set preciseActions` anchor; "
                  "extra set directives NOT added", file=sys.stderr)
        return new_text

    return postprocess


LEAK_COMBOS = [
    ([],                              ""),
    (["-DLeakShare"],                 "_LeakShare"),
    (["-DLeakSKey"],                  "_LeakSKey"),
    (["-DLeakShare", "-DLeakSKey"],   "_LeakShare_LeakSKey"),
]


def run_tamarin(flags, output_path: Path, dry_run: bool,
                mode: str = "-m=proverif", postprocessors=()):
    """Run tamarin export and write output_path.

    postprocessors is a sequence of (func, label) pairs applied in order to the
    exported text; label is printed whenever the pass changes something.
    """
    cmd = ["tamarin-prover", mode, *flags, str(SPTHY_FILE)]
    print(f"  $ {' '.join(cmd)} > {output_path.relative_to(BASE_DIR)}",
          flush=True)
    if dry_run:
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        print("ERROR: tamarin-prover not found on PATH.", file=sys.stderr)
        sys.exit(1)

    if proc.returncode != 0:
        print(f"  FAILED (rc={proc.returncode})", flush=True)
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        return False

    text = proc.stdout
    for func, label in postprocessors:
        new_text = func(text)
        if new_text != text:
            print(f"  ({label})", flush=True)
            text = new_text

    output_path.write_text(text, encoding="utf-8")
    return True


def group_postprocessors(group: str, is_quantum: bool):
    pp = []
    if group == "pfs":
        pp.append((postprocess_pfs, "stripped `i < c` premise inequality"))
    if group == "secrecy":
        pp.append((postprocess_secrecy, "stripped `i < j` premise inequality"))
    if is_quantum:
        pp.append((postprocess_quantum, "injected phase-1 DL oracle"))
    return pp


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--group", action="append",
                   choices=sorted(GROUPS.keys()),
                   help="Only generate this trace group (repeatable). "
                        "Default: all.")
    p.add_argument("--no-classical", action="store_true",
                   help="Skip non-PQDL trace files.")
    p.add_argument("--no-quantum", action="store_true",
                   help="Skip PQDL (quantum/) trace files.")
    p.add_argument("--no-diffequiv", action="store_true",
                   help="Skip diff-equivalence (diffequiv/) files.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print commands without running.")
    return p.parse_args()


def main():
    args = parse_args()
    groups = args.group or list(GROUPS.keys())

    if not SPTHY_FILE.exists():
        print(f"ERROR: {SPTHY_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    failures = []

    for group in groups:
        group_flag = GROUPS[group]

        if not args.no_classical:
            print(f"[{group}] classical:")
            for leak_flags, suffix in LEAK_COMBOS:
                out = PROVERIF_DIR / f"edhoc_psk_{group}{suffix}.pv"
                ok = run_tamarin([group_flag, *leak_flags], out, args.dry_run,
                                 postprocessors=group_postprocessors(group, False))
                if not ok:
                    failures.append(out)

        if not args.no_quantum:
            print(f"[{group}] quantum:")
            out = QUANTUM_DIR / f"edhoc_psk_quantum_{group}.pv"
            ok = run_tamarin([group_flag, "-DPQDL"], out, args.dry_run,
                             postprocessors=group_postprocessors(group, True))
            if not ok:
                failures.append(out)

    if not args.no_diffequiv:
        for stem, (flag, modes) in DIFFEQUIV.items():
            print(f"[diffequiv:{stem}]:")
            for mode_suffix, is_passive in modes:
                out = (DIFFEQUIV_DIR /
                       f"edhoc_psk_proverif_diffEquiv_{stem}_{mode_suffix}_attacker.pv")
                ok = run_tamarin([flag], out, args.dry_run,
                                 mode="-m=proverifequiv",
                                 postprocessors=[(make_postprocess_diffequiv(is_passive),
                                                  f"added {mode_suffix} set directives")])
                if not ok:
                    failures.append(out)

    if failures:
        print(f"\n{len(failures)} file(s) failed:", file=sys.stderr)
        for f in failures:
            print(f"  {f.relative_to(BASE_DIR)}", file=sys.stderr)
        sys.exit(2)

    print("\nDone.")


if __name__ == "__main__":
    main()
