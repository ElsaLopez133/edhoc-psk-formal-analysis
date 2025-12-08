## 📁 Structure of this directory

```text
models/
│
├── edhoc_psk_sapic.spthy           # Main SAPIC+ specification
├── LAKEPropertiesPSK.splib         # Lemmas for SAPIC+
├── Headers.splib                   # Optional attacker-capability flags
│
├── proverif/                       # ProVerif translations and equivalence models
│     ├── edhoc_psk_proverif.pv
│     ├── edhoc_psk_proverif_X.pv
│     ├── edhoc_psk_proverif_diffEquiv_anonymity_active_attacker.pv
│     └── edhoc_psk_proverif_diffEquiv_linkability_passive_attacker.pv
│     └── quantum/                  # Save-Now-Decrypt-Later (post-quantum) models
│         ├── edhoc_psk_proverif_quantum.pv
│         ├── edhoc_psk_proverif_diffEquiv_quantum_anonymity_active_attacker.pv
│         └── edhoc_psk_proverif_diffEquiv_quantum_linkability_passive_attacker.pv
│
└── scripts/
      └── automated_run.py          # Batch script for Tamarin
```

## 🚀 Running the model using SAPIC+

The main specification is 
```bash
edhoc_psk_sapic.spthy
```
It uses applied pi-calculus for the protocol and first-order logic for lemmas.

### Running the Tamarin Model

#### ▶️ Prove all lemmas (non-interactively)

```bash
tamarin-prover --prove edhoc_psk_sapic.spthy
```

#### ▶️ Prove a specific lemma

```bash
tamarin-prover --prove=secret_psk edhoc_psk_sapic.spthy
```

Any lemma listed in LAKEPropertiesPSK.splib can be used here.

#### ⚙️ Adding attacker capabilities

Defined in Headers.splib:
| Flag        | Meaning                                                   |
| ----------- | --------------------------------------------------------- |
| `LeakShare` | Ephemeral DH secret leakage                               |
| `LeakSKey`  | Leakage of the final session key                          |
| `PQDL`      | Post-quantum discrete-log oracle (Save-Now Decrypt-Later) |

To activate any capability:
```bash
tamarin-prover --prove=<lemma> -D<attacker-capability> edhoc_psk_sapic.spthy
```

#### Interactive Mode (Optional)

Note: Only works with a GUI. If on a headless server (e.g., SSH), use automatic mode instead.
To explore traces interactively:

```bash
tamarin-prover interactive edhoc_psk_sapic.spthy
```

If it fails to open a window, you're likely missing GUI/X11 support — run locally or use X11 forwarding:

```bash
ssh -X user@host
```

#### Automated running

To run all the lemmas and record runtime and proof steps:

```bash
python3 automated_run.py
```

### Running the ProVerif Model

To run with ProVerif, we first need to convert the SAPIC+ file to a ProVerif file:

```bash
tamarin-prover edhoc_psk_sapic.spthy -m=proverif > edhoc_psk_proverif.pv
```

To convert to ProVerif with additional flags:
```bash
tamarin-prover edhoc_psk_sapic.spthy -D<flag> -m=proverif > edhoc_psk_proverif.pv
```

This transforms the lemmas, expressed in firts-order-logic, into queries, expressed as trace properties.

You can then run ProVerif using

```bash
proverif edhoc_psk_proverif.pv 
```

If you want to output the trace-attack, create a directory (in this case ./graphs) and use the -graph option 

```bash
proverif -graph ./graphs edhoc_psk_proverif.pv
```

To output the elapsed time, do
```bash
/usr/bin/time -f "Elapsed time: %e seconds" proverif edhoc_psk_proverif.pv
```

#### Identity Protection in ProVerif

We use diff-equivalence to prove anonymity and (weak) linkability.
Intuitively, two process are equivalent if they cannot be distinguished by the attacker.

To generate the equivalence model:

```bash
 tamarin-prover -m=proverifequiv -D=diffEquivAnonymityInitiator edhoc_psk_sapic.spthy > edhoc_psk_proverif_diffEquiv_anonymity_initiator.pv
```

The flag can be modified depending on whether we want to prove anonymity (of either I or R) or linkability (of either I or R).
The options are:
- diffEquivAnonymityInitiator
- diffEquivAnonymityResponder
- diffEquivLinkabilityInitiator
- diffEquivLinkabilityResponder

We provide two ready-to-run files:

| File | Purpose |
|------|---------|
| `edhoc_psk_proverif_diffEquiv_linkability_passive_attacker.pv` | Linkability under a passive attacker, for both Initiator and Responder |
| `edhoc_psk_proverif_diffEquiv_anonymity_active_attacker.pv` | Anonymity under a active attacker, for both Initiator and Responder |
---

#### Post-Quantum Resistance in ProVerif

To analyze EDHOC-PSK under ''Save-Now, Decrypt-Later'' (SNDL) attacks, we provide a separate folder (proverif/quantum) containing ProVerif models where the attacker is equipped with a post-quantum ability: a Discrete Logarithm oracle that can recover Diffie–Hellman exponents from recorded values.

This oracle is added through the private equation:
```bash
reduc forall a:bitstring; DL(exp(g,a), g) = a [private].
```
and is activated in a dedicated protocol phase. This reflects a realistic quantum adversary who records all traffic today and later uses quantum resources to break ECDH.

There are three files in the given folder
| File | Purpose |
|------|---------|
| `edhoc_psk_proverif_diffEquiv_quantum_linkability_passive_attacker.pv` | Linkability in the SNDL model |
| `edhoc_psk_proverif_diffEquiv_quantum_anonymity_active_attacker.pv` | Anonymity in the SNDL |
| `edhoc_psk_proverif_quantum.pv` | Confidentiality, authentication and key confirmation in the SNDL |
---
