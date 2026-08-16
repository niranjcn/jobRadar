## Description

<!-- Summarize the change and the motivation behind it. What problem does this solve? -->



## Related Issue(s)

<!-- Link related issues. Use "Closes #123" to auto-close on merge -->
Closes #

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would change existing behavior)
- [ ] 📝 Documentation update
- [ ] 🎨 Style / formatting (no logic change)
- [ ] ♻️ Refactor (no functional change, no new feature)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update
- [ ] 🔧 Chore / build / CI config

## How Has This Been Tested?

<!-- Describe the tests you ran and how to reproduce them. CI runs these checks
on every PR, so list what you ran locally too. -->

- [ ] Backend lint + format: `cd backend && ruff check . && ruff format --check .`
- [ ] Backend unit tests: `cd backend && python -m pytest tests/test_unit.py`
- [ ] Frontend tests: `cd frontend && npm test`
- [ ] Manual testing (docker compose smoke test, etc.)

**Test Configuration:**
- OS:
- Version:

## Migration / Config Requirements

<!-- New migrations in backend/migrations/? New env vars? Changes to
sources.json, README, docker-compose.yml, or render.yaml? If none, say "None". -->

None

## Screenshots / Demo (if applicable)

<!-- Drag and drop images or a short GIF here -->



## Checklist

- [ ] My code follows the style guidelines of this project (ruff, see `backend/pyproject.toml`)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Notes

<!-- Anything else reviewers should know — deployment steps, rollback plan, follow-up work, etc. -->

@coderabbitai summary