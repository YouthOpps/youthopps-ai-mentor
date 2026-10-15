# YouthOpp AI Mentor - Research and Technical Plan

Status: Research findings retained; the first mock-data prototype was implemented
with user approval. The project content and API messages are now in English.
Research date: October 15, 2026.
Target source: https://www.youthopps.org/

## 1. Research findings and access

Access was tested again after the user changed the network permissions. Both
https://youthopps.org/ and https://www.youthopps.org/ returned HTTP 200 for the
homepage. Subpages were inspected successfully through the www host. Subpage
requests to the bare domain returned HTTP 403; the reason for the difference was
not established. This does not mean the site is generally unavailable. HTML
canonical links refer to the bare domain.

The earlier proxy restriction no longer blocked this research. The homepage,
category and detail HTML, architecture documentation, source policy, robots.txt,
sitemap, client JavaScript, and a static JSON index were read. No visual or
interactive browser test was performed; listing behavior was investigated through
HTML, JavaScript, and published documentation.

The site calls itself "YouthOpp / Open opportunity index." Youth Opportunities
(youthop.com) is only one source in that index, not the same site as youthopps.org.
Direct institutional sources and other aggregators are also included. Listings
are independent discovery records that refer users to publishers for applications
and authoritative eligibility information.

## 2. How opportunities are listed

The homepage displayed **7,663 listings** at the time of research. This is a
changing inventory count, not the number of opportunities accepting applications.

- Categories: scholarships, internships, fellowships, volunteering, training,
  jobs, competitions, and grants. Filters also include other.
- Table fields: opportunity title/type, source institution and website,
  destination, and deadline. Titles link to /opportunity/<id>/; institutions
  link to /sources/publisher/<source-id>/.
- /opportunities/ and category pages contain 30 records per page. The internship
  archive exposed 33 pages. Static pagination uses /page/2/; JavaScript also
  stores search state in URL query parameters.
- Filters: q (text), country (publisher country), destination, category, source,
  and eligible (applicant country). Publisher country must not be confused with
  the applicant's citizenship or the opportunity's destination.
- Documented ordering: unexpired dated records by nearest deadline, unknown
  deadlines, then expired records; record ID breaks equal-deadline ties.
  Filters apply to the full collection before pagination. Static browsing works
  without JavaScript; search and live expiry checks require JavaScript.
- Detail fields: title, type, optional short summary, Destination, Who may apply,
  Deadline, Published, Last checked, Publisher, attribution, and an external
  "Read the original & apply" link. This link sometimes leads to another
  aggregator rather than directly to the organizer's application.

Inspected examples, all HTTP 200 through www:

| Type | Opportunity / detail link | Observation |
| --- | --- | --- |
| Scholarship | [DAAD EPOS 2027](https://www.youthopps.org/opportunity/youth-opportunities-59140/) | Eligible countries appear in the summary; structured eligibility and destination are missing; links to youthop.com |
| Scholarship | [Fulbright - Indiana University](https://www.youthopps.org/opportunity/0e4a05e909f2d1e9c849375e/) | Second scholarship detail example; title retains its source language |
| Fellowship | [UMAPS 2027-2028](https://www.youthopps.org/opportunity/youth-opportunities-59479/) | Country and nomination conditions appear in the summary; structured applicant eligibility is unknown |
| Fellowship | [African Climate Collaborative](https://www.youthopps.org/opportunity/youth-opportunities-59546/) | Second fellowship detail example |
| Internship | [WBI CIRC SEE](https://www.youthopps.org/opportunity/c4ecbf2fc9104fe59f63eb2e/) | France; summary mentions EUR 1,400/month, up to EUR 500 travel support, student requirements, and deadline 2026-11-13 |
| Internship | [Remote journalist/content creator](https://www.youthopps.org/opportunity/youth-for-europe-97980/) | Title states unpaid/remote; destination and eligibility unknown; deadline 2026-12-02 |

Parsing detail: raw HTML can contain an `Expired` label with a `hidden`
attribute. Finding that word in plain extracted text does not establish expiry.
Use the deadline and visibility logic. Site documentation uses the end of the
UTC day for date-only deadlines; the original publisher's actual time zone still
needs verification.

## 3. API, RSS, JSON, and permissions

### Verified technical access paths

| Path | Result | Interpretation |
| --- | --- | --- |
| [robots.txt](https://www.youthopps.org/robots.txt) | 200; User-agent: *, Allow: /; sitemap link | No general crawling prohibition; not a reuse license |
| [sitemap.xml](https://www.youthopps.org/sitemap.xml) | 200; page and source-specific sub-sitemaps | Useful for discovering URLs |
| https://www.youthopps.org/feed/ | 404 | This candidate RSS address is absent; other feed paths were not ruled out |
| https://www.youthopps.org/wp-json/ | 404 | This WordPress API candidate is absent; other APIs were not ruled out |
| /assets/collection.966583482b8b7416.json | 200; 966 internship records | Actual search index discovered from the category HTML data-index attribute |
| GitHub data-source JSON | 200; 417 records in the sampled source | Structured snapshot linked by the site's architecture documentation |

No documented general query API or RSS/Atom discovery link was found in the
inspected homepage, documentation, architecture, source policy, or category pages.
This does not prove that no official API exists. The observed architecture uses
static pages and collection indexes; a live application API contract was not found.

Static internship index fields: id, deadline (numeric timestamp), html, search,
category, source, country, destination, eligible. Filtering occurs client-side;
the q URL parameter should not be mistaken for a server API. Index filenames
contain a content hash and should be discovered from HTML rather than hardcoded.
Treat HTML fragments as untrusted content, never as instructions or automatically
safe markup for rendering.

### Preferred candidate: data-source snapshots

The [architecture guide](https://www.youthopps.org/docs/architecture/) describes:
publisher -> data-pipeline -> data-source -> static website.
The [data repository](https://github.com/YouthOpps/data-source) publishes
`datas/<source-id>/data.json` and `metadata.json` for each source.

Directly inspected examples:

- https://raw.githubusercontent.com/YouthOpps/data-source/main/README.md
- https://raw.githubusercontent.com/YouthOpps/data-source/main/datas/youth-opportunities/data.json
- https://raw.githubusercontent.com/YouthOpps/data-source/main/datas/youth-opportunities/metadata.json

Example metadata: status=success, record_count=417,
last_success_at=2026-10-14T22:15:44.203Z, publisher_country=BD,
publisher_type=aggregator. Collection success does not prove applications remain
open. A later failed collection preserves the last successful records.

Observed record fields: id, title, url, source, source_url, published_at,
summary, tags, location, deadline, language, category/categories, kind,
host_countries, eligible_countries, publisher_country, created_at, updated_at,
first_seen_at, last_seen_at, last_checked_at, status, classification.
An empty eligible_countries array in this upstream source does not establish
worldwide eligibility: some sampled country requirements exist only in summary
text. A future adapter must preserve this distinction from the explicit
unrestricted-country convention used in our fictional fixtures.

The README states that no root catalog.json or aggregate manifest is published.
Supported source discovery needs clarification; explicitly selected source IDs
could serve an MVP. The site guide describes the new layout while the repository
README also contains an old-catalog migration note. Because of this documentation
difference, pin the consumed commit SHA and test against the actual schema. Do
not assume the deployed website and the data repository's main branch use the
same snapshot.

### Reuse limitations

The [trust policy](https://www.youthopps.org/docs/trust/) explicitly states that
public GitHub access is not a reuse license and that the guide grants no license.
The attempted data-source/main/LICENSE path returned 404; this is not exhaustive
proof that no differently named license exists. Applicable data licensing or
third-party consumption terms remain unverified. Technical JSON access was
confirmed, but redistribution permission was not. Copying full articles,
branding, or images is not recommended.

The [bot guide](https://www.youthopps.org/bot/) describes its own collectors'
policy: review robots/terms, space requests at least six seconds apart, start at
most ten requests in any rolling minute, honor Retry-After, and stop on access
refusal. This is not an automatic third-party license or API agreement. At least
these conservative limits, and any stricter source terms, are proposed for a
possible HTML adapter. Research used limited read requests; no bulk crawl or
access-control bypass was performed.

**Decision:** Clarify snapshot reuse/licensing through the owner's documentation
or explanation first. If permitted, consume source-specific JSON rather than
crawling thousands of detail pages. Otherwise evaluate permitted static-index or
HTML access. Do not base implementation on unverified RSS or WordPress endpoints.
No message was sent to the site operator during this research.

## 4. Proposed Python architecture

The original production-oriented proposal is one Python project:

Permitted JSON snapshot adapter -> normalization/validation -> SQLite -> matching
service -> FastAPI -> GPT Actions or another client.

The implemented mock prototype uses Python 3.11+, FastAPI, and Pydantic, with
local JSON instead of SQLite. Persistence is unnecessary for its current scope.
SQLAlchemy/Alembic and a database remain future options, not installed features.

- **Tools:** a virtual environment and pinned dependencies. Prefer JSON access;
  add feedparser only if an RSS source is verified, and an HTML parser only if
  necessary. Check supported tool versions before implementation changes.
- **Collection:** a permitted-source adapter with source ID, cursor/page state,
  last successful synchronization, and error reporting. Begin with a command-line
  task and add scheduling if needed; a distributed queue is unnecessary initially.
- **Storage:** SQLite and migrations if persistence becomes necessary;
  PostgreSQL if deployment needs concurrent writers. Enforce source ID or
  normalized source URL uniqueness and idempotent refreshes.
- **Service:** search, details, and profile recommendations. A user search must
  not trigger a fresh crawl of the whole source site.
- **Observability:** last update, record counts, collection failures, source
  status, and latency. Do not log credentials or personal profiles.

### Proposed opportunity model for real data

id, source, source_id, source_url, publisher_record_url, application_url,
title, organization, publisher_country, publisher_type, host_countries,
source_revision, opportunity_type, summary, subjects, location, remote, funding,
eligible_countries, residency_rules, education_levels, age_min/age_max,
language_requirements, deadline_at, deadline_precision, deadline_timezone,
rolling_deadline, published_at, fetched_at, last_verified_at, status.

Initially map upstream `url` to publisher_record_url. Do not call it an
application_url until its role is confirmed. Store metadata status and last
successful collection separately. Missing values remain null/unknown. Normalize
countries and fields while retaining textual evidence and provenance. Do not
invent a time zone for ambiguous deadlines. Exclude expired opportunities from
default recommendations, mark unknown dates, and track disappeared records
rather than immediately deleting them.

### Profile and matching

The planned profile includes education, field/interests, citizenship and separate
residence where needed, preferred destinations/types, and optional funding or
remote preferences. Request age where needed for eligibility; passport, full
birth date, and CV are unnecessary for the first version. Profiles are used
within a request without default persistence.

First exclude explicit deadline, citizenship, age, and education violations.
Missing rules or profile fields establish neither eligibility nor ineligibility;
return a review warning. Then score preferences with understandable reasons.
Results should carry matching reasons, unverified conditions, freshness, and
source links. A score is not an acceptance probability. The prototype's exact
implemented filters and weights are documented in README.md.

An LLM is optional. Future English summaries and natural-language search must
not invent requirements or deadlines. External page text is data, not an
instruction source; maintain the trust boundary against prompt injection.
Embeddings and a vector database are unnecessary for the initial scope.

## 5. ChatGPT integration

The legacy ChatGPT Plugins beta was retired; a new project should not depend on
its plugin manifest. That platform information was not verified against live
OpenAI documentation during this research. Confirm current account support,
publication requirements, and integration options before implementation.
The proposed starting point is **GPT Actions** calling FastAPI from a custom GPT.
ChatGPT Apps SDK/MCP is a separate integration option, not the Actions protocol,
and is not required for the first version.

Planned Actions components:

- A publicly reachable HTTPS API with a valid TLS certificate.
- A FastAPI-generated schema checked against the platform's supported OpenAPI
  features, with stable operation IDs, descriptions, and examples.
- Originally proposed future routes: GET /opportunities for filtered discovery,
  GET /opportunities/{id} for details, and POST /recommendations for explained
  profile matches. These are not implemented routes in the prototype.
- Implemented prototype routes: POST /opportunities/search and GET /health.
  See README.md and openapi.json for the actual current contract.
- Source/application URLs, update times, and eligibility uncertainty in results;
  bounded response sizes and understandable errors.
- A quota-protected API key for a non-personal pilot, or user OAuth for persistent
  accounts. Manage credentials in server secret storage and Actions settings,
  never in the schema or repository.
- GPT instructions: ask only for missing necessary profile fields, cite API
  sources, avoid eligibility/success guarantees, and do not submit applications.
- A privacy policy, support contact, and any current domain/publication checks
  required for public distribution.

Historical Plugins compatibility, if separately requested, could involve
/.well-known/ai-plugin.json, OpenAPI, authentication, a logo, and legal contact
fields. These are legacy components, not a promise of present-day installability.

Official verification targets, whose content was not read during research:

- https://help.openai.com/en/articles/8988022-winding-down-the-chatgpt-plugins-beta
- https://platform.openai.com/docs/actions

## 6. Implementation phases and acceptance criteria

1. **Verify the source:** network access, site identity, category examples,
   access documentation, and reuse permission. Record evidence before building
   a live-data collector.
2. **Data layer:** validate the schema and permitted adapter. Test categories,
   missing dates, time zones, duplicate records, and page/schema changes.
3. **Matching:** synthetic profiles must demonstrate explicit exclusions,
   uncertainty warnings, and consistent score explanations.
4. **API:** test search/details/recommendations as implemented, validation,
   pagination, quotas, and authentication when added. Check displayed sources.
5. **Actions pilot:** verify an actual HTTPS profile -> recommendation -> detail
   flow in ChatGPT, including schema support, errors, and timeouts.

Further checks: repeated collection must not duplicate records; expired records
must not appear as active recommendations; stale cache age must be visible;
403/429 handling must be tested; logs must exclude profiles and secrets.
Distributed services, payments, CV uploads, automatic applications, and
notification infrastructure are outside the initial scope.

## 7. Decisions and next steps

- Access through www was confirmed; the earlier general proxy restriction was
  resolved for the research requests.
- If reuse terms permit: prefer source-specific JSON snapshots, optional SQLite,
  rule-based matching, FastAPI, and GPT Actions. HTML scraping/RSS is not the
  first choice.
- Keep publisher country, destination, and applicant citizenship/residence
  separate. Do not assert eligibility when structured fields are missing or
  disagree with textual conditions; retain evidence and review warnings.
- Read data and metadata from a consistent commit/revision. On schema failure,
  preserve the last valid local snapshot and disclose its age.
- Open questions: licensing/reuse terms, supported source discovery, refresh
  contract, and sample deadline/eligibility verification with original publishers.
  Publisher sites were not independently crawled during this research.
- OpenAI platform documentation was not reverified during the follow-up site
  research; the integration proposal remains conditional.

The user approved a working prototype after this research. It uses fictional
local JSON only; no live data source was integrated. README.md documents the
implemented behavior, installation, startup, and validation commands.
