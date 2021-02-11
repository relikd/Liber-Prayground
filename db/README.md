### InterruptDB

- `db_high`           : Find IoC combinations that are as high as possible
- `db_high_secondary` : List of non-optimal solutions with score greater than 1.4
- `db_norm`           : Find IoC combinations that are close to normal english (1.7737)
- `db_norm_secondary` : List of non-optimal solutions with score greater than 0.55
- `db_indices`        : Just each index of each rune for all chapters

_Note:_ All secondary dbs do not include the solutions from the original db.

### OEIS

Download and unzip the OEIS [stripped.gz][1]. Rename the file to `oeis_orig.txt`. Run `trim_orig_oeis()` in `solver.py`, which will generate the `oeis.txt`.

[1]: https://oeis.org/stripped.gz