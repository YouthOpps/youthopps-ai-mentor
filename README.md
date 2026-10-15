# YouthOpp AI Mentor

Developed by [Alperen](https://github.com/alperenyrmbs).

A Python 3.11+ and FastAPI prototype that helps students discover opportunities
and understand why they match their profile. It ranks scholarships, internships,
fellowships, and other opportunities with simple, explainable rules and returns
supportive mentor messages in English.

**This prototype uses eight fictional mock opportunities only. It does not fetch,
use, or redistribute real YouthOpps data.** Example source links point to
`example.org` and are not application links. Dates in 2099 keep the demo fixtures
usable; they are not real deadlines. Data reuse permissions remain unconfirmed.

## Features

- Profile validation: age, education, interests, optional citizenship and residence.
- Opportunity type, text search, and an optional Europe destination filter.
- Explicit eligibility checks and a score from 0 to 100 with matching reasons.
- Warnings when eligibility information or deadlines are unknown.
- Opportunity details, source links, and a mock-data notice in every search response.
- A replaceable repository interface for a future permitted JSON data source.
- Generated OpenAPI documentation and automated tests.

No API key, LLM service, database, or external data service is required. Profiles
are used in memory for each request and are not persisted. SQLite is unnecessary
for this prototype.

## Install and run

From the repository root, using Python 3.11 or newer:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.
For a cloud environment that needs access outside the container, use
`--host 0.0.0.0`. The prototype has no authentication or rate limiting.

Routes:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/opportunities/search` | Rank mock opportunities for a profile |
| GET | `/health` | Report process health and mock mode |
| GET | `/docs` | Interactive Swagger documentation |
| GET | `/openapi.json` | Generated OpenAPI schema |

## Example: a student looking for an internship in Europe

This example represents a 22-year-old computer engineering undergraduate living
in Turkey. Citizenship is deliberately omitted: residence does not establish it.

```bash
curl -sS -X POST http://127.0.0.1:8000/opportunities/search \
  -H 'Content-Type: application/json' \
  -d '{
    "profile": {
      "age": 22,
      "residence_country": "TR",
      "education": "undergraduate",
      "interests": ["computer engineering"],
      "opportunity_type": "internship",
      "preferred_region": "europe"
    },
    "limit": 10
  }'
```

Expected fixture results while their demo deadlines have not passed:

| Fictional opportunity | Destination | Score |
| --- | --- | --- |
| MOCK: Software Development Internship in Germany | Germany | 100 |
| MOCK: Web Development Internship in France | France | 100 |
| MOCK: Climate Research Internship | Netherlands | 60 |

The two technology internships match the student's interest, age, education, and
selected type. The climate internship is a broader alternative with no direct
interest match. The remote internship is excluded because its location does not
establish a European destination. The computer engineering alias maps to the
technology tag; it does not verify a degree requirement.

Each result contains `opportunity`, `score`, `reasons`, `eligibility_status`,
`warnings`, and `mentor_message`. Opportunity fields include title, description,
destination country, category, deadline, eligibility rules, and source URL.
The response also contains `notice`, `is_mock`, `evaluated_on`, and `total`.
`total` counts matches before applying `limit`; no matches returns HTTP 200 with
an empty list. Invalid input returns HTTP 422.

## Profile and search options

| Field | Accepted values / meaning |
| --- | --- |
| `age` | Required integer, 1–120 |
| `education` | `high_school`, `undergraduate`, `graduate`, `doctoral`, `other` |
| `interests` | Required list of 1–20 nonblank strings, at most 80 characters each |
| `country` | Optional two-letter citizenship code, such as `TR` |
| `residence_country` | Optional two-letter residence code; not used as citizenship |
| `opportunity_type` | `scholarship`, `internship`, `fellowship`, `other`; omit or use null for all |
| `preferred_region` | `europe`; omit or use null for no region filter |
| `query` | Optional top-level substring search over title, description, and interests |
| `limit` | Optional top-level integer, 1–50; default 10 |

Country codes are uppercased and checked for a two-letter format, not against a
complete ISO country list. Interest matching uses a small English alias
dictionary and exact tag overlap, rather than semantic search or an LLM.

The Europe filter uses the explicit destination list in
`app/matching.py`: AD AL AT BA BE BG BY CH CY CZ DE DK EE ES FI FR GB GR HR HU IE
IS IT LI LT LU LV MC MD ME MK MT NL NO PL PT RO RS SE SI SK SM UA VA XK.
It is a prototype selection policy, not an EU membership filter. Transcontinental
countries such as TR/RU, remote locations, and unknown destinations are excluded.

## Matching rules

Expired opportunities and explicit age, citizenship, or education mismatches are
excluded. Unknown citizenship does not cause exclusion, but a restricted country
condition cannot be confirmed and earns no country points. Dates are evaluated
by UTC calendar day, including today's deadline. Unknown deadlines generate a
warning. Region, type, and text criteria are filters.

| Matching component | Maximum points |
| --- | ---: |
| Proportion of profile interests matched | 40 |
| Selected opportunity type | 20 |
| Known and satisfied citizenship condition, including explicitly unrestricted | 15 |
| Known and satisfied education condition | 15 |
| Age within a fully specified minimum/maximum range | 10 |

No selected type means no type points. Region does not add points. Ties are
resolved by earliest known deadline and then record ID. Missing eligibility
information earns no points and produces `needs_review`.
`countries: []` explicitly means unrestricted; `null` means unknown.
`matches_stated_rules` refers only to the modeled fixture rules. Scores do not
represent acceptance probabilities and do not verify visa, work authorization,
language, or all potential application requirements.

## Project layout

```text
app/
  main.py                       FastAPI routes and dependency wiring
  models.py                     Pydantic request/response models
  matching.py                   Filtering, scoring, and mentor explanations
  repository.py                 Repository protocol and mock implementation
  data/mock_opportunities.json  Eight fictional records
tests/test_api.py              API and matching regression tests
openapi.json                    Exported API contract
requirements.txt                Pinned runtime and test dependencies
PLAN.md                         Research and technical plan in English
```

`OpportunityRepository` separates matching from data access. After reuse rights
are verified, a JSON adapter can implement this interface and replace
`get_repository`. It must handle provenance, consistent revisions, source status,
staleness, validation, and missing eligibility information. Mock-only notices and
API metadata must also be updated deliberately when adding a real source.
No live adapter is included. See [PLAN.md](PLAN.md) for the research findings.

## OpenAPI and ChatGPT integration

The checked-in `openapi.json` is generated from the same application contract as
`/openapi.json`. Regenerate it from the repository root after API changes:

```bash
.venv/bin/python -c 'import json; from pathlib import Path; from app.main import app; Path("openapi.json").write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n")'
```

The search operation has the stable operation ID `searchOpportunities` and
`x-openai-isConsequential: false` because it only searches. This is an integration
starting point, not a completed ChatGPT deployment. GPT Actions integration has
not been tested inside ChatGPT. It still needs a reachable HTTPS API, an actual
`servers` URL in the schema, platform compatibility checks, authentication,
quotas, and a privacy disclosure for profile transmission.

## Tests

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
```

The suite includes 21 cases covering validation, mock disclosure, scoring,
explicit exclusions, unknown conditions, date boundaries, search/limits, repository
replacement, OpenAPI, Europe filtering, and residence/citizenship separation.
Tests do not contact external sites. The current test client emits a dependency
deprecation warning about its HTTP transport; it does not fail the tests.

## Configuration and secrets

No secrets are needed for this demo. Keep future credentials in environment
variables or a secret manager. `.gitignore` excludes local `.env` files, virtual
environments, caches, common credential files, keys, databases, and build output.
Only placeholder examples should ever go into `.env.example`.
Ignore rules cannot detect arbitrary secrets embedded in source or remove secrets
already committed. Review staged changes before publishing; do not put credentials
in code, fixtures, logs, documentation, or the OpenAPI schema.

## Prepare for Render deployment

Deployment preparation is included in `render.yaml`; no Render service has been
created or deployed as part of this change. The blueprint uses the `main` branch,
Python **3.12.14** (also pinned in `.python-version`), and Render's assigned `PORT`.
Run all commands from the repository root; leave Render's Root Directory unset.

| Setting | Value |
| --- | --- |
| Runtime | Python |
| Branch | `main` |
| Build command | `python -m pip install -r requirements.txt && python -m pytest -q` |
| Start command | `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --no-access-log` |
| Health check | `/health` |
| Environment variable | `PYTHON_VERSION=3.12.14` |
| Automatic deployments | Off (`autoDeployTrigger: "off"`) |

The build installs the pinned dependencies, including test tools, and runs the
test suite before starting the service. One Uvicorn process is sufficient for
this small in-memory demo. No persistent disk, database, API key, or other secret
is needed. Access logging is disabled to avoid recording request URLs. Profiles
are sent in POST bodies, are not persisted, and must not be added to application
logs. Hosting providers still handle requests under their own policies.

Automatic deployments are disabled to keep later releases deliberate. Applying a
Blueprint still provisions a service and triggers its initial deployment; it is
not a preview-only operation. Do not apply it until publication is approved.
The `free` instance choice depends on Render's current account availability and
limits; check the dashboard before confirming. Free instances may spin down when
idle, so the first request may take longer. Do not attach a paid plan implicitly.

### When publication is approved

1. Commit these preparation files and merge the reviewed changes into `main`.
2. In Render, connect GitHub with access to `alperenyrmbs/youthopps-ai-mentor`.
3. Choose **New + > Blueprint**, select the repository and `main` branch, and
   review `render.yaml`. Applying this Blueprint begins the actual publication.
4. Alternatively choose **New + > Web Service** and enter the settings above.
   Set the health-check path and disable auto-deploys in service settings.
5. Review the instance plan and confirm only when ready to publish. Inspect build
   logs for a passing test suite, followed by successful application startup.
6. Use the actual HTTPS service URL assigned by Render; no public URL is assumed
   or reserved by this repository.

Verify the deployed paths using that assigned URL:

- `/health` must return HTTP 200 and `{"status":"ok","data_mode":"mock"}`.
- `/openapi.json` must return HTTP 200 with the `searchOpportunities` operation.
- `/docs` exposes interactive API documentation.
- Repeat the example POST request above against the deployed host and confirm
  `is_mock: true` and the fictional-data notice.

`/openapi.json` is generated by FastAPI, not served as an arbitrary repository
file. Private configuration files and source files are not mounted as static
content. Keep all future secrets in Render's environment settings, never in the
Blueprint. The public demo has no authentication or rate limiting and must not
be treated as a production service for sensitive personal data. This preparation
does not establish a completed ChatGPT integration or permission to use real
YouthOpps records.

Render documentation references (live access was blocked in the preparation
workspace, so dashboard/schema validation remains a deployment-time check):

- https://render.com/docs/deploy-fastapi
- https://render.com/docs/python-version
- https://render.com/docs/blueprint-spec
