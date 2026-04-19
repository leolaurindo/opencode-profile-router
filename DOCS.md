# Docs

`opencode-router` is an explicit wrapper around `opencode`.

Compatible with the `opencode` version in `.opencode-version`.

`work` will be used as the main "example" of a profile name. Whenever it shows, its a <profile-name>.

## Mental Model

- A profile is a named set of OpenCode overrides.
- Profile files live at `~/.config/opencode-router/profiles/<name>.env`.
- Profile files are router metadata, parsed as data by the script, not sourced as shell.
- Each profile gets its own managed config area at `~/.config/opencode-router/profiles/<name>/config/opencode`.
- Each profile gets its own managed data root at `~/.local/opencode-profiles/<name>`.
- Managed config/data/state paths are derived from the profile name, not configured per profile file.
- By default, profile config is an extra layer on top of your normal shared `~/.config/opencode` config.
    - With `--full-config-isolation`, the profile uses its own `XDG_CONFIG_HOME` and stops inheriting the shared global OpenCode config.
- This is different from project `.opencode/`: project config is repo-scoped and can override settings for that repo, but it does not create separate provider login state.
- Routing is by longest matching path prefix. More specific paths win, so `~/work/project/` beats `~/work`.
- If no profile is called or resolved, `opencode-router` runs plain `opencode` with your "normal" global configs.
- `opencode-router profile default ...` forces one invocation to run as plain `opencode` with no router profile overrides.
- OpenCode args are passed through unchanged. The router only inspects enough argv to choose a routing target.
- The routing target comes from `--dir <path>`, `--dir=<path>`, the first positional directory when it is not in the built-in top-level OpenCode command allowlist, `tui <dir>`, or the current working directory.
- `opencode-router path/to/dir` uses that path for routing, but it does not `cd` before launching OpenCode.

## Commands

| Command | Purpose |
| --- | --- |
| `opencode-router [opencode args...]` | Run OpenCode with automatic profile routing |
| `opencode-router run [opencode args...]` | Explicit form of the default routed run |
| `opencode-router profile <name\|default> [opencode args...]` | Force one profile, or plain OpenCode, for a single invocation |
| `opencode-router which [--verbose] [opencode args...]` | Preview routing without launching OpenCode |
| `opencode-router new [name] [path]` | Create a managed profile |
| `opencode-router list` | List configured profiles |
| `opencode-router show <name\|default> [--config\|--config-file\|--data\|--profile-file]` | Show one profile, or print one specific path field |
| `opencode-router remove <name> [--dry-run\|--yes]` | Remove one managed profile |
| `opencode-router remove --prune [--dry-run\|--yes]` | Delete stale managed directories |
| `opencode-router remove --all [--dry-run\|--yes]` | Remove all managed router data |
| `opencode-router help` | Print CLI usage |

### `opencode-router [opencode args...]`

Run OpenCode with automatic profile routing.

- If a profile matches, `XDG_DATA_HOME` is overridden for that process.
- If the profile enables state isolation, `XDG_STATE_HOME` is also overridden.
- By default, if the profile has config files or a config dir, `OPENCODE_CONFIG_DIR` is set for that process.
- `OPENCODE_CONFIG` is only set when the profile's `opencode.jsonc` file exists.
- With full config isolation, `XDG_CONFIG_HOME` is set for that profile instead.
- If the first positional argument is an existing directory and not an OpenCode subcommand, that directory is used for routing.
- If nothing matches, it runs plain `opencode`.

### `opencode-router run [opencode args...]`

Explicit form of the default routed run.

Useful if you want the routing behavior to be obvious in a script or shell alias.

### `opencode-router profile <name|default> [opencode args...]`

Force one specific profile for a single invocation.

Use this when you do not want path-based auto-selection.

Use `default` to bypass router profile overrides and run plain `opencode` for one invocation.

Example:

```sh
opencode-router profile work auth login # auth login are passedthrough opencode argg
opencode-router profile default run "hello"
```

### `opencode-router which [--verbose] [opencode args...]`

Show what the router would do without launching OpenCode.

- Default output is just the selected profile name, such as `work` or `default`.
- With `--verbose`, it prints the resolved target dir plus the same profile details as `show` for the currently resolved profile.

Examples:

```sh
opencode-router which ~/work/my-repo
opencode-router which --verbose ~/work/my-repo
```

### `opencode-router new [name] [path]`

Create a new managed profile.

If `name` or `path` is missing, it prompts interactively.

Arguments:

- `name`: profile name, such as `work`
- `path`: optional root path that activates the profile, such as `~/work`

Flags:

- `--description <text>`: set `PROFILE_DESCRIPTION`
- `--use-state`: also isolate `XDG_STATE_HOME`
- `--full-config-isolation`: isolate config completely from `~/.config/opencode`
- `--no-config`: do not create `opencode.jsonc`
- `--force`: overwrite the profile file, and rewrite the config file if this command created one

By default, `new` creates the profile file, managed data root, config directory, and `opencode.jsonc`.

The profile file only stores metadata such as name, description, match path, and isolation flags. Managed runtime paths are derived from the profile name.

If you skip `path`, the profile is created without auto-selection and can still be used with `opencode-router profile <name> ...`.

Example:

```sh
opencode-router new work "$HOME/work" --description "Work profile"
```

### `opencode-router list`

List configured profile names.

### `opencode-router show <name|default> [--config|--config-file|--data|--profile-file]`

Show one profile with its resolved paths and routing settings.

Useful when checking where config and data live for that profile.

- `--config`: print the config directory
- `--config-file`: print the `opencode.jsonc` path
- `--data`: print the data root
- `--profile-file`: print the profile metadata file path

Examples:

```sh
opencode-router show work
opencode-router show work --config
cd "$(opencode-router show work --config)"
opencode-router show work --config-file
```

### `opencode-router remove <name> [--dry-run|--yes]`

Remove one managed profile.

It removes the managed profile file, config directory, and data directory for that profile name.

Flags:

- `--dry-run`: preview removal
- `--yes`: actually remove

Default is dry-run.

### `opencode-router remove --prune [--dry-run|--yes]`

Remove stale managed profile config or data directories that no longer have a matching profile file.

Flags:

- `--dry-run`: preview removal
- `--yes`: actually remove

Default is dry-run.

### `opencode-router remove --all [--dry-run|--yes]`

Remove all managed router data.

It removes:

- `~/.config/opencode-router`
- `~/.local/opencode-profiles`

### `opencode-router help`

Print the CLI usage summary.

You can also use `opencode-router -h` or `opencode-router --help`.
