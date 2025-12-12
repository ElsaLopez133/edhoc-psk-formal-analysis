# EDHOC-PSK Formal Analysis

Our repository consists of formal models of EDHOC-PSK written in SAPIC+.
The models support different attacker capabilities, including Save-Now-Decrypt-Later (SNDL) post-quantum adversaries.

## 📌 Goals

The model enables the verification of:

- Authentication and secrecy properties
- Anonymity and unlinkability
- Post-quantum resilience of PSK-based EDHOC

## Requirements

- Tamarin Prover ≥ 1.9.0
- ProVerif ≥ 2.04
- Python 3 (for automation script)
- Optional: Graphviz (for ProVerif attack graphs)

## 📚 References

- [EDHOC IETF Draft](https://datatracker.ietf.org/doc/html/draft-ietf-lake-edhoc)
- [EDHOC-PSK Draft](https://datatracker.ietf.org/doc/draft-ietf-lake-edhoc-psk/)

## Acknolwdegments

This repository follows https://github.com/charlie-j/edhoc-formal-analysis/tree/master
