<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη της εικόνας κοντέινερ toolbox του ds4

Το `ds4-cockpit` εκτελεί τη μηχανή συμπερασμού ds4 μέσα σε ένα container toolbox. Στην καρτέλα **Interactive Toolboxes**, επιλέξτε το πιο πρόσφατο διαθέσιμο toolbox (π.χ. `ds4-rocm-7.2.4`) και κάντε κλικ στο **Create/Update** για να γίνει λήψη της εικόνας.

Για να κάνετε απευθείας λήψη της εικόνας:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Η έκδοση του toolbox αλλάζει με την πάροδο του χρόνου, γι' αυτό ο παρακάτω έλεγχος αντιστοιχεί στην οικογένεια εικόνων και όχι σε μια σταθερή ετικέτα.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->