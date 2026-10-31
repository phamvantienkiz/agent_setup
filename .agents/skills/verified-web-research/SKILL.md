---
name: verified-web-research
description: Mandatory workflow for any question that needs factual information - parse the user's intent, analyze, reason, search the web for the latest information, evaluate source credibility, cross-check, cite sources, and explicitly mark "Unverified information" when something cannot be confirmed. Use this skill for EVERY question about events, people, organizations, products, software versions, prices, figures, laws, news, technology, health, finance, or anything that may have changed, even when the question looks simple and you feel certain you already know the answer. Never answer from the model's memory in place of searching.
---

# Verified Web Research

This skill forces the Agent to **search first, answer second**, and every piece of information it gives must either carry a source or be labeled unverified.

## Core principles

1. **Web search is the default; memory is the last resort.** Knowledge inside the model can be outdated or wrong, even for things that seem simple (who currently holds a position, the latest version, the current price, recent events). Do not answer these kinds of questions from memory.
2. **No source, no claim.** Every factual statement must be tied to a source that was actually read in this turn.
3. **Honesty over completeness.** Saying "could not be verified" is better than guessing to produce an answer.
4. **Prefer the latest information.** Use the current date (from the system context) when a time bound is needed; never put an old year in a query.

## The 5-step workflow

### Step 1. Intent parsing

Before searching, analyze the question (briefly, internally, or visibly if the question is complex):

- **What is the person really asking?** What they need to know, as opposed to how they phrased it.
- **Key entities:** people, organizations, products, places, concepts, points in time.
- **Type of information:** event / figure / definition / comparison / how-to / prediction / opinion.
- **Time sensitivity:** could this information have changed? Does the person need "current", "latest", or a historical point in time?
- **Hidden sub-questions:** which smaller questions must be answered to answer the big one? (e.g., "compare A and B" needs information on A, information on B, and only then the comparison.)
- **Ambiguity:** if the question is ambiguous, pick the most reasonable interpretation, state the assumption, and still search. Ask for clarification only when the different interpretations lead to completely different results.

### Step 2. Analysis and search planning

- List what needs to be verified and split it into separate queries, one per entity or sub-question. Do not cram several things into one query.
- Decide the **ideal source type** for each part: the organization's official site, government agencies, academic papers, authoritative technical documentation, reputable news outlets.
- Scale the search effort to the complexity:

| Question type                                    | Suggested number of searches |
| ------------------------------------------------ | ---------------------------- |
| A single simple fact                             | 1-2                          |
| Medium, multi-part question                      | 3-6                          |
| Deep research, comparisons, controversial topics | 6-15                         |

### Step 3. Searching (always web search first)

- Use the available web search tool **first**. If a page-reading tool (fetch/browse) is available, use it to read the full page instead of relying on short snippets.
- Keep queries short and specific (about 2-6 words), start broad, then narrow. Each new query must differ from the previous one; if results are poor, change the keywords, change the angle, and search in both English and the user's language when appropriate.
- For news or fast-changing information: add "today", the current month/year, or "latest" to the query.
- For personal or internal data (documents, email, calendar), use the matching internal tool first, then use the web for the external part.
- If the person provides a URL: read that URL first.
- **Use memory only** for: stable background knowledge (mathematical definitions, basic scientific principles, historical events that are settled). Even then, if the question contains any "currently / latest / still active" element, search anyway.
- If no web search tool is available in this session: say so plainly, then answer from existing knowledge and label it **"Unverified information (no web search available; based on model knowledge, may be outdated)"**.

### Step 4. Verifying information

For every important piece of information, check four things:

**a) Origin:** Who published it? Is it a primary source or a retelling of another source? Trace back to the original whenever possible.

**b) Source credibility.** Rate it on this scale:

| Level  | Source type                                                                                                                 | Examples                                                                                                                                                           |
| ------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| High   | Official sources, original documents                                                                                        | Official websites of organizations/companies, government portals (.gov, .gov.vn), official technical documentation, peer-reviewed publications, standard databases |
| Fair   | Mainstream press with an editorial team and a corrections process                                                           | Reuters, AP, BBC, VnExpress, Tuoi Tre, Thanh Nien, reputable trade journals                                                                                        |
| Medium | Aggregators, open encyclopedias, expert blogs with a clearly named author                                                   | Wikipedia (use for orientation, then cross-check against original sources), technical blogs by recognized experts                                                  |
| Low    | Forums, social media, SEO/affiliate sites, content without an author, auto-generated aggregator pages, AI-generated content | Reddit, Facebook, Quora, mass-produced "top 10" sites                                                                                                              |

Warning signs: no author or publish date, sensational headline, no cited sources, a sales motive, outdated content, a site impersonating an official domain.

**c) Freshness:** What is the publish or update date? Is it still correct as of today? When information conflicts, prefer the source that is both newer and more credible, and state the time reference explicitly.

**d) Cross-checking:**

- Important information (figures, dates, names, decisions, health/financial/legal recommendations) needs **at least 2 independent sources**, or 1 official source at the High level.
- Two articles that copy from the same origin do not count as two independent sources.
- When sources conflict: present both sides, say exactly where they conflict, which source is more trustworthy and why. Do not silently pick one and hide the other.
- For topics prone to manipulation or controversy (politics, conspiracy theories, pseudoscience, heavily SEO'd product categories): raise the level of skepticism and look for opposing sources.

**Verification result - assign one of three statuses:**

- ✅ **Verified:** backed by a High/Fair source, or at least 2 independent sources that agree.
- ⚠️ **Partially verified:** only one Medium-level source, or sources that do not fully agree, or the information may be outdated.
- ❌ **Unverified:** no trustworthy source found, only Low-level sources, or sources that conflict and cannot be resolved.

### Step 5. Reasoning and answering

- Reason only from the information that was gathered. Clearly separate **sourced facts** from **your own inference/assessment**. Inference must be labeled as inference.
- Do not add details "for completeness" without a source.
- If no answer can be found: say plainly that it was not found, state what was searched, and suggest where to look next. Do not make things up.

## Citation rules

- **Every specific piece of information** (figure, date, name, claim, event) must have a source right after the sentence.
- Source format: `[Source name, publish date if available](URL)`. If the interface has its own citation mechanism, use that.
- Rephrase in your own words; do not copy long passages verbatim. If a direct quote is necessary, keep it short (under 15 words), put it in quotation marks, and use at most one quote per source. Never reproduce song lyrics, poems, or long passages of articles.
- Cite only sources that you **actually read** in this turn. Never invent URLs, never invent article titles, never attribute information to a source you have not read.
- Official/original sources are preferred over aggregator pages.

## Rules for the "unverified" label

When a piece of information is ❌ (or ⚠️ with a caveat), **add this line at the end of that information**:

> **Unverified information.**

A short reason may follow, for example: _"(only source is a forum post; no official source confirming it was found)"_ or _"(sources give different figures)"_.

Do not use this label to dodge searching. Use it only after genuinely searching and failing to confirm.

## Answer format template

Adjust the length to the question. For simple questions, answer briefly and go straight to the result; not every section is required.

```
**Short answer:** [1-2 sentence conclusion, with verification status]

**Details:**
- [Fact 1] ([Source A, date](URL)).
- [Fact 2] ([Source B, date](URL)), ([Source C](URL)).
- [Fact 3 that could not be confirmed]. **Unverified information.**

**Confidence level:** ✅ Verified / ⚠️ Partial / ❌ Unverified
- Sources used: [list with a quick credibility rating]
- Conflicts/limitations (if any): ...

**My assessment (inference):** [if needed; clearly marked as inference]
```

For very simple questions, a compact form is fine:

```
Currently [fact] ([Source, date](URL)).
```

## What not to do

- Do not answer from memory for information that may have changed and then pretend a search was done.
- Do not say "as far as I know" in place of searching when a search tool is available.
- Do not cite sources that were not read, and do not fabricate URLs.
- Do not treat the first search result as truth by default.
- Do not hide conflicts between sources.
- Do not give definitive medical, financial, or legal advice; provide only verified information with sources and state that you are not a professional.
- Do not stop after a single search if the results are not enough for a complete answer.

## Pre-send checklist

- [ ] Did I parse the intent and sub-questions correctly?
- [ ] Does every factual claim come from a web search in this turn (not from memory)?
- [ ] Did I assess the credibility and freshness of each source?
- [ ] Was important information cross-checked?
- [ ] Does every specific claim have a real citation?
- [ ] Is anything I could not confirm labeled "Unverified information"?
- [ ] Is inference kept separate from facts?
