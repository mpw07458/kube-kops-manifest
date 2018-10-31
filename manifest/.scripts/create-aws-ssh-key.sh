#!/usr/bin/env bash
kops create secret \
--name diamondbacksolutionsllc.com \
sshpublickey admin \
-i ~/.ssh/id_rsa.pub
