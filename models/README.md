## 📁 Files

| File | Purpose |
|------|---------|
| `edhoc_psk_sapic.spthy` | Main SAPIC+ theory modeling EDHOC with PSK |
| `edhoc_psk_proverif.pv` | ProVerif translation of the SAPIC+ model |
| `edhoc_psk_proverif_X.pv` | ProVerif variants with additional attacker capabilities |
| `LAKEPropertiesPSK.splib` | Lemmas for SAPIC+ model |
| `Headers.splib` | Definition of optional attacker capabilities |
| `automated_run.py` | Script to batch-run lemmas and collect statistics |

---

## 🚀 Running the model using SAPIC+

The file edhoc_psk_sapic.spthy is written in the SAPIC+ syntax, meaning that the process is modeled using the applied pi-calculus (same as ProVerif) whereas lemmas are written using first-order logic (same as Tamarin).

This file can either be run in Tamarin or Proverif.

### Running the Tamarin Model

#### Prove all lemmas (non-interactively)

```bash
tamarin-prover --prove edhoc_psk_sapic.spthy
```

#### Prove a specific lemma

```bash
tamarin-prover --prove=secret_psk edhoc_psk_sapic.spthy
```

You can change secret_psk to any lemma defined in the LAKEPropertiesPSK.splib.

#### Adding attacker capabilities

We define three flags that model attacker capabilities.
They can be found in the file Headers.splib:
- LeakShare: models leakage of DH secrets
- LeakSKey: models leakage of the session key
- PQDL: activates the post-quantum discrete logarithm oracle (used in Save Now Decrypt Later analysis)

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

The flag (-D=diffEquivAnonymityInitiator) can be modified depending on whether we want to prove anonymity ( of either I or R) or linkability (of either I or R).
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

To analyze EDHOC-PSK under ''Save-Now, Decrypt-Later'' (SNDL) attacks, we provide a separate folder containing ProVerif models where the attacker is equipped with a post-quantum ability: a Discrete Logarithm oracle that can recover Diffie–Hellman exponents from recorded values.

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
