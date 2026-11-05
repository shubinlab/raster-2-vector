# Presentation benchmark: GitHub repositories above 200,000 stars

Source: [Top GitHub repositories](https://nazsam.github.io/github-top-repos/most-starred.html), snapshot of **2026-11-04 13:30 UTC**, top 100. The published ranking shows **31** entries strictly above 200,000 stars. This is a reproducible ranking snapshot, **not an exhaustive GitHub-wide live census**. Stars change continuously. Detailed README/structure comparisons focused on relevant examples; all 31 were identified in the snapshot, not individually audited file by file.

| # | Repository | Stars in source snapshot |
|--:|---|---:|
| 1 | [codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) | 559,665 |
| 2 | [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | 530,679 |
| 3 | [public-apis/public-apis](https://github.com/public-apis/public-apis) | 495,987 |
| 4 | [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp) | 458,527 |
| 5 | [morluto/rea](https://github.com/morluto/rea) | 429,332 |
| 6 | [EbookFoundation/free-programming-books](https://github.com/EbookFoundation/free-programming-books) | 400,845 |
| 7 | [openclaw/openclaw](https://github.com/openclaw/openclaw) | 393,879 |
| 8 | [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | 376,740 |
| 9 | [nilbuild/developer-roadmap](https://github.com/nilbuild/developer-roadmap) | 371,227 |
| 10 | [jwasham/coding-interview-university](https://github.com/jwasham/coding-interview-university) | 363,885 |
| 11 | [awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) | 333,618 |
| 12 | [vinta/awesome-python](https://github.com/vinta/awesome-python) | 332,375 |
| 13 | [mattpocock/skills](https://github.com/mattpocock/skills) | 312,373 |
| 14 | [obra/superpowers](https://github.com/obra/superpowers) | 312,188 |
| 15 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 296,897 |
| 16 | [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) | 288,989 |
| 17 | [996icu/996.ICU](https://github.com/996icu/996.ICU) | 277,209 |
| 18 | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | 272,051 |
| 19 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | 260,433 |
| 20 | [trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) | 255,792 |
| 21 | [torvalds/linux](https://github.com/torvalds/linux) | 254,363 |
| 22 | [react/react](https://github.com/react/react) | 251,918 |
| 23 | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | 229,325 |
| 24 | [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) | 225,856 |
| 25 | [anomalyco/opencode](https://github.com/anomalyco/opencode) | 224,500 |
| 26 | [vuejs/vue](https://github.com/vuejs/vue) | 212,493 |
| 27 | [ossu/computer-science](https://github.com/ossu/computer-science) | 210,705 |
| 28 | [n8n-io/n8n](https://github.com/n8n-io/n8n) | 209,536 |
| 29 | [DigitalPlatDev/FreeDomain](https://github.com/DigitalPlatDev/FreeDomain) | 207,066 |
| 30 | [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | 205,160 |
| 31 | [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow) | 201,296 |

## Practical design patterns adopted

- **[openclaw](https://github.com/openclaw/openclaw)**: clear onboarding, platform guidance and security docs. We added platform-specific installation and security caveats.
- **[obra/superpowers](https://github.com/obra/superpowers)** and **[mattpocock/skills](https://github.com/mattpocock/skills)**: portable agent skill layout and predictable installation. We retained a root `SKILL.md` and added the maintained skills CLI workflow.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: useful CLI examples and troubleshooting. We added separate skill/engine quick starts, doctor checks and explicit limitations.
- **[n8n](https://github.com/n8n-io/n8n)**: compelling product introduction and organized docs. We added a short product pitch, navigation table and meaningful status badges.
- **[build-your-own-x](https://github.com/codecrafters-io/build-your-own-x)**: a scannable README. We separated quick start from deep documentation.

## Missing features before this revision

1. A portable agent installation workflow beyond Codex and Claude Code.
2. Realistic Windows/macOS/Linux engine instructions and warnings about native dependencies.
3. A reproducible Docker fallback for cross-platform execution.
4. CI workflows, versioned change history and installer regression tests.
5. Security, compatibility and contribution policy documents.
6. Prominent examples and badges that represent actual status, not invented claims.
7. An explicit license decision. **No open-source license has yet been granted**: public visibility alone is not licensing.

## Design choices deliberately avoided

No fabricated stars, download counters, success rates or platform coverage. No claim of universal 95% mask IoU or aesthetic perfection. No heavyweight monorepo or build tooling for a compact Python skill.
