## 📁 Files

| File | Purpose |
|------|---------|
| `edhoc_psk_tamarin.spthy` | Main Tamarin theory modeling EDHOC with PSK |
| `edhoc_psk_sapic.spthy` | Main SAPIC+ theory modeling EDHOC with PSK |
| `edhoc_psk_proverif.pv` | Main ProVerif theory modeling EDHOC with PSK |
| `LAKEPropertiesPSK.spthy` | Lemas for SAPIC model |

---


## 🚀 Running the model using SAPIC+

The file edhoc_psk_sapic.spthy is written in the SAPIC+ syntax, meaning that the process is modled using the applied pi calculus (same as ProVerif) whereas lemmas are writtne using first-order-logic, (same as Tamarin).

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
tamarin-prover --prove=session_key_secrecy edhoc_psk_sapic.spthy
```

You can change session_key_secrecy to any lemma defined in the file.

The script prove_edhoc.sh can be used to run tamarin adding different parameters. and using different threat models (-DLeakShare -DLeakPSK -DLeakSessionKey -DSanityCheck)

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

### Running the ProVerif Model

To run with ProVerif, we first need to convert the file to a ProVerif file:

```bash
tamarin-prover edhoc_psk_sapic.spthy -m=proverif > edhoc_psk_proverif.pv
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

### ❓Which one to use

ProVerif is a great tool for the initial, automated analysis. In ProVerif, traces are inferred automatically, leading to less explicit control over temporal behaviors. It focuses more on reachability properties, such as executability, secrecy and authentication, and has a limited support for equivalence. The output is mostly textual with limited visualiztion.

Tamarin, on the other hand, can handle more complex staeful protocols, and supports rich algebraic theories. It can model actions with temporal ordering and fine grained control over traces. It supports obervational equivalence. It often requires manual guidance, making it less automatic than ProVerif, and it is generally slower. It allows for visual interpretation of the results the integrated GUI.
