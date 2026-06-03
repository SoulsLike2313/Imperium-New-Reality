# Canonical PC -> VM3 Transfer Commands

## Route identity
- alias: `imperium-vm3`
- remote user: `vboxuser3`
- inbox: `/home/vboxuser3/IMPERIUM_VM3_INBOX`

## Probe
```bash
ssh imperium-vm3 "hostname; whoami; pwd"
```

## Send taskpack
```bash
scp <taskpack.zip> imperium-vm3:/home/vboxuser3/IMPERIUM_VM3_INBOX/
```

## Verify hash on VM3
```bash
ssh imperium-vm3 "sha256sum /home/vboxuser3/IMPERIUM_VM3_INBOX/<taskpack.zip>"
```

## Example with current taskpack
```bash
scp TASKPACK_NEWGEN_VM3_ROUTE_REGISTRY_ASTRONOMICON_BODY_UBUNTU_V0_1.zip imperium-vm3:/home/vboxuser3/IMPERIUM_VM3_INBOX/
ssh imperium-vm3 "sha256sum /home/vboxuser3/IMPERIUM_VM3_INBOX/TASKPACK_NEWGEN_VM3_ROUTE_REGISTRY_ASTRONOMICON_BODY_UBUNTU_V0_1.zip"
```

Expected hash for prior route proof taskpack:
`5a71cf8a61c588b87888d4c1f98309933805771ed8d71cfde5376ae59f05199a`
