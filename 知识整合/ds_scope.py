"""Attach explicit DS statement matches; never infer exam scope from keywords."""
from pathlib import Path
import hashlib, json, re

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

def attach_ds_scope(config, cards):
    scope = config.get('ds_scope')
    if not scope:
        return None
    mapping = json.loads((BASE / scope['mapping']).read_text(encoding='utf-8'))['statements']
    ds_folder = ROOT / '期中复习'
    exam = json.loads((ds_folder / 'exam.json').read_text(encoding='utf-8'))
    canonical = set(re.findall(r'^% @note (c[1-8]-\d{2})\|',
                              (ds_folder / 'content/knowledge.tex').read_text(encoding='utf-8'), re.M))
    website = ROOT / 'site/ds'
    if not website.exists():
        website = ROOT / 'ds'  # Repository checkout, where published files sit at the root.
    manifest = json.loads((website / 'resource-manifest.json').read_text(encoding='utf-8'))
    official_digest = hashlib.sha256((ROOT / config['sources'][scope['source']]['path']).read_bytes()).hexdigest()
    assert official_digest == manifest['sources']['programme']['sha256'], 'Rebuild DS metadata after the official programme PDF changes'
    statements = {}
    for chapter in manifest['chapters']:
        data = json.loads((website / chapter['data']).read_text(encoding='utf-8'))
        for statement in data['cards']:
            assert statement['id'] not in statements, 'Duplicate official statement'
            statements[statement['id']] = statement
    assert set(mapping) == canonical == set(statements), 'DS map must cover exactly the official knowledge list'
    assert len(mapping) == sum(ch['count'] for ch in exam['chapters'])
    index = {c['id']: c for c in cards}
    proofs = {p['card']: p['number'] for p in exam['proof_cards']}
    statement_only = {ch['id'] for ch in exam['chapters'] if ch.get('statements_only')}
    for card in cards:
        card['ds'] = []
    for identifier, targets in mapping.items():
        assert targets and len(targets) == len(set(targets)), 'Empty or duplicate DS targets: ' + identifier
        statement = statements[identifier]
        for target in targets:
            assert target in index and index[target]['type'] != 'exercise', 'Unknown/non-course DS target: ' + target
            assert int(index[target]['chapter'][2:]) <= 8, 'Probability chapter incorrectly marked for DS'
            index[target]['ds'].append({
                'id': identifier, 'title': statement['title'], 'fr': statement['title_fr'],
                'pages': sorted({p['page'] for p in statement['originals']}),
                'also': [t for t in targets if t != target],
                'statements_only': int(identifier[1]) in statement_only,
                'proof': proofs.get(identifier)
            })
    for excluded in ['dynkin', 'measure-uniqueness']:
        assert not index[excluded]['ds'], 'Excluded independent statement tagged for DS'
    tagged = [c for c in cards if c['ds']]
    assert all(c['ds'] for c in cards if c.get('ds_added')), 'New DS supplement missing its tag'
    report = {
        'statements': len(statements), 'mapped_cards': len(tagged),
        'existing_marked_cards': sum(not c.get('ds_added') for c in tagged),
        'added_cards': [c['id'] for c in tagged if c.get('ds_added')],
        'proof_links': len(proofs), 'statement_only_chapters': sorted(statement_only),
        'official_source_sha256': official_digest,
        'mapping': mapping,
        'note': 'Explicit statement correspondence; additional content/proofs within a card are not automatically required for DS.'
    }
    scope['summary'] = report
    return report
