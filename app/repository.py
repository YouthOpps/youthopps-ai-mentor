"""Veri erişim sınırı: gelecekte izinli JSON adaptörü aynı arayüzü uygular."""
import json
from pathlib import Path
from typing import Protocol

from .models import Opportunity


class OpportunityRepository(Protocol):
    def list_opportunities(self) -> list[Opportunity]: ...


class MockRepository:
    def __init__(self, path: Path | None = None):
        self.path = path or Path(__file__).parent / 'data' / 'mock_opportunities.json'

    def list_opportunities(self) -> list[Opportunity]:
        rows = json.loads(self.path.read_text(encoding='utf-8'))
        opportunities = [Opportunity.model_validate(row) for row in rows]
        if any(not item.is_mock for item in opportunities):
            raise ValueError('MockRepository yalnızca örnek veri kabul eder.')
        return opportunities
