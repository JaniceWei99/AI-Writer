# Changelog

This file documents all notable changes to this project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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

[1.3.1]: https://github.com/USERNAME/REPO/releases/tag/v1.3.1
[1.3.0]: https://github.com/USERNAME/REPO/releases/tag/v1.3.0
[1.2.0]: https://github.com/USERNAME/REPO/releases/tag/v1.2.0
[1.1.0]: https://github.com/USERNAME/REPO/releases/tag/v1.1.0
[1.0.0]: https://github.com/USERNAME/REPO/releases/tag/v1.0.0
