from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_today
from app.matching import recommend
from app.models import Opportunity, SearchRequest
from app.repository import MockRepository


@pytest.fixture
def client():
    app.dependency_overrides[get_today] = lambda: date(2026, 10, 15)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def payload():
    return {'profile': {'age': 22, 'country': 'tr', 'education': 'undergraduate',
                        'interests': ['artificial intelligence'], 'opportunity_type': 'scholarship'}}


def test_search_rank_and_mock_disclosure(client, payload):
    response = client.post('/opportunities/search', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_mock'] and 'fictional' in data['notice']
    assert data['evaluated_on'] == '2026-10-15'
    assert data['results'][0]['opportunity']['id'] == 'ai-scholarship'
    assert data['results'][0]['score'] == 100
    assert data['results'][0]['reasons']
    assert 'mock opportunity' in data['results'][0]['mentor_message']
    assert all(r['opportunity']['is_mock'] for r in data['results'])
    assert all(r['opportunity']['source_url'].startswith('https://example.org/') for r in data['results'])


@pytest.mark.parametrize('field,value', [('age', 0), ('age', 121), ('country', 'Turkey'),
                                         ('education', 'invalid'), ('interests', []),
                                         ('interests', ['   ']), ('opportunity_type', 'invalid')])
def test_invalid_profiles(client, payload, field, value):
    payload['profile'][field] = value
    assert client.post('/opportunities/search', json=payload).status_code == 422


@pytest.mark.parametrize('change', [{'age': 17}, {'country': 'US'}, {'education': 'doctoral'}])
def test_explicit_ineligibility_excluded(client, payload, change):
    payload['profile'].update(change)
    result = client.post('/opportunities/search', json=payload).json()
    assert 'ai-scholarship' not in [r['opportunity']['id'] for r in result['results']]


def test_unknown_eligibility_warns(client, payload):
    payload['profile']['opportunity_type'] = 'internship'
    data = client.post('/opportunities/search', json=payload).json()
    item = next(r for r in data['results'] if r['opportunity']['id'] == 'unknown-internship')
    assert item['eligibility_status'] == 'needs_review'
    assert len(item['warnings']) == 4
    assert item['score'] < 100


def test_text_filter_and_empty_results(client, payload):
    payload['query'] = 'Global'
    result = client.post('/opportunities/search', json=payload).json()
    assert result['total'] == 1
    assert result['results'][0]['opportunity']['id'] == 'global-scholarship'
    payload['query'] = 'no-such-opportunity'
    data = client.post('/opportunities/search', json=payload).json()
    assert data['total'] == 0 and data['results'] == []


def test_limit_and_all_categories(client, payload):
    payload['profile']['opportunity_type'] = None
    payload['limit'] = 1
    data = client.post('/opportunities/search', json=payload).json()
    assert data['total'] > 1 and len(data['results']) == 1
    payload['limit'] = 0
    assert client.post('/opportunities/search', json=payload).status_code == 422


def test_deadline_boundary_and_stable_order(payload):
    request = SearchRequest.model_validate(payload)
    original = MockRepository().list_opportunities()[0]
    expired = original.model_copy(update={'id': 'expired', 'deadline': date(2026, 10, 14)})
    today = original.model_copy(update={'id': 'today', 'deadline': date(2026, 10, 15)})
    future = original.model_copy(update={'id': 'future', 'deadline': date(2026, 10, 16)})
    result = recommend([expired, future, today], request, date(2026, 10, 15))
    assert [r.opportunity.id for r in result] == ['today', 'future']
    assert recommend([future, today], request, date(2026, 10, 15)) == result


def test_repository_is_replaceable(client, payload):
    from app.main import get_repository

    class EmptyRepository:
        def list_opportunities(self) -> list[Opportunity]:
            return []

    app.dependency_overrides[get_repository] = EmptyRepository
    assert client.post('/opportunities/search', json=payload).json()['results'] == []


def test_openapi_contract(client):
    schema = client.get('/openapi.json').json()
    operation = schema['paths']['/opportunities/search']['post']
    assert operation['operationId'] == 'searchOpportunities'
    assert operation['x-openai-isConsequential'] is False
    assert 'SearchRequest' in schema['components']['schemas']
    assert 'SearchResponse' in schema['components']['schemas']
    assert client.get('/health').json() == {'status': 'ok', 'data_mode': 'mock'}


def test_europe_internship_scenario(client):
    payload = {'profile': {'age': 22, 'residence_country': 'TR',
                          'education': 'undergraduate',
                          'interests': ['computer engineering'],
                          'opportunity_type': 'internship',
                          'preferred_region': 'europe'}}
    response = client.post('/opportunities/search', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['is_mock']
    assert [(r['opportunity']['id'], r['score']) for r in data['results']] == [
        ('software-internship-de', 100), ('software-internship-fr', 100),
        ('climate-internship', 60)]
    assert all(r['opportunity']['country'] != 'Remote' for r in data['results'])
    assert all(any('Europe' in reason for reason in r['reasons']) for r in data['results'])


def test_europe_excludes_non_european_and_unknown_destinations(payload):
    item = MockRepository().list_opportunities()[0]
    request = SearchRequest.model_validate(payload)
    request.profile.preferred_region = 'europe'
    records = [item.model_copy(update={'id': country, 'country': country})
               for country in ['DE', 'US', 'Remote', 'Unknown']]
    result = recommend(records, request, date(2026, 10, 15))
    assert [r.opportunity.country for r in result] == ['DE']


def test_residence_does_not_prove_citizenship(client, payload):
    payload['profile'].pop('country')
    payload['profile']['residence_country'] = 'TR'
    data = client.post('/opportunities/search', json=payload).json()
    item = next(r for r in data['results'] if r['opportunity']['id'] == 'ai-scholarship')
    assert item['score'] == 85
    assert item['eligibility_status'] == 'needs_review'
    assert any('residence is not sufficient' in warning for warning in item['warnings'])


def test_unknown_region_is_rejected(client, payload):
    payload['profile']['preferred_region'] = 'somewhere'
    assert client.post('/opportunities/search', json=payload).status_code == 422
