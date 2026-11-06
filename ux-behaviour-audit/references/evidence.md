# Shipping the fixes

The audit edits nothing. When the user approves fixes, ship them so each one can be judged alone and is proven, not described.

## One finding, one change

- One branch per finding, each from the upstream main, so the owner can take some and leave others. Check the product's contribution rules first: commit style, changelog line, whether an issue comes before a PR, whether new visible behaviour needs a switch.
- New visible behaviour on a surface the owner keeps minimal ships behind a switch, off by default (case CS37).
- Before filing, merge every branch together in a throwaway branch and run the tests, so the set lands cleanly in any order. Expect only changelog conflicts.
- With more than three findings, hand each to its own delegate or a fresh thread, carrying the report path, the finding, its rule from the philosophy, and these steps. The audit thread then stays small enough to review the results.

## Proof

- **A test that fails on main and passes on the branch.** Run it against a frozen build of main as well as the branch, and put both results in the PR. A test that already fails on main is noted as such, not fixed in passing.
- **Before and after pictures.** Capture the same steps on the main build and the branch build, side by side or stacked, with a caption per step naming the key or click. For motion or a drag, a GIF or MP4 of both. Clear the frame folder between runs so two runs never mix, and use a font that has the key glyphs (⌘ ⇧ ⌥) for captions.
- **A manual check for the owner.** The exact command that launches a disposable copy of the branch build and the steps to try, for what the driver cannot show (a real keyboard, a trackpad, Reduce Motion).

## Hosting images on someone else's repo

`gh issue create --attach` and `gh pr create --attach` need write access to the repository. On a repo you only fork, put the images in a secret gist (`gh gist create` refuses binary files, so create it with a text file, clone it with `git -c credential.helper='!gh auth git-credential' clone`, add the images, push), then link the raw URLs in the issue or PR.

## After review

Read the owner's replies before proposing more of the same kind. A fix cut for style is a rule of the product's philosophy: record it where the next audit will read it (the project's agent notes or memory), and keep it out of later reports.
