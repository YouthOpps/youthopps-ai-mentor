from datetime import date

from .models import Opportunity, Recommendation, SearchRequest


# Small, explicit alias map; other terms use exact matching.
ALIASES = {'artificial intelligence': 'ai', 'computer engineering': 'technology'}

# Explicit prototype destination list, not EU membership. Transcontinental
# countries such as TR/RU are excluded. New regions need their own policy.
EUROPE_DESTINATIONS = frozenset(
    'AD AL AT BA BE BG BY CH CY CZ DE DK EE ES FI FR GB GR HR HU IE IS '
    'IT LI LT LU LV MC MD ME MK MT NL NO PL PT RO RS SE SI SK SM UA VA XK'.split()
)


def canonical(term: str) -> str:
    term = term.strip().casefold()
    return ALIASES.get(term, term)


def recommend(items: list[Opportunity], request: SearchRequest, today: date) -> list[Recommendation]:
    profile = request.profile
    results = []
    for item in items:
        if item.deadline is not None and item.deadline < today:
            continue
        if profile.opportunity_type and item.category != profile.opportunity_type:
            continue
        if profile.preferred_region == 'europe' and item.country.upper() not in EUROPE_DESTINATIONS:
            continue
        searchable = ' '.join([item.title, item.description, *item.interests]).casefold()
        if request.query and request.query.strip().casefold() not in searchable:
            continue
        rules = item.eligibility
        if rules.min_age is not None and profile.age < rules.min_age:
            continue
        if rules.max_age is not None and profile.age > rules.max_age:
            continue
        if rules.countries and profile.country is not None and profile.country not in rules.countries:
            continue
        if rules.education_levels is not None and profile.education not in rules.education_levels:
            continue

        score = 0
        reasons = []
        warnings = []
        # 40 interests + 20 selected type + 15 citizenship + 15 education + 10 age.
        shared = sorted({canonical(x) for x in profile.interests} & {canonical(x) for x in item.interests})
        if shared:
            score += round(40 * len(shared) / len({canonical(x) for x in profile.interests}))
            labels = {'technology': 'technology', 'ai': 'artificial intelligence', 'education': 'education',
                      'climate': 'climate', 'research': 'research'}
            reasons.append('Topics that match your interests: ' + ', '.join(labels.get(x, x) for x in shared) + '.')
        else:
            reasons.append('There is no direct interest match; this is a broader alternative.')
        if profile.opportunity_type:
            score += 20
            reasons.append('This matches the opportunity type you are looking for.')
        if rules.countries == []:
            score += 15
            reasons.append('This mock opportunity has no citizenship country restriction.')
        elif rules.countries is not None and profile.country is not None:
            score += 15
            reasons.append('Your stated citizenship meets the country requirement.')
        elif rules.countries:
            warnings.append('The country requirement cannot be confirmed without your citizenship; residence is not sufficient.')
        else:
            warnings.append('Citizenship eligibility is not specified.')
        if profile.preferred_region == 'europe':
            reasons.append('The destination matches your preference for Europe.')
        if rules.education_levels is not None:
            score += 15
            reasons.append('Your education level meets the stated requirement.')
        else:
            warnings.append('Education requirements are not specified.')
        if rules.min_age is not None and rules.max_age is not None:
            score += 10
            reasons.append('Your age is within the stated range.')
        else:
            warnings.append('Age requirements are not fully specified.')
        if item.deadline is None:
            warnings.append('The application deadline is unknown.')
        if not reasons:
            reasons.append('This matches your search filters; please check the eligibility details.')
        message = ' '.join(reasons) + ' This mock opportunity could be a starting point for exploring your options.'
        results.append(Recommendation(
            opportunity=item, score=score, reasons=reasons,
            eligibility_status='needs_review' if warnings else 'matches_stated_rules',
            warnings=warnings,
            mentor_message=message + (' Check the missing requirements before assuming you are eligible.' if warnings else ' For real applications, verify all requirements with the original source.'),
        ))
    return sorted(results, key=lambda x: (-x.score, x.opportunity.deadline or date.max, x.opportunity.id))
