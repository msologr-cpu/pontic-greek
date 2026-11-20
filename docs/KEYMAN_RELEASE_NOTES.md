# Keyman Release Notes & v6.1 Upgrade Checklist

Target upstream path in `keymanapp/keyboards`: `release/p/pontic_greek/`

## Changes in v6.1 (From v6.0 Merged in PR #4180)

1. **`source/pontic_greek.kmn`**
   - Bumped `store(&VERSION)` to `'15.0'` and `store(&KEYBOARDVERSION)` to `'6.1'`.
   - Translated all header and rule comments to English; cleaned `store(&MESSAGE)` to `'Pontic Greek Keyboard'`.
   - Added `begin PostKeystroke > use(PostKeystroke)` and `group(PostKeystroke) readonly` to auto-return touch layouts from `shift` back to `default` after character insertion, while preserving `caps` lock and active dead keys (`dk(tonos)`, `dk(dialytika)`, `dk(pontic)`, `dk(pontic_tonos)`).
   - Added `[SHIFT T_TONOS]` and `[SHIFT T_PONTIC_DK]` post-fix rules, `[SHIFT K_SPACE]` handling, and bi-directional dead-key ordering (`dk(tonos) + [T_PONTIC_DK] > dk(pontic_tonos)`).

2. **`source/pontic_greek.keyman-touch-layout`**
   - Added explicit `"caps"` layer to both `phone` and `tablet` platforms with `"*ShiftedLock*"` on `K_SHIFT` (`nextlayer: "default"`) and `"layer": "shift"` on character/diacritic keys.
   - Updated `shift` layer `K_SHIFT` label to standard `"*Shifted*"` (`sp: 2`, `nextlayer: "default"`).
   - Verified zero `"nextlayer"` overrides on letter keys inside `shift` / `caps`.

3. **Documentation & Package**
   - Synced upstream files (`source/pontic_greek.kvks`, `source/readme.htm`, `source/help/pontic_greek.php`, `LICENSE.md`, `HISTORY.md`, `README.md`) with updated v6.1 auto-shift and Caps Lock instructions.
   - Compiled cleanly with `@keymanapp/kmc 18.0.255` (`<CompilerWarningsAsErrors>True</CompilerWarningsAsErrors>` — zero warnings/errors) and verified all mobile sequences with Node runtime simulation.
   - **Note for upstream PR:** In `keymanapp/keyboards/release/p/pontic_greek/source/pontic_greek.kps`, restore the shared font paths (`..\..\..\shared\fonts\grek\pontic-sans\PonticSans-Regular.ttf` and `..\..\..\shared\fonts\grek\pontic-sans\OFL.txt`) before opening the PR against `keymanapp/keyboards`.
