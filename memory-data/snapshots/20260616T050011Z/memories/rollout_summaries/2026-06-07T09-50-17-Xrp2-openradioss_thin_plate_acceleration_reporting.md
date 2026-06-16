thread_id: 019ea17d-818b-7020-b868-bd7a2b1eada4
updated_at: 2026-06-10T10:35:11+00:00
# REDACTED: sensitive-looking memory line
cwd: \\?\D:\OpenRadioss
git_branch: master

# OpenRadioss thin-plate acceleration diagnosis, solver instrumentation, and report export

Rollout context: the user wanted the OpenRadioss thin-plate impact case rerun from the solver/source-code level, old results in `D:\OpenRadioss\runs\test` cleaned first, the reason for through-thickness acceleration decay found, a physically reasonable fix proposed/validated, and then a progress report exported as Markdown to the Desktop. The later part of the thread narrowed to reducing runtime/memory pressure, then to exporting a Markdown status file.

## Task 1: Thin-plate acceleration anomaly investigation and solver-side sensor work

Outcome: partial

Preference signals:

- the user explicitly asked to 鈥滄妸娌＄敤鐨勭粨鏋滐紝鏁版嵁绛夐兘娓呯悊娓呯悊鈥?before reruns, indicating that future attempts should aggressively wipe stale outputs, restarts, logs, `.ctl`, `testA*`, `testT01*`, and temp artifacts before trusting new results.
- the user asked for 鈥滃厛杈撳嚭涓€涓樁娈垫€х殑鎶ュ憡锛屽憡璇夋垜浣犻兘鐢ㄤ簡鍝簺鏂规硶璇曢獙锛岃繕宸粈涔堟病鏈夊畬鎴愶紝鐩墠鏈変粈涔堣繘灞曗€?indicating that they want interim reports to enumerate methods tried, outcomes, and remaining gaps rather than a vague status update.
- the user later asked 鈥滅粰鎴憁arkdown鏂囦欢锛岃緭鍑哄埌妗岄潰鈥? which is a durable delivery preference for Markdown artifacts on the Desktop.

Key steps:

- The run directory `D:\OpenRadioss\runs\test` was cleaned multiple times; old `.out/.rst/.csv/.ctl/testA*` outputs were removed, and the run directory was reduced to just the deck and a few control files when needed.
- Starter was rerun successfully on the original `test.k`; it generated `test_0000.out`, `test_0000_0001.rst`, and `test_0001.rad`, with one warning about `12 INCOMPATIBLE KINEMATIC CONDITIONS` but no errors.
- The case was shortened repeatedly (`/RUN` changed from longer windows down to `7e-6`, `3e-6`, `1e-6`, and finally `1e-7`) to try to get a minimal smoke test for the sensor patch.
- The solver source was instrumented in `scratch/OpenRadioss-src/engine/source/assembly/accele.F` to emit a sensor CSV (`sensor_patch_acceleration.csv`) and to trace selected nodes with environment variables.
- The solver call site in `scratch/OpenRadioss-src/engine/source/engine/resol.F` was updated to call `ACC_TRACE_STATE` before `ACCELE`.
- The user鈥檚 鈥渇ront/back鈥?nodes were re-evaluated from the deck topology: the earlier `4875664/4875665/4875666` back-side points were found to be isolated/non-structural because they were not referenced by any `*ELEMENT_*` connectivity. The connected through-thickness chain around the impact column was instead identified as `4787297, 5163987, 4845061, 5163995, 4845062, 5164002, 4845063`.
- The raw TH output confirmed very large nodal acceleration spikes at the connected surface nodes, e.g. `4845063` reached about `1.262297e+12` AZ, while the connected back-side node `4787297` peaked at about `5.685989e+11` AZ. The same-time mismatch and delay were measured and compared to the thickness wave estimate.
- Source inspection of `accele.F` showed that OpenRadioss computes acceleration by dividing assembled force-like quantities by nodal mass (`A = A / MS`) and sets acceleration to zero when `MS <= 0`, which explained why isolated or improperly mapped points could vanish or behave nonphysically.
- The sensor-patch idea evolved into a more physical 鈥減atch acceleration鈥?calculation: sum the forces and masses of selected nodes and output `sum(F)/sum(M)` rather than relying on a single nodal acceleration spike.
- Several heavy execution attempts were limited by machine/tool constraints; the engine often wrote only the startup banner and hardware information, then the foreground command timed out before reaching a useful `NC=0` state.
- Build environment fixes were required to make any source change compile: `TEMP` and `TMP` had to be moved to `D:\OpenRadioss\scratch\tmp`, and explicit oneAPI/MSVC/SDK `PATH`, `LIB`, and `INCLUDE` values had to be set for `ninja`/`ifx`.
- The engine rebuild ultimately succeeded after the temp-directory fix; `ninja` completed the 14-step rebuild and linked `engine_win64_smp.exe` successfully.

Failures and how to do differently:

- The first attempt to add a sensor state into the existing `COMMON /ACC_SENSOR_I/` layout was risky and appeared to destabilize early engine startup; the safer pattern was to put new state into a separate `COMMON /ACC_SENSOR_MAP_I/` instead of extending the original common block.
- Even after the rebuild succeeded, the modified engine still failed to make it to a validated `NC=0` run with a non-empty sensor CSV during the available time windows, so the source-side sensor patch is not yet fully proven.
- Long foreground engine runs on this model were repeatedly interrupted by tool timeouts. Background/monitoring runs were preferable, but some `.cmd`-based launch paths were unreliable and produced only the startup banner without the expected status logs.
- The run scripts became a source of uncertainty when the engine only wrote the header or created a temporary `08_test_...tmp` file; future attempts should add minimal diagnostics or a rollback path before further long runs.

Reusable knowledge:

- On this Windows OpenRadioss setup, the reliable rebuild recipe was: set `TEMP/TMP` to `D:\OpenRadioss\scratch\tmp`, set explicit oneAPI/MSVC/SDK `PATH`, `LIB`, and `INCLUDE`, then run `D:\OpenRadioss\.venv\Scripts\ninja.exe -j 1 engine_win64_smp.exe` from `scratch\OpenRadioss-src\engine\cbuild_engine_win64_smp_ninja`.
- The exact ifx temp-file failure that had to be solved first was `ifx: error #10112: redirect_io: fopen(...) for stdout/stderr failed`; this was fixed by redirecting `TEMP/TMP` to a writable workspace directory.
- The OpenRadioss Windows build system rewrites the engine binary both in the build directory and in `scratch\OpenRadioss-src\exec\engine_win64_smp.exe`; checking both timestamps is useful after each rebuild.
- `accele.F` is the relevant source file for nodal acceleration assembly/division and for any trace/sensor output instrumentation.
- The file-level evidence of the sensor patch being in place is visible in `accele.F`: separate `COMMON /ACC_SENSOR_MAP_I/ ISENS_MAPPED`, `ACC_TRACE_STATE`, and the `ISENS_ACTIVE == 1 .AND. ISENS_MAPPED == 0` mapping guard.
- The Desktop Markdown report was successfully generated at `C:\Users\Administrator\Desktop\OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md`.

References:

1. `D:\OpenRadioss\runs\test\test.k` 鈥?original 43 MB deck used for the thin-plate impact case.
2. `D:\OpenRadioss\runs\test\test_0001.rad` 鈥?repeatedly shortened to `1e-7` for smoke tests; retained `/DT 0.45 0` and `/TFILE/4 1.0e-08` during the experiments.
3. `D:\OpenRadioss\runs\test\run_sensor_engine.cmd` 鈥?run wrapper that sets OpenRadioss/Intel oneAPI environment and emits `engine_runner_status.log`.
4. `D:\OpenRadioss\scratch\OpenRadioss-src\engine\source\assembly\accele.F` 鈥?core source file modified for tracing and sensor patch logic.
5. `D:\OpenRadioss\scratch\OpenRadioss-src\engine\source\engine\resol.F` 鈥?call site where `ACC_TRACE_STATE(NCYCLE,TT,NUMNOD,NODES%NODGLOB)` was inserted before `ACCELE`.
6. `D:\OpenRadioss\Desktop\OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md` 鈥?final Markdown progress file on the Desktop.
7. Exact ifx failure that was resolved before the successful rebuild: `ifx: error #10112: redirect_io: fopen("C:\Users\ADMINI~1\AppData\Local\Temp\82752000000010252\827522clangdashv4") for stdout failed` and the same for stderr.
8. The successful rebuild evidence: `ninja` completed the 14-step build and linked `engine_win64_smp.exe` (`NINJA_EXIT=0`).
9. The raw TH evidence that made the node-selection correction necessary: `testT01.csv` originally showed massive AZ spikes for the connected top node (`4845063`) and a smaller but still large response on the connected bottom node (`4787297`), while the earlier back nodes `4875664/65/66` were not actually structural nodes.

## Task 2: Cleanup of unusable run artifacts

Outcome: success

Preference signals:

- the user asked to remove useless outputs and data, which was interpreted as deleting stale run products rather than archiving them.

Key steps:

- `D:\OpenRadioss\runs\test` was cleaned after the failed/partial run attempts.
- The cleanup removed logs, temporary files, `test_0000.out`, the large `test_0000_0001.rst`, `test_0001.out`, `testT01*`, `testA*`, `.ctl`, and other run debris.
- The cleanup freed about `1.84 GB` of data in the run directory.
- `D:\OpenRadioss\scratch\tmp` and stale build logs under `scratch\OpenRadioss-src\engine` were also cleaned.

Failures and how to do differently:

- None specific to the cleanup itself; the main caution is to preserve `test.k`, the original backup deck, and the current `test_0001.rad` while deleting artifacts.

Reusable knowledge:

- After the cleanup, `D:\OpenRadioss\runs\test` only kept the deck(s) and the small run-control file, which is the right baseline for the next attempt.

References:

- Cleanup command removed roughly `1.84 GB` from `D:\OpenRadioss\runs\test`.
- Remaining preserved files after cleanup: `test.k`, `test_original_before_sensor_rigid_v6.k`, `test_0001.rad`, and `run_sensor_engine.cmd`.

## Task 3: Markdown status report exported to Desktop

Outcome: success

Preference signals:

- the user explicitly requested a Markdown file on the Desktop.

Key steps:

- A Markdown status document summarizing the rollout state, experiments, failures, and next steps was created at `C:\Users\Administrator\Desktop\OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md`.
- The file was written in Chinese, consistent with the user鈥檚 language.

References:

- File path: `C:\Users\Administrator\Desktop\OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md`.
- Filename: `OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md`. 


