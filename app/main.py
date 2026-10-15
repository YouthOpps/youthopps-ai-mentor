from datetime import date, datetime, timezone

from fastapi import Depends, FastAPI

from .matching import recommend
from .models import SearchRequest, SearchResponse
from .repository import MockRepository, OpportunityRepository

NOTICE = 'DEMO: All opportunities are fictional mock records, not real listings or application links.'
app = FastAPI(
    title='YouthOpp AI Mentor — Mock Prototype', version='0.1.0',
    description=NOTICE + ' Profiles are not stored. Scores are not acceptance probabilities.',
)


def get_repository() -> OpportunityRepository:
    return MockRepository()


def get_today() -> date:
    return datetime.now(timezone.utc).date()


@app.get('/health', operation_id='getHealth')
def health() -> dict[str, str]:
    return {'status': 'ok', 'data_mode': 'mock'}


@app.post('/opportunities/search', response_model=SearchResponse,
          operation_id='searchOpportunities', summary='Rank mock opportunities for a profile',
          description=NOTICE, openapi_extra={'x-openai-isConsequential': False})
def search_opportunities(
    request: SearchRequest,
    repository: OpportunityRepository = Depends(get_repository),
    today: date = Depends(get_today),
) -> SearchResponse:
    results = recommend(repository.list_opportunities(), request, today)
    return SearchResponse(notice=NOTICE, is_mock=True, evaluated_on=today,
                          total=len(results), results=results[:request.limit])
