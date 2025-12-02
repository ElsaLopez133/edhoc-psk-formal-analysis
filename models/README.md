## 📁 Files

| File | Purpose |
|------|---------|
| `edhoc_psk_sapic.spthy` | Main SAPIC+ theory modeling EDHOC with PSK |
| `edhoc_psk_proverif.pv` | Main ProVerif theory modeling EDHOC with PSK |
| `edhoc_psk_proverif_X.pv` | Main ProVerif theory modeling EDHOC with PSK with additional capabilities of the attacker |
| `LAKEPropertiesPSK.spthy` | Lemas for SAPIC model |

---

## 🚀 Running the model using SAPIC+

The file edhoc_psk_sapic.spthy is written in the SAPIC+ syntax, meaning that the process is modled using the applied pi calculus (same as ProVerif) whereas lemmas are written using first-order-logic (same as Tamarin).

This file can either be run in Tamarin or Proverif.

### Running the Tamarin Model

#### ✅ Prove all lemmas (non-interactively)

```bash
tamarin-prover --prove edhoc_psk_sapic.spthy
```

You can also run the full tamarin model with the same command:

```bash
tamarin-prover --prove edhoc_psk_tamarin.spthy
```

#### ✅ Prove a specific lemma

```bash
tamarin-prover --prove=secret_psk edhoc_psk_sapic.spthy
```

You can change secret_psk to any lemma defined in the file.

The script prove_edhoc.sh can be used to run tamarin adding different parameters and using different threat models (-DLeakShare -DLeakSKey -DSanityCheck)

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

To run all the lemmas and calculate the time and steps, there is a python script (automated_run.py). To run it:

```bash
python3 automated_run.py
```

### Running the ProVerif Model

To run with ProVerif, we first need to convert the file to a ProVerif file:

```bash
tamarin-prover edhoc_psk_sapic.spthy -m=proverif > edhoc_psk_proverif.pv
```

To convert to Proverif with additional flags:
```bash
tamarin-prover edhoc_psk_sapic.spthy -DLeakShare -m=proverif > edhoc_psk_proverif.pv
```

This transforms the lemmas, expressed in firts-order-logic, into queries, expressed as trace properties.

We can then run ProVerif using

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

#### Anonymity in Proverif

To prove anonymoty we use the equivalences in Proverif. Intuitively, two process are equivalent if they cannot be distinguished by the attacker.

To obtain the proverif file from the SAPIC+ file, run

```bash
 tamarin-prover -m=proverifequiv -D=diffEquivAnonymityInitiator edhoc_psk_sapic.spthy > edhoc_psk_proverif_diffEquiv_anonymity_initiator.pv
```

The flag (-D=diffEquivAnonymityInitiator) can be modified depending on whether we want to prove anonymity ( of either I or R) or linkability (of either I or R).

The script 
```bash
 ./proverif_anonymity.sh <label> <file> 
```
allows us to run the equivalence of FILE, annotate it with LABEL and append the results in a .csv

We provide two files to prove anonymity and linkability, respectively:

| File | Purpose |
|------|---------|
| `edhoc_psk_proverif_diffEquiv_linkability_passive_attacker.pv` | We prove linkability under a passive attacker |
| `edhoc_psk_proverif_diffEquiv_anonymity_active_attacker.pv` | We prove anonymity under a active attacker |
---

#### Post-Quantum Resistance in Proverif

To analyse EDHOC-PSK under Save-Now, Decrypt-Later (SNDL) attacks, we provide a separate folder containing ProVerif models where the attacker is equipped with a post-quantum ability: a Discrete Logarithm oracle that can recover Diffie–Hellman exponents from recorded values.

This oracle is added through the private equation:
```bash
reduc forall a:bitstring; DL(exp(g,a), g) = a [private].
```
and is activated in a dedicated protocol phase. This reflects a realistic quantum adversary who records all traffic today and later uses quantum resources to break ECDH.

There are three files in the given folder
| File | Purpose |
|------|---------|
| `edhoc_psk_proverif_diffEquiv_quantum_linkability_passive_attacker.pv` | We prove linkability in the SNDL model |
| `edhoc_psk_proverif_diffEquiv_quantum_anonymity_active_attacker.pv` | We prove anonymity in the SNDL |
| `edhoc_psk_proverif_quantum.pv` | We prove confidentiality, authentication and key confirmation in the SNDL |
---

### ❓Which one to use

ProVerif is a great tool for the initial, automated analysis. In ProVerif, traces are inferred automatically, leading to less explicit control over temporal behaviors. It focuses more on reachability properties, such as executability, secrecy and authentication, and has a limited support for equivalence. The output is mostly textual with limited visualiztion.

Tamarin, on the other hand, can handle more complex staeful protocols, and supports rich algebraic theories. It can model actions with temporal ordering and fine grained control over traces. It supports obervational equivalence. It often requires manual guidance, making it less automatic than ProVerif, and it is generally slower. It allows for visual interpretation of the results the integrated GUI.
