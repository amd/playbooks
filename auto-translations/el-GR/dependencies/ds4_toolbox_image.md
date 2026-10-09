<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη της εικόνας container εργαλειοθήκης ds4

Το `ds4-cockpit` εκτελεί τη μηχανή συμπερασμάτων ds4 μέσα σε μια εργαλειοθήκη container. Στην καρτέλα **Interactive Toolboxes**, επιλέξτε την πιο πρόσφατη διαθέσιμη εργαλειοθήκη (π.χ. `ds4-rocm-7.2.4`) και κάντε κλικ στο **Create/Update** για να γίνει λήψη της εικόνας.

Για απευθείας λήψη της εικόνας:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Η έκδοση της εργαλειοθήκης αλλάζει με τον καιρό, επομένως ο παρακάτω έλεγχος αντιστοιχεί στην οικογένεια εικόνων και όχι σε μια σταθερή ετικέτα.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->