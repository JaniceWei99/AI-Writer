# Changelog

This file documents all notable changes to this project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.5.0] - 2026-03-26

### Added

- **Quick-start cards** (P1): ResultPanel empty state shows 3 clickable cards (Write an article / Polish text / Translate content), clicking auto-sets the task type and focuses the input
  - `onQuickStart` callback passes task type to App.tsx
  - WritingForm adds `quickStart` / `onQuickStartConsumed` props, switches task and focuses textarea on receipt
- **Token count animation** (P1): Smooth transition animation when token numbers change (`.token-count-anim` class, `transition: all 0.3s ease-out`)
- **Word count target** (P2-8): WritingForm character count row adds target word count input (`word-target-input`), ResultPanel title bar shows word count progress bar (`.word-count-progress`), progress bar turns green when target is met
  - App.tsx adds `wordCountTarget` / `setWordCountTarget` state
  - ResultPanel internal `countChars()` function strips Markdown markup before counting characters
- **Tone/formality control** (P2-9): WritingForm submit row adds segmented control (Casual | Standard | Formal), non-"Standard" tone auto-appends `[Writing tone requirement: casual/formal]` to content
- **Streamlined action bar** (P2-10): ResultPanel action bar refactored — Copy + Try Another buttons always visible; Edit + all export formats moved to `⋯` overflow menu (`showOverflow` state + `.overflow-menu`); PPT export stays inline

### Improved

- ResultPanel empty state illustration and copy updated: icon + "Start Creating" + "Choose a method to get started quickly"
- Copy button text simplified from "Copy Result" to "Copy"
- WritingForm advanced options (style, language, template, attachment) collapsed into expandable area, submit row cleaner
- Frontend test coverage increased from 54 to 66 test cases, 12 new tests covering quick-start, tone control, word count target, overflow menu

## [1.4.0] - 2026-03-26

### Added

- **CSS design token system**: `index.css` defines 122 CSS custom properties covering semantic colors, shadows, spacing, border-radius, transitions, and z-index
  - Semantic color variables: `--color-ppt`, `--color-error`, `--color-success`, `--color-warning`, `--color-info` with bg/border/ring variants
  - Shadow levels: `--shadow-sm` / `--shadow-md` / `--shadow-lg` / `--shadow-xl`
  - Spacing scale: `--sp-1` through `--sp-8`
  - Border-radius scale: `--radius-sm` through `--radius-full`
  - Transition presets: `--transition-fast` / `--transition-normal` / `--transition-slow`
  - z-index levels: `--z-dropdown` / `--z-modal` / `--z-toast`
- **Auto dark mode adaptation**: `prefers-color-scheme: dark` media query + `data-theme="dark"` manual toggle, all semantic variables auto-flip
- **Global shared animations**: 4 `@keyframes` (`fadeIn`, `slideUp`, `pulse`, `blink`) defined centrally in `index.css`
- **Global focus-visible style**: Unified accessible focus ring for all interactive elements
- **prefers-reduced-motion support**: Reduced-motion media query disables non-essential animations for motion-sensitive users

### Improved

- **10 component CSS files** comprehensively replaced hardcoded colors with CSS variables (922 line changes), ensuring theme consistency
  - `App.css`, `WritingForm.css`, `ResultPanel.css`, `HistoryPanel.css`, `AuthPanel.css`, `QualityPanel.css`, `LongFormPanel.css`, `ConfirmDialog.css`, `StyleEditor.css`, `SettingsPanel.css`
- **Eliminated 8 duplicate `@keyframes`** definitions, all components share global animations
- **10 TSX components** added WAI-ARIA accessibility attributes:
  - Dialogs: `role="dialog"` / `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby` (ConfirmDialog, SettingsPanel, AuthPanel, StyleEditor)
  - Error messages: `role="alert"` (auth errors, upload errors, offline banner, quality score errors, result errors, style edit errors)
  - Live regions: `aria-live="polite"` (ResultPanel content, LongFormPanel results, App status indicator)
  - Tab navigation: `role="tablist"` / `role="tab"` / `aria-selected` (App.tsx writing mode tabs)
  - Expandable areas: `aria-expanded` (App.tsx sidebar, QualityPanel collapsible panels)
  - Icon button labels: 18+ `aria-label` attributes (theme toggle, settings, sidebar, close, delete, search clear, etc.)
- `QualityPanel.tsx` score color function switched to CSS variables (`var(--color-success)` / `var(--color-warning)` / `var(--color-error)`)

## [1.3.1] - 2026-03-23

### Improved

- Unified version numbers to 1.3.1, marking the PPT generation feature as a stable release
- Synchronized FastAPI backend version number

## [1.3.0] - 2026-03-23

### Added

- PPT multi-layout system: 6 slide layout types (bullets, stats, comparison, timeline, quote, grid)
- AI Prompt auto-annotation: LLM embeds `[layout: xxx]` markers in slide titles based on content type
- `stats` layout: Rounded cards with large numbers + labels, displayed in multi-column arrangement
- `comparison` layout: Two-column comparison with column headers and center divider
- `timeline` layout: Horizontal timeline with node circles and above/below annotations
- `quote` layout: Large quotation mark decoration + centered quote text + attribution
- `grid` layout: Adaptive 2-3 column card grid with top accent line
- 12 new test cases covering all layouts and edge cases

### Improved

- Page count constraint elevated to highest priority, strictly following user-specified page count
- Layout diversity requirements adapted to page count (>=8 pages: at least 3 layouts, <8: at least 2, <=3: no requirement)
- Table of contents/summary page threshold raised from 6 to 8 pages to avoid wasting pages in short presentations
- Backward compatible: slides without layout markers automatically default to bullets layout

## [1.2.0] - 2026-03-22

### Added

- PPT export feature: export AI-generated PPT outlines to `.pptx` files
- 4 PPT theme templates: Business Blue (business), Minimal Gray (minimal), Fresh Green (green), Warm Tones (warm)
- Optional Unsplash image integration: automatically fetch relevant images for PPT slides
- Backend endpoint `POST /api/writing/export-pptx` (based on python-pptx)
- Frontend PPT export options: theme selector, image toggle
- Settings panel: new Unsplash Access Key input field
- PPT export unit tests and integration tests (22 new test cases)

## [1.1.0] - 2026-03-22

### Added

- Result editing: modify AI-generated content before export (edit/save/cancel)
- "Try Another" button: regenerate different results with the same parameters
- Input character counter: real-time character count displayed below text input area
- Multi-format export: added plain text (.txt), Markdown (.md), PDF (.pdf) export
- PDF export backend endpoint `POST /api/writing/export-pdf` (based on fpdf2, with Chinese support)
- Confirmation dialog (ConfirmDialog component) for clearing history
- "Retry" button displayed after request failures
- Dark mode toggle (three-state cycle: Follow System / Light / Dark), with persistent settings
- Polish/translate comparison view: side-by-side comparison of original and generated text
- Model/parameter settings panel (SettingsPanel): custom model name and temperature parameter
- Prompt template management: save/load/delete reusable writing instruction templates
- Keyboard shortcuts: Ctrl+Enter to submit, Esc to stop generation, Ctrl+S intercept
- Copy success/failure feedback: button text temporarily changes to "Copied"/"Copy Failed"
- History records migrated to backend SQLite database (SQLAlchemy + aiosqlite)
- History CRUD API: `GET/POST/DELETE /api/history`
- Backend structured logging system (request method/path/status code/duration)
- Request logging middleware (RequestLoggingMiddleware)
- IP rate limiting middleware (RateLimitMiddleware): AI generation endpoints limited to 10 requests per IP per minute
- Mobile sidebar collapse/expand (hamburger menu button for screens below 768px)
- Ollama offline degradation prompt: disable submit button and display guidance when service is offline

## [1.0.0] - 2026-03-21

### Added

- Article generation with multiple styles: Literary, Shanghai Gaokao Essay, Xiaohongshu Viral, WeChat Official Account, Toutiao Headlines, AI Drama Script, PPT Generation
- Classical Chinese poetry creation (5-char/7-char quatrains, regulated verse) with character count validation and auto-retry
- Text polishing feature
- Text translation supporting 6 languages: English, Chinese, Japanese, Korean, French, German
- Text summarization feature
- Streaming output (SSE) for real-time content display
- File upload supporting PDF, Word, TXT, Markdown, CSV, JSON, XML, HTML formats (max 10MB)
- Export results to Word document (.docx) with system "Save As" dialog for choosing save location
- History management (localStorage-based) with keyword search and chronological sorting
- Copy results to clipboard
- Download success/failure notification messages
- Backend health check endpoint
- CORS cross-origin support

### Fixed

- Fixed file upload network error: removed manually set Content-Type header, allowing axios to auto-generate multipart header with boundary
- Fixed empty Word export content: Chinese filename in Content-Disposition header was not URL-encoded, causing latin-1 encoding failure and 500 error
- Fixed showSaveFilePicker dialog not appearing: moved dialog invocation before await to ensure execution within user gesture context

[1.5.0]: https://github.com/USERNAME/REPO/releases/tag/v1.5.0
[1.4.0]: https://github.com/USERNAME/REPO/releases/tag/v1.4.0
[1.3.1]: https://github.com/USERNAME/REPO/releases/tag/v1.3.1
[1.3.0]: https://github.com/USERNAME/REPO/releases/tag/v1.3.0
[1.2.0]: https://github.com/USERNAME/REPO/releases/tag/v1.2.0
[1.1.0]: https://github.com/USERNAME/REPO/releases/tag/v1.1.0
[1.0.0]: https://github.com/USERNAME/REPO/releases/tag/v1.0.0
