# Playbook Testing Guide

> **Note:** The testing infrastructure is still being developed. Playbook creators are not expected to add tests to their playbooks yet.

---

## Testing Tags

Use `@test` tags to make existing code blocks testable. These tags **wrap your existing code** and are picked up by CI to run automated tests. The HTML comment tags themselves are invisible to website visitors, but the wrapped code remains visible by default. Add `hidden=true` to hide the code block from the website if needed (e.g., for test-only setup commands).

**Basic syntax — wrap existing code blocks:**

```markdown
<!-- @test:id=install-deps timeout=300 -->
```bash
pip install transformers accelerate
```
<!-- @test:end -->
```

The test tags wrap the code block that users see. No duplication needed — the same code that appears in the playbook is what gets tested.

**Test attributes:**

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `id` | Yes | — | Unique identifier for the test (use kebab-case) |
| `timeout` | No | `300` | Maximum execution time in seconds |
| `continue_on_error` | No | `false` | If `true`, test failure won't fail the CI job |
| `hidden` | No | `false` | If `true`, hides the code block from the website (useful for test-only setup) |

> **Note:** Platform is automatically inferred from the surrounding `@os:` tags. Tests inside `<!-- @os:windows -->` run only on Windows, tests inside `<!-- @os:linux -->` run only on Linux, and tests outside any `@os:` block run on all platforms.

**Supported languages:**

| Language tag | Execution |
|--------------|-----------|
| `bash`, `sh`, `shell` | PowerShell on Windows, Bash on Linux |
| `cmd`, `batch` | Windows CMD |
| `powershell`, `pwsh`, `ps1` | PowerShell |
| `python` | Python interpreter |

**Example: Ordering tests by README position**

Tests run in the order they appear in the README. Place prerequisite steps before the tests that need them:

```markdown
### Create Virtual Environment

<!-- @os:windows -->
<!-- @test:id=create-venv timeout=60 -->
```cmd
python -m venv myenv
myenv\Scripts\activate.bat
```
<!-- @test:end -->
<!-- @os:end -->

### Install Dependencies

<!-- @test:id=install-deps timeout=300 -->
```bash
pip install transformers torch
```
<!-- @test:end -->

### Run the Script

<!-- @test:id=run-script timeout=60 -->
```bash
python run_model.py --help
```
<!-- @test:end -->
```

In this example, `create-venv` runs first, then `install-deps`, then `run-script` — matching the natural reading order of the playbook.

**Example: Platform-specific tests**

Combine with `@os` tags for platform-specific instructions:

```markdown
<!-- @os:windows -->
<!-- @test:id=setup timeout=120 -->
```cmd
pip install torch
python -c "import torch; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=setup timeout=120 -->
```bash
pip3 install torch
python3 -c "import torch; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->
```

**Example: Verification tests (not shown to users)**

For tests that verify things but shouldn't appear in the playbook, place them after visible content:

```markdown
| [run_llm.py](assets/run_llm.py) | Basic LLM script |

<!-- @test:id=verify-scripts timeout=30 -->
```python
import os, sys
missing = [f for f in ['run_llm.py'] if not os.path.exists(f)]
if missing:
    sys.exit(1)
```
<!-- @test:end -->

Both scripts support...
```

**Best practices:**

1. **Wrap, don't duplicate**: Put test tags around existing code blocks instead of writing separate test code
2. **Order matters**: Tests run in README order, so place prerequisites before the steps that need them
3. **Keep tests fast**: Use appropriate timeouts; most tests should complete in under 60 seconds
4. **Handle missing hardware**: CI machines may not have GPUs; tests should handle this gracefully
5. **Test the happy path**: Focus on verifying instructions work, not edge cases

**Running tests locally:**

```bash
python .github/scripts/run_playbook_tests.py --playbook your-playbook-id --platform windows
```

**CI behavior:**

- Tests run automatically on PRs that modify playbook files
- Tests run on self-hosted runners tagged with `Windows` and `halo`
- Tests run in the order they appear in the README
- Test results are uploaded as artifacts for debugging
