---
name: pyinstaller-windows-packaging
description: >
  Use when packaging Python desktop applications on Windows with PyInstaller,
  especially when handling C-extension packages, DLL collection, hidden imports,
  app resources, RTK or PowerShell quoting, executable size, icons, and frozen
  runtime paths.
---

# PyInstaller Windows Packaging

## Goal

Build Windows PyInstaller executables with the needed runtime files while
avoiding bloated dependency collection and misleading import-warning fixes.

## Use When

- Packaging a Python GUI or desktop app into a Windows `.exe`.
- PyInstaller warns about missing modules from packages that expose attributes
  through a `.pyd` or DLL-backed package.
- The build uses RTK, PowerShell, icons, Matplotlib, NumPy, pandas, or package
  data files.

## Do Not Use When

- The task is a pure Python library build with no frozen executable.
- The target platform is not Windows and no PyInstaller behavior is involved.

## Inputs

- Entry script or `.spec` file.
- Required icons, data files, and runtime package dependencies.
- Existing build command if available.

## Workflow

1. Recall package-specific memory before changing the spec.
2. Start from the existing `.spec` or last known good PyInstaller command.
3. Identify C-extension or DLL-backed packages that need whole-package
   collection.
4. Use targeted collection for such packages, for example `--collect-all
   lsreader` when a package wraps `.pyd` and DLL files.
5. Treat warnings such as `package.DataType` or `package.D3plotReader` as
   possibly misleading when those names are exported attributes, not modules.
6. Avoid broad `collect_all` for large common packages such as NumPy, pandas,
   and Matplotlib unless debugging a real missing dependency.
7. Let PyInstaller hooks handle common scientific packages and force only the
   specific backend or resource that is needed, such as Matplotlib `Agg`.
8. In frozen mode, resolve app paths from `sys.executable` and bundled resources
   from `sys._MEIPASS` with a source-tree fallback.
9. Handle Windows shell quoting deliberately. For PowerShell cmdlets under RTK,
   run PowerShell explicitly rather than passing cmdlet names directly.
10. Build, inspect warnings, and test the generated executable.

## Validation

- Generated `.exe` starts on the target machine.
- Required `.pyd`, DLL, icon, and data files are present.
- Build warnings are reviewed but not blindly patched with broad hidden imports.
- Executable size and build time are reasonable after dependency changes.

## Failure Modes

- Runtime import fails for a `.pyd` package: collect the whole package or the
  specific binary/data files.
- Huge executable and many pytest warnings: remove broad `collect_all` for
  NumPy, pandas, or Matplotlib.
- RTK cannot resolve a PowerShell cmdlet: run `rtk powershell -NoProfile
  -Command ...`.
- `$` disappears inside nested PowerShell commands: escape it for the outer
  shell.

## RAG Handoff

Search memory for `pyinstaller`, `packaging`, `lsreader`, `rtk`, `powershell`,
`frozen`, and the project name before changing packaging commands.
