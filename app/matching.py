from datetime import date

from .models import Opportunity, Recommendation, SearchRequest


# Küçük ve açık bir sözlük; bilinmeyen terimler tam eşleşmeyle değerlendirilir.
ALIASES = {'yapay zeka': 'ai', 'artificial intelligence': 'ai',
           'teknoloji': 'technology', 'eğitim': 'education',
           'iklim': 'climate', 'araştırma': 'research',
           'bilgisayar mühendisliği': 'technology', 'computer engineering': 'technology'}

# Prototipin açık hedef listesi: AB değildir; TR/RU gibi kıtalararası
# ülkeler bu varsayılan filtrede yoktur. Yeni bölgeler ayrı politika ister.
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
        # 40 ilgi + 20 tür tercihi + 15 ülke + 15 eğitim + 10 yaş.
        shared = sorted({canonical(x) for x in profile.interests} & {canonical(x) for x in item.interests})
        if shared:
            score += round(40 * len(shared) / len({canonical(x) for x in profile.interests}))
            labels = {'technology': 'teknoloji', 'ai': 'yapay zeka', 'education': 'eğitim',
                      'climate': 'iklim', 'research': 'araştırma'}
            reasons.append('İlgi alanlarınla ortak konular: ' + ', '.join(labels.get(x, x) for x in shared) + '.')
        else:
            reasons.append('İlgi alanlarınla doğrudan eşleşme bulunmadı; bu daha genel bir alternatif.')
        if profile.opportunity_type:
            score += 20
            reasons.append('Aradığın fırsat türüyle eşleşiyor.')
        if rules.countries == []:
            score += 15
            reasons.append('Örnek ilanda vatandaşlık ülkesi kısıtlaması yok.')
        elif rules.countries is not None and profile.country is not None:
            score += 15
            reasons.append('Belirttiğin vatandaşlık ülkesi koşula uyuyor.')
        elif rules.countries:
            warnings.append('Vatandaşlık ülken bilinmediği için ülke koşulu doğrulanamadı; ikamet yeterli değildir.')
        else:
            warnings.append('Vatandaşlık uygunluğu belirtilmemiş.')
        if profile.preferred_region == 'europe':
            reasons.append('Fırsatın hedef ülkesi Avrupa tercihinle eşleşiyor.')
        if rules.education_levels is not None:
            score += 15
            reasons.append('Eğitim düzeyin belirtilen koşula uyuyor.')
        else:
            warnings.append('Eğitim koşulu belirtilmemiş.')
        if rules.min_age is not None and rules.max_age is not None:
            score += 10
            reasons.append('Yaşın belirtilen aralıkta.')
        else:
            warnings.append('Yaş koşulu tam belirtilmemiş.')
        if item.deadline is None:
            warnings.append('Son başvuru tarihi bilinmiyor.')
        if not reasons:
            reasons.append('Seçtiğin arama filtrelerine uyuyor; uygunluk bilgilerini kontrol etmelisin.')
        message = ' '.join(reasons) + ' Bu örnek fırsat, seçeneklerini keşfetmen için bir başlangıç olabilir.'
        results.append(Recommendation(
            opportunity=item, score=score, reasons=reasons,
            eligibility_status='needs_review' if warnings else 'matches_stated_rules',
            warnings=warnings,
            mentor_message=message + (' Eksik koşulları doğrulamadan uygun olduğunu varsayma.' if warnings else ' Gerçek başvurularda tüm koşulları kaynakta doğrula.'),
        ))
    return sorted(results, key=lambda x: (-x.score, x.opportunity.deadline or date.max, x.opportunity.id))
