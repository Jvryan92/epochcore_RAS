# 🛠️ Merge Multiple Repositories into `Jvryan92/epochcore_RAS`

## Overview

This pull request merges the following repositories as subdirectories into the main repository `Jvryan92/epochcore_RAS`:

- [`EpochCore5/epoch5-template`](https://github.com/EpochCore5/epoch5-template)
- [`Jvryan92/StategyDECK`](https://github.com/Jvryan92/StategyDECK)
- [`Jvryan92/epoch-mesh`](https://github.com/Jvryan92/epoch-mesh)

All source code, documentation, and assets from each repo are preserved in their respective subfolders.

---

## Merge Strategy

- Each repository is imported as a subdirectory:
  - `epoch5-template/`
  - `StategyDECK/`
  - `epoch-mesh/`
- Commit history for each imported repo is preserved (if using `git read-tree`).
- No secrets or environment files (.env) are imported. Only safe templates (.env.example) are kept.
- `.gitignore` is updated to prevent accidental commits of sensitive files.
- Main README is updated to reflect the new structure.

---

## Instructions (for local merge)

```bash
# 1. Clone the target repository
git clone https://github.com/Jvryan92/epochcore_RAS.git
cd epochcore_RAS

# 2. For each repo to import:
# Example for epoch5-template
git remote add epoch5-template https://github.com/EpochCore5/epoch5-template.git
git fetch epoch5-template
git read-tree --prefix=epoch5-template/ -u epoch5-template/main
git commit -m "Import epoch5-template as subdirectory"

# Repeat for StategyDECK and epoch-mesh
git remote add StategyDECK https://github.com/Jvryan92/StategyDECK.git
git fetch StategyDECK
git read-tree --prefix=StategyDECK/ -u StategyDECK/main
git commit -m "Import StategyDECK as subdirectory"

git remote add epoch-mesh https://github.com/Jvryan92/epoch-mesh.git
git fetch epoch-mesh
git read-tree --prefix=epoch-mesh/ -u epoch-mesh/main
git commit -m "Import epoch-mesh as subdirectory"

# 3. Push to main branch
git push origin main
```

---

## Verification Checklist

- [ ] All source repos are imported as subdirectories.
- [ ] No `.env` or secret files are present in the merged repo.
- [ ] `.env.example` files are present for safe configuration.
- [ ] `.gitignore` is updated to include sensitive file patterns.
- [ ] Main README lists and describes each imported project.
- [ ] Tests and CI/CD run successfully for each module.

---

## Post-Merge Tasks

- Update documentation as needed.
- Refactor or integrate code if you want tighter coupling between modules.
- Communicate changes to collaborators.

---

**If you want to skip preserving commit history or flatten file structures, update the instructions above.  
Let me know if you want a second copy or a variation (for a different merge scenario)!**