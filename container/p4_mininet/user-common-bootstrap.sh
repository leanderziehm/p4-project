#!/bin/bash

# SPDX-FileCopyrightText: 2021 Radostin Stoyanov
#
# SPDX-License-Identifier: Apache-2.0

# Print script commands and exit on errors.
set -xe

# --- Mininet --- #
MININET_COMMIT="5b1b376336e1c6330308e64ba41baac6976b6874"  # 2023-May-28
git clone https://github.com/mininet/mininet mininet
cd mininet
git checkout ${MININET_COMMIT}
PATCH_DIR="${HOME}/patches"
patch -p1 < "${PATCH_DIR}/mininet-patch-for-2023-jun.patch"
cd ..
sudo ./mininet/util/install.sh -nw

find /usr/lib /usr/local $HOME/.local | sort > $HOME/usr-local-7-after-mininet-install.txt
