# archives/ — compacted

Everything formerly in this folder is stored as gzip tarballs to keep the working tree small.
`MANIFEST.md` lists every tarball, its SHA-256, and every file inside it.

**Unpack**

    tar -xzf archives/<name>.tar.gz -C archives      # restores the original paths
    tar -tzf archives/<name>.tar.gz | less            # list without unpacking

Unpack into `archives/` only when you need the files; do not commit the unpacked copies. Archived
files are frozen history: do not edit them.

**What is where**

| Tarball | Contents |
|---|---|
| `rev-T-frozen.tar.gz` | **The frozen Rev T.** Pre-change copies of every file that mentioned Rev T (T1-T6) plus the whole 50 mm nacelle (SCAD, STLs, tools). Rev U live files carry "carried forward from Rev T..." labels; this is the original. Unpack into an empty directory (paths are under `rev-T-frozen/`). |
| `rev-T-and-earlier.tar.gz` | Frozen at the Rev U checkpoint (2026-11-03): Rev S/T BOMs, the Rev S viewer, one-shot BOM edit scripts, dated status snapshots, stale studies. Its own `rev-T-and-earlier/README.md` explains each file. |
| `airframe-archives.tar.gz`, `avionics-archives.tar.gz`, `stl.tar.gz`, `18in-scale-scad.tar.gz` | Retired airframe, avionics, and STL material from earlier revisions. |
| `graphical-build-guide-pre-revt.tar.gz`, `docs-superseded.tar.gz`, `stale-20260601.tar.gz`, `chat.tar.gz`, `serenity.tar.gz`, `root-readme-deep-dive-2026-08-03.tar.gz` | Superseded guides and documents, and saved working material. |
| `loose-zips.tar.gz`, `loose-files.tar.gz` | Former top-level zips, old viewer `.jsx` files, and early BOM snapshots. |

**Adding to the archive.** Do not unpack and repack an existing tarball. Add a new tarball named for
the checkpoint, for example `rev-U-and-earlier.tar.gz`, build it the same way
(`tar --sort=name --owner=0 --group=0 --numeric-owner --mtime=<date> ... | gzip -9 -n`), and add its
section to `MANIFEST.md`. Keep each tarball under GitHub's 100 MB file limit.
