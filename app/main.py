from datetime import date, datetime, timezone

from fastapi import Depends, FastAPI

from .matching import recommend
from .models import SearchRequest, SearchResponse
from .repository import MockRepository, OpportunityRepository

NOTICE = 'DEMO: Tüm fırsatlar kurgusal örnek verilerdir; gerçek ilan veya başvuru bağlantısı değildir.'
app = FastAPI(
    title='YouthOpp AI Mentor — Mock Prototype', version='0.1.0',
    description=NOTICE + ' Profil kaydedilmez. Puanlar başarı olasılığı değildir.',
)


def get_repository() -> OpportunityRepository:
    return MockRepository()


def get_today() -> date:
    return datetime.now(timezone.utc).date()


@app.get('/health', operation_id='getHealth')
def health() -> dict[str, str]:
    return {'status': 'ok', 'data_mode': 'mock'}


@app.post('/opportunities/search', response_model=SearchResponse,
          operation_id='searchOpportunities', summary='Profil için örnek fırsatları sırala',
          description=NOTICE, openapi_extra={'x-openai-isConsequential': False})
def search_opportunities(
    request: SearchRequest,
    repository: OpportunityRepository = Depends(get_repository),
    today: date = Depends(get_today),
) -> SearchResponse:
    results = recommend(repository.list_opportunities(), request, today)
    return SearchResponse(notice=NOTICE, is_mock=True, evaluated_on=today,
                          total=len(results), results=results[:request.limit])
