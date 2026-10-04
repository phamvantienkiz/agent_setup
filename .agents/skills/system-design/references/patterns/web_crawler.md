# Distributed Web Crawler Architecture Pattern

Web Crawler

### Requirements
- Crawl billions of web pages
- Respect robots.txt and rate limits
- Handle duplicates, broken links, and dynamic content

### Key Components
- **URL frontier:** Priority queue of URLs to crawl (BFS order)
- **Fetcher:** Downloads page content (HTTP client with timeout and retry)
- **DNS resolver:** Cached DNS lookups to avoid repeated resolution
- **Content parser:** Extracts links, text, and metadata from HTML
- **Deduplication:** Content hash (MD5/SHA) to detect duplicate pages
- **URL filter:** Removes unwanted URLs (file types, domains, robots.txt exclusions)
- **Storage:** Blob store for raw content, database for metadata and links

### Design Decisions
- **Politeness:** One connection per domain at a time; respect `Crawl-delay` in robots.txt
- **Priority:** Rank URLs by PageRank, freshness, or domain importance
- **Deduplication:** URL dedup (seen this URL?) + content dedup (seen this content at another URL?)
- **Trap avoidance:** Detect infinite loops (calendar pages, query parameter variations), set max URL depth
- **Recrawl:** Schedule recrawl based on page change frequency (detect via Last-Modified, ETag)

---


