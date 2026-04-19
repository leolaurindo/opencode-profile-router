# Opencode Profile Router

Tiny profile wrapper for OpenCode.

Compatible with the `opencode` version in `.opencode-version`.

OpenCode supports custom config and data locations through environment variables, but it does not have a built-in profile system for multiple auth contexts from the same provider. For example, separate personal and work ChatGPT logins are not supported out of the box.

`opencode-router` adds a lightweight profile layer on top of OpenCode. Each profile can have its own auth state, data root, and OpenCode config, with optional full config isolation when needed.

This is also useful when you want to use your company or team OpenCode setup, such as shared harnesses, skills, or tools, without interfering with your personal workflow. With full config isolation, a profile can behave like a separate global OpenCode setup.

This is different from a project `.opencode/` setup. Project config is repo-scoped and discovered from the current directory up to the nearest Git root. It can override config for that project, but it does not provide separate provider login state by itself.

With `opencode-router`, you can:

- define named profiles with separate auth and data roots;
- route profiles by path. E.g.: "always open `work` profile for anything under `~/work`" instead of your normal opencode profile, unless bypassing with `opencode-router profile default`;
- use profile-specific OpenCode config;
- optionally fully isolate config. By default, profiles still inherit your shared global OpenCode config. Full isolation is optional.
- For **the brave and true**, `opencode-router` can also intercept the `opencode` command so routing happens automatically from your shell when calling `opencode`. This is convenient, but also more prone to bugs and fragile than calling `opencode-router` explicitly.


## Quick Start

This is essentially a shell script, so you can make your own setup. Just make sure it can be called from anywhere. The recommended one, however, is as follows:

```sh
git clone https://github.com/leolaurindo/opencode-profile-router ~/.local/share/opencode-profile-router
mkdir -p "$HOME/.local/bin"
ln -sf "$HOME/.local/share/opencode-profile-router/opencode-router" "$HOME/.local/bin/opencode-router"
chmod +x "$HOME/.local/share/opencode-profile-router/opencode-router"

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

Optionally, create an easy alias:

```sh
echo 'alias ocr="opencode-router"' >> ~/.bashrc
echo 'alias opr="opencode-router"' >> ~/.zshrc
```

## Setup your first profile:

```sh
opencode-router new work "$HOME/work"
opencode-router profile work auth login
cd "$(opencode-router show work --config)"
# edit opencode.jsonc here using normal OpenCode config syntax
opencode-router "$HOME/work/my-repo"
```

See `DOCS.md` for commands, routing details, managed paths, config layering, and shell setup.


## Intercepting `opencode`

See `DOCS.md` or `opencode-router --help` to understand how opencode args are passed through.

```sh
alias opencode="opencode-router"
```

Or:

```sh
opencode() {
  opencode-router "$@"
}
```

You can bypass the wrapper with `command opencode` or by forcing `opencode profile default`.

## Contributing

Issues and pull requests are welcome.

### TODOs

- add a regression script for the main routing and profile flows
- add a script for automating the allowlist verification

## License

0BSD. See `LICENSE`.
