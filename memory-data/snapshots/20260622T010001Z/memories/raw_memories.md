# Raw Memories

Merged stage-1 raw memories (stable ascending thread-id order):

## Thread `019ea17d-818b-7020-b868-bd7a2b1eada4`
updated_at: 2026-06-10T10:35:11+00:00
cwd: \\?\D:\OpenRadioss
# REDACTED: sensitive-looking memory line
rollout_summary_file: 2026-06-07T09-50-17-Xrp2-openradioss_thin_plate_acceleration_reporting.md

---
description: OpenRadioss thin-plate impact acceleration diagnosis and report export; outcome partial/uncertain because the solver-side sensor patch compiled but the run never reached a validated NC=0 data-producing state, while the user requested progress reports and a desktop markdown export.
task: diagnose thin-plate through-thickness acceleration anomaly; build a report and export markdown to Desktop
task_group: OpenRadioss / solver-debugging
task_outcome: partial
cwd: D:\OpenRadioss
keywords: OpenRadioss, accele.F, resol.F, ifx, ninja, TEMP, TMP, COMMON, sensor_patch_acceleration.csv, run_sensor_engine.cmd, test_0001.rad, starter_win64.exe, engine_win64_smp.exe, oneAPI, MSVC
---
### Task 1: Thin-plate acceleration anomaly investigation + markdown report export

task: diagnose and explain abnormal through-thickness acceleration attenuation in runs/test; modify solver-side sensor output and export progress report markdown to Desktop
task_group: OpenRadioss / transient solver debugging
task_outcome: partial

Preference signals:
- when the user asked to 鈥滄妸娌＄敤鐨勭粨鏋滐紝鏁版嵁绛夐兘娓呯悊娓呯悊鈥? they want old run artifacts aggressively removed before new experiments, not kept around for later inspection.
- when the user asked for 鈥滃厛杈撳嚭涓€涓樁娈垫€х殑鎶ュ憡锛屽憡璇夋垜浣犻兘鐢ㄤ簡鍝簺鏂规硶璇曢獙锛岃繕宸粈涔堟病鏈夊畬鎴愶紝鐩墠鏈変粈涔堣繘灞曗€? they want interim status written clearly with attempted methods, results, and remaining work instead of a vague summary.
- when the user asked 鈥滅粰鎴憁arkdown鏂囦欢锛岃緭鍑哄埌妗岄潰鈥? they want deliverables written as a Markdown file on the Desktop, not just pasted in chat.

Reusable knowledge:
- On this Windows OpenRadioss setup, `ifx` preprocessing can fail with `error #10112: redirect_io: fopen(...) for stdout/stderr failed` unless `TEMP` and `TMP` are redirected to a writable workspace directory such as `D:\OpenRadioss\scratch\tmp` before invoking `ninja`.
- For incremental engine rebuilds, setting explicit `PATH`, `LIB`, and `INCLUDE` entries for oneAPI/compiler/MSVC/Windows SDK was sufficient to make `ninja -j 1 engine_win64_smp.exe` succeed once the temp-dir issue was fixed.
- Appending new variables to an existing legacy Fortran `COMMON /ACC_SENSOR_I/` block was risky; a later attempt that introduced `ISENS_MAPPED` inside the existing common was followed by abnormal engine behavior. Moving the new state to a separate `COMMON /ACC_SENSOR_MAP_I/` was the safer layout.
- The source-level modifications were concentrated in `D:\OpenRadioss\scratch\OpenRadioss-src\engine\source\assembly\accele.F` and the call site in `engine/source/engine/resol.F`.
- The engine run repeatedly wrote only the header of `engine_stdout.log` / `test_0001.out` and never reached `NC=0` / a useful sensor CSV after the sensor-mapping experiments, so the solver-side sensor patch still needs a minimal diagnostic or rollback path before further long runs.
- A clean report file was successfully written to `C:\Users\Administrator\Desktop\OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md`.

Failures and how to do differently:
- The first sensor-mapping implementation tried to scan and map nodes in a way that was too heavy for a very large model, and later runs appeared to stall before the time loop; next attempts should avoid per-step full-node rescans and keep any new per-cycle logic minimal.
- Rebuild attempts via nested `cmd /c` strings were fragile and often failed silently; the reliable path was to use PowerShell directly with explicit environment variables and to capture `ninja` output with `Tee-Object`.
- Long foreground engine runs are not viable on this machine; even shortened `/RUN` windows were still interrupted by tool timeouts while the engine was still in early initialization. Future runs should prefer detached/background execution plus log polling, or a much smaller diagnostic window.
- The old results in `runs\test` were repeatedly a source of confusion; the working pattern is to wipe `testA*`, `.rst`, `testT01*`, logs, `.ctl`, and temp files before each new attempt, while keeping only the input deck(s) and the current control file.

References:
- `D:\OpenRadioss\runs\test\test.k` 鈥?original large LS-DYNA deck used for the thin-plate impact case.
- `D:\OpenRadioss\runs\test\test_0001.rad` 鈥?repeatedly edited engine input for shortened windows and output control.
- `D:\OpenRadioss\runs\test\run_sensor_engine.cmd` 鈥?run script that sets OpenRadioss/oneAPI environment and invokes the rebuilt engine.
- `D:\OpenRadioss\scratch\OpenRadioss-src\engine\source\assembly\accele.F` 鈥?main source file modified for trace/sensor output and mapping experiments.
- `D:\OpenRadioss\scratch\OpenRadioss-src\engine\source\engine\resol.F` 鈥?call site updated to invoke `ACC_TRACE_STATE` before `ACCELE`.
- `D:\OpenRadioss\Desktop\OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md` 鈥?final Markdown report requested by the user.
- Exact ifx failure from earlier build attempt: `ifx: error #10112: redirect_io: fopen("C:\Users\ADMINI~1\AppData\Local\Temp\82752000000010252\827522clangdashv4") for stdout failed` and `stderr failed`.
- Exact `ninja` diagnostic that showed the source touched was being rebuilt: `ninja explain: output CMakeFiles/engine_win64_smp.dir/source/assembly/accele.F-pp.f older than most recent input D:/OpenRadioss/scratch/OpenRadioss-src/engine/source/assembly/accele.F`.
- The Desktop markdown filename: `OpenRadioss_钖勬澘鍔犻€熷害寮傚父闃舵璁板綍.md`.

