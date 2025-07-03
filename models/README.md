## 📁 Files

| File | Purpose |
|------|---------|
| `edhoc_psk_tamarin.spthy` | Main Tamarin theory modeling EDHOC with PSK |
| `edhoc_psk_proverif.spthy` | Main Proverif theory modeling EDHOC with PSK |
| `LAKEPropertiesPSK.splib` | Lemas for Proverif model |
| `LAKEPropertiesPSKTamarin.spthy` | Lemas for Tamarin model |

---

## 🚀 Running the Tamarin Model

### ✅ Prove all lemmas (non-interactively)

```bash
tamarin-prover --prove edhoc_psk_tamarin.spthy
```

### ✅ Prove a specific lemma
```bash
tamarin-prover --prove=session_key_secrecy edhoc_psk_tamarin.spthy
```

You can change session_key_secrecy to any lemma defined in the file.

### Interactive Mode (Optional)

Note: Only works with a GUI. If on a headless server (e.g., SSH), use automatic mode instead.

To explore traces interactively:

```bash
tamarin-prover interactive edhoc_psk_tamarin.spthy
```

If it fails to open a window, you're likely missing GUI/X11 support — run locally or use X11 forwarding:

```bash
ssh -X user@host
```
