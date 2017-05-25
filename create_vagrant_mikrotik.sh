#!/usr/bin/env bash

dl_link='https://download2.mikrotik.com/routeros/6.38.1/chr-6.38.1.vdi'
vmname='mikrotik-6-38-1'

[[ -f ./downloads/$(basename "$dl_link") ]] && {
  echo "*** vdi already exists"
} || {
  mkdir -p ./downloads/
  wget --directory-prefix=./downloads/ "$dl_link"
}


echo "*** create the vm"
VBoxManage createvm \
  --name "$vmname" \
  --ostype 'Linux_64' \
  --register

VBoxManage storagectl \
  "$vmname" \
  --name "SATA Controller" \
  --add sata

echo "*** add the hard disk"
VBoxManage storageattach \
 "$vmname" \
  --storagectl "SATA Controller" \
  --port 0 \
  --device 0 \
  --type hdd \
  --medium ./downloads/$(basename "$dl_link")

vagrant package --base "$vmname" --output ~/"$vmname".box

vagrant box add "$vmname" ~/"$vmname".box --name "$vmname"
