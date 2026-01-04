<p align="center">
  <img src="images/image.png" alt="Webustler Logo" width="300" height="300">
</p>

<h1 align="center">Webustler</h1>

<p align="center">
  <strong>MCP server for web scraping that actually works.</strong><br>
  Extracts clean, LLM-ready markdown from any URL — even Cloudflare-protected sites.
</p>

<p align="center">
  <a href="#features"><img src="https://img.shields.io/badge/Features-13+-blue?style=for-the-badge" alt="Features"></a>
  <a href="#installation"><img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="#installation"><img src="https://img.shields.io/badge/MCP_Toolkit-Coming_Soon-orange?style=for-the-badge&logo=docker&logoColor=white" alt="MCP Toolkit Coming Soon"></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-Server-purple?style=for-the-badge" alt="MCP Server"></a>
</p>

<p align="center">
  <a href="#why-webustler">Why Webustler?</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#output-format">Output</a>
</p>

---

<a id="why-webustler"></a>

## 🤔 Why Webustler?

Most scraping tools fail on protected sites. **Webustler doesn't.**

<table>
<tr>
<td>

### ❌ Other Tools
- Block on Cloudflare
- Require API keys
- Charge per request
- Return messy HTML
- No retry logic

</td>
<td>

### ✅ Webustler
- Bypasses protection automatically
- 100% free & self-hosted
- Unlimited requests
- Clean, LLM-ready markdown
- Smart retry with fallback

</td>
</tr>
</table>

---

## 📊 Comparison

| Feature | Webustler | Firecrawl | ScrapeGraphAI | Crawl4AI | Deepcrawl |
|:--------|:---------:|:---------:|:-------------:|:--------:|:---------:|
| Anti-bot bypass | ✅ | ⚠️ | ❌ | ⚠️ | ❌ |
| Cloudflare support | ✅ | ⚠️ | ❌ | ⚠️ | ❌ |
| No API key needed | ✅ | ❌ | ❌ | ✅ | ⚠️ |
| Self-hosted | ✅ | ✅ | ✅ | ✅ | ✅ |
| MCP native | ✅ | ✅ | ✅ | ✅ | ❌ |
| Token optimized | ✅ | ✅ | ❌ | ✅ | ✅ |
| Rich metadata | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| Link categorization | ✅ | ❌ | ❌ | ❌ | ✅ |
| File detection | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Reading time | ✅ | ❌ | ❌ | ❌ | ❌ |
| Zero config | ✅ | ❌ | ❌ | ❌ | ❌ |
| Free forever | ✅ | ❌ | ❌ | ✅ | ✅ |

<p align="center"><sub>✅ Full support · ⚠️ Partial/Limited · ❌ Not supported</sub></p>

---

<a id="features"></a>

## ✨ Features

<table>
<tr>
<td width="50%">

### 🛡️ Smart Fallback System
Primary method fails? Automatically retries with anti-bot bypass. No manual intervention needed.

### 📋 Rich Metadata Extraction
- Title, description, author
- Open Graph & Twitter Cards
- Published/modified time
- Language, keywords, robots

### 🔗 Link Categorization
Separates internal links (same domain) from external links. Perfect for crawling workflows.

### 📁 File Download Detection
Detects PDFs, images, archives, and other file types. Returns structured info instead of garbled binary.

</td>
<td width="50%">

### 🧹 Token-Optimized Output
Removes ads, sidebars, popups, base64 images, cookie banners, and all the junk LLMs don't need.

### 📊 Table Preservation
Data tables stay intact in markdown. No more broken layouts.

### ⏱️ Content Analysis
Word count and reading time calculated automatically. Know your content at a glance.

</td>
</tr>
</table>

---

<a id="installation"></a>

## 📦 Installation

```bash
git clone https://github.com/drruin/webustler.git
cd webustler
docker build -t webustler .
```

---

## 🔧 MCP Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "webustler": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "webustler"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add webustler -- docker run -i --rm webustler
```

### Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "webustler": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "webustler"]
    }
  }
}
```

### Windsurf

Add to your Windsurf MCP config:

```json
{
  "mcpServers": {
    "webustler": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "webustler"]
    }
  }
}
```

### With Custom Timeout

Pass the `TIMEOUT` environment variable (in seconds):

```json
{
  "mcpServers": {
    "webustler": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "TIMEOUT=180", "webustler"]
    }
  }
}
```

---

<a id="usage"></a>

## 🚀 Usage

Once configured, the `scrape` tool is available to your MCP client:

```
Scrape https://example.com and summarize the content
```

```
Extract all links from https://news.ycombinator.com
```

```
Get the article from https://protected-site.com/article
```

Webustler handles everything automatically — including Cloudflare challenges.

---

<a id="output-format"></a>

## 📄 Output Format

Returns clean markdown with YAML frontmatter:

```markdown
---
sourceURL: https://example.com/article
statusCode: 200
title: Article Title
description: Meta description here
author: John Doe
language: en
wordCount: 1542
readingTime: 8 mins
publishedTime: 2025-01-01
openGraph:
  title: OG Title
  image: https://example.com/og.png
twitter:
  card: summary_large_image
internalLinksCount: 42
externalLinksCount: 15
imagesCount: 8
---

# Article Title

Clean markdown content here with **formatting** preserved...

| Column 1 | Column 2 |
|----------|----------|
| Tables   | Work too |

---
## Internal Links

- https://example.com/page1
- https://example.com/page2

---
## External Links

- https://other-site.com/reference

---
## Images

- https://example.com/image1.jpg
```

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    URL ──► Primary Fetch ──► Blocked? ──► Fallback Fetch       │
│                                  │              │               │
│                                  ▼              ▼               │
│                              Success ◄──────────┘               │
│                                  │                              │
│                                  ▼                              │
│                          Clean HTML                             │
│                                  │                              │
│                                  ▼                              │
│              ┌───────────────────┼───────────────────┐          │
│              ▼                   ▼                   ▼          │
│         Metadata            Markdown             Links          │
│              │                   │                   │          │
│              └───────────────────┼───────────────────┘          │
│                                  ▼                              │
│                          Format Output                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 Retry Logic

| Method | Attempts | Delay | Purpose |
|--------|:--------:|:-----:|---------|
| Primary | 2 | 5s | Fast extraction |
| Fallback | 3 | 5s | Anti-bot bypass |

**Total**: Up to 5 attempts before failure. Handles timeouts, rate limits, and challenges.

---

## 🧹 Content Cleaning

<details>
<summary><strong>Click to see what gets removed</strong></summary>

### Tags Removed
| Category | Elements |
|----------|----------|
| Scripts | `<script>`, `<noscript>` |
| Styles | `<style>` |
| Navigation | `<nav>`, `<header>`, `<footer>`, `<aside>` |
| Interactive | `<form>`, `<button>`, `<input>`, `<select>`, `<textarea>` |
| Media | `<svg>`, `<canvas>`, `<video>`, `<audio>`, `<iframe>`, `<object>`, `<embed>` |

### Selectors Removed
- Sidebars (`[class*='sidebar']`, `[id*='sidebar']`)
- Comments (`[class*='comment']`)
- Ads (`[class*='ad-']`, `[class*='advertisement']`)
- Social (`[class*='social']`, `[class*='share']`)
- Popups (`[class*='popup']`, `[class*='modal']`)
- Cookie banners (`[class*='cookie']`)
- Newsletters (`[class*='newsletter']`)
- Promos (`[class*='banner']`, `[class*='promo']`)

### Also Removed
- Base64 inline images (massive token savings)
- Empty elements
- Excessive newlines (max 3 consecutive)

</details>

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|:-------:|-------------|
| `TIMEOUT` | `120` | Request timeout in seconds |

---

## 🏆 Why Not Just Use...

<details>
<summary><strong>Firecrawl?</strong></summary>

Firecrawl is excellent but:
- Requires API key and paid plans for serious usage
- Limited anti-bot capabilities
- More complex setup with environment variables

</details>

<details>
<summary><strong>ScrapeGraphAI?</strong></summary>

ScrapeGraphAI uses LLMs to parse pages:
- Requires LLM API keys (OpenAI, etc.) for all operations
- Adds latency (LLM calls) and cost (token usage)
- Webustler is deterministic — faster, cheaper, predictable

</details>

<details>
<summary><strong>Crawl4AI?</strong></summary>

Crawl4AI is a powerful open-source crawler but:
- Requires more configuration to get started
- LLM features require additional API keys
- Webustler works out of the box with zero config

</details>

<details>
<summary><strong>Deepcrawl?</strong></summary>

Deepcrawl is a great Firecrawl alternative but:
- Hosted API requires API key (self-host is free)
- No anti-bot bypass capabilities
- REST API only, not an MCP server

</details>

---

## 📁 Project Structure

```
webustler/
├── server.py           # MCP server
├── Dockerfile          # Docker image
├── requirements.txt    # Dependencies
├── LICENSE             # MIT License
├── images/             # Assets
│   └── image.png
└── README.md           # Documentation
```

---

<a id="license"></a>

## 📜 License

MIT License — use it however you want.

---

<p align="center">
  <strong>MCP server for LLMs. Works everywhere. No API keys. No limits.</strong>
</p>

<p align="center">
  <sub>Made with care for the AI community</sub>
</p>
