# IMPERIUM ID POLICY V0.1

Every resident receives an `imperium_id`.

V0.1 format:

```text
imp:<kind>:<class_slug>:<name_slug>:<path_hash_12>
```

The path hash prevents collisions when many files share names. Future migrations may introduce long-lived identity records where `imperium_id` survives path movement.
