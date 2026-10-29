```
  ● ● ● ● ·   · ● ● ● ●   · · · ● ·   ● ● ● ● ·   ● · · · ●   · ● ● ● ·
  ● · · · ●   ● · · · ·   · · ● ● ·   ● · · · ●   ● · · ● ·   ● · · · ●
  ● · · · ●   ● · · · ·   · ● · ● ·   ● · · · ●   ● · ● · ·   ● · · · ·
  ● ● ● ● ·   · ● ● ● ·   ● · · ● ·   ● ● ● ● ·   ● ● · · ·   ● · ● ● ●
  ● · · · ·   · · · · ●   ● ● ● ● ●   ● · · · ·   ● · ● · ·   ● · · · ●
  ● · · · ·   · · · · ●   · · · ● ·   ● · · · ·   ● · · ● ·   ● · · · ●
  ● · · · ·   ● ● ● ● ·   · · · ● ·   ● · · · ·   ● · · · ●   · ● ● ● ●
```

**Turn PS4 `.pkg` files into folders shadPS4 can actually play. On macOS. In one command.**

shadPS4 does not install `.pkg` files anymore. It wants a plain folder containing
`eboot.bin` and `sce_sys/`. `ps4pkg` gets you from one to the other, and names the
folder after the real game so your library is readable.

```
$ ps4pkg extract "EP1063-CUSA13198_00-USOTSUKIHIME0001-A0100-V0100.pkg"

  Package   EP1063-CUSA13198_00-USOTSUKIHIME0001-A0100-V0100.pkg
  Size      1.92 GB
  Type      game
  Into      /Volumes/Games/PS4

  ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀⣀⣀  61%  182/297 files  1.42 GB  ETA 2m 18s
```

...and when it lands:

```
  Game      The Liar Princess and the Blind Prince
  Title ID  CUSA13198
  Folder    /Volumes/Games/PS4/The Liar Princess and the Blind Prince [CUSA13198]
  Took      5m 53s

  ● Ready for shadPS4. Point its game folder at: /Volumes/Games/PS4
```

---

## Install

### Architecture fix in this fork

To use this fork's installer changes, clone the repository and run its local
installer from the checkout (the upstream download command below downloads the
upstream release instead):

```bash
git clone https://github.com/ojczeo/ps4pkg.git
cd ps4pkg
# Before the fix is merged, switch to its review branch:
git checkout fix/macos-build-architecture
bash install.sh
```

`ps4pkg install` selects the native hardware architecture: `arm64` on Apple
Silicon, including when launched from a Rosetta terminal, or `x86_64` on Intel.
It passes the same target to Crypto++ and CMake, checks zlib's architecture,
and cleans stale Crypto++ objects before rebuilding a missing or incompatible
archive. A failed build prints the location of its complete log and preserves it.

Use a Homebrew zlib 1.3+ library for that architecture. Apple Silicon Homebrew
normally lives in `/opt/homebrew`; Intel Homebrew normally lives in `/usr/local`.
If no compatible library is found, install zlib with the matching Homebrew.

Portable regression checks: `python3 test_install.py` and `bash -n ps4pkg`.
These mock macOS build tools; an actual macOS build is still required to verify
the compiled extractor. After installing, check the result with:

```bash
file "${PS4PKG_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/ps4pkg}/bin/pkg-extractor"
```

### Upstream installer

One line. Paste it into Terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Ashref-dev/ps4pkg/main/install.sh | bash
```

That installs what's needed, downloads `ps4pkg`, and builds the extraction engine
(about half a minute, once). Then open a new terminal window and you're ready.

**Requirements:** macOS (Apple Silicon or Intel), [Homebrew](https://brew.sh), and
Apple's command line tools. The installer checks for all three and tells you exactly
what to do if something's missing.

**Everything is in this repository.** The extraction engine's source is bundled in
[`vendor/`](vendor), so installing does not depend on any other project staying online.
Nothing is fetched from third-party repositories at install time.

---

## Use it

**One game:**

```bash
ps4pkg extract "MyGame.pkg"
```

**A whole folder of them:**

```bash
cd /Volumes/Games/PS4
ps4pkg batch
```

**See what you've got before committing to anything:**

```bash
ps4pkg check .
```
```
  game     EP1063-CUSA13198_00-USOTSUKIHIME0001-A0100-V0100.pkg
  game     FINAL.FANTASY_CUSA33818_v1.00.pkg
  update   FINAL.FANTASY_CUSA33818_v1.20.pkg
```

**All commands:**

| Command | What it does |
|---|---|
| `ps4pkg extract <game.pkg> [folder]` | Extract one package. Goes next to the `.pkg` unless you name a folder. |
| `ps4pkg batch [folder]` | Extract every `.pkg` in a folder, one after another. |
| `ps4pkg check [file or folder]` | Is it a game, an update, or DLC? |
| `ps4pkg install` | Build or rebuild the extraction engine. |
| `ps4pkg doctor` | Check that everything is in place. |
| `ps4pkg version` | Version. |

---

## Then in shadPS4

Open shadPS4, go to **Settings → Paths**, and point the game folder at the folder
holding your extracted games. They show up with proper names and cover art.

---

## What it will and won't do to your files

- **Your `.pkg` files are never touched.** Not moved, not deleted, not modified.
- **Nothing is ever overwritten.** Already extracted that game? It says so and stops,
  in under a second, instead of grinding through it again.
- **Ctrl-C is safe.** The half-finished folder is removed, so you never end up with a
  broken game that looks real.
- **A failed extraction leaves nothing behind.** If the engine stops early or reports a
  problem, the partial output is cleaned up rather than presented as a working game.
- **Free space is checked first**, so you don't fill a drive halfway through.

---

## Games, updates and DLC

`ps4pkg` reads what a package actually is and labels the folder to match:

```
The Liar Princess and the Blind Prince [CUSA13198]
FINAL FANTASY [CUSA33818]
FINAL FANTASY [CUSA33818] (Update)
Some Game [CUSA01234] (DLC)
```

A base game folder has `eboot.bin` and is bootable. Updates and DLC are add-on content
and are marked as such, so you always know what you're looking at.

---

## If something goes wrong

**`command not found: ps4pkg`**
Open a new terminal window. If it persists, run `export PATH="$HOME/.local/bin:$PATH"`.

**Something's missing**
Run `ps4pkg doctor` — it lists what's present and what isn't.

**The build failed**
Usually a missing dependency. Try `brew install cmake zlib` and then `ps4pkg install`.

**"this is not a readable PS4 package"**
The file isn't a real PS4 package, or the download is incomplete or corrupted.
Check the file size against where you got it from.

**Extraction is slow**
Extraction decrypts as it goes, and external drives are the usual bottleneck.
A 2 GB game over USB takes a few minutes; the same game on an internal SSD is far
quicker. The ETA is live, so you always know where you stand.

**It says "Already extracted"**
You've done that one before. Delete the existing folder if you want to redo it.

---

## How it works

The actual extraction is done by `pkg_extractor` from
[AzaharPlus/shadPS4Plus](https://github.com/AzaharPlus/shadPS4Plus) — the PKG handling
code that used to live inside shadPS4 itself, which makes it the most faithful choice
available.

That project publishes Windows and Linux builds only. `ps4pkg` bundles the sources it
needs in [`vendor/`](vendor), applies a small macOS compatibility fix (macOS has no
`fseeko64`; its `fseeko` is already 64-bit), builds them against Homebrew's zlib, and
wraps the result in an interface designed for humans: live progress, real game names
read from `param.sfo`, safe interrupts, and sensible refusal to destroy anything.

The bundled code is redistributed under its original licenses, with its origin,
exact commit, and the one modification documented in
[`vendor/NOTICE.md`](vendor/NOTICE.md). Only the files required to build the extractor
are included — not the rest of the emulator.

---

## For AI agents

If you are an AI assistant setting this up for someone, here is the whole job.

**Install:**

```bash
curl -fsSL https://raw.githubusercontent.com/Ashref-dev/ps4pkg/main/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
ps4pkg doctor
```

`ps4pkg doctor` exits after listing status; every line marked `●` in green is fine.

**Extract:**

```bash
ps4pkg extract "/absolute/path/to/Game.pkg"
```

**Notes that matter when running this non-interactively:**

- Progress is rendered with carriage returns. When capturing output, pipe it through
  `tr '\r' '\n'` or you will see one unreadable line.
- Extraction is genuinely slow on external drives (minutes for multi-GB games). It is
  not hung. Use a generous timeout — 30+ minutes for large titles — and do not kill it
  just because output looks static between file boundaries.
- Exit code is `0` on success, `1` on failure, `130` if interrupted.
- `ps4pkg check <file>` is fast and read-only. Use it to classify packages before
  committing to long extractions.
- Never delete or move the user's `.pkg` files. The tool never does; neither should you.
- The tool refuses to overwrite. If it reports "Already extracted", that is expected
  behaviour and not an error to work around.
- Verify success by confirming `eboot.bin` exists inside the resulting folder. For a
  base game it must be there; for updates and DLC it legitimately is not.

**Do not** attempt to make encrypted or incomplete packages work by patching around
failures. If extraction fails, report it plainly to the user.

---

## Credits

Built by **Achraf Ben Abdallah** — [@Ashref-dev](https://github.com/Ashref-dev)

Extraction engine: [AzaharPlus/shadPS4Plus](https://github.com/AzaharPlus/shadPS4Plus) (GPL-2.0),
derived from [shadPS4](https://github.com/shadps4-emu/shadPS4).

`ps4pkg` is licensed **GPL-2.0-or-later**, matching the shadPS4 code it builds on.
See [LICENSE](LICENSE).

Use it with games you own. This project does not provide, endorse, or assist with
obtaining copyrighted material.

