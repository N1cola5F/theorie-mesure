"""Write an immutable content inventory; refuse to replace an existing version."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    parser.add_argument('--date', required=True, help='Release date YYYY-MM-DD')
    parser.add_argument('--previous', type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'v\d+\.\d+\.\d+', args.version):
        raise ValueError('Use vMAJOR.MINOR.PATCH')
    datetime.strptime(args.date, '%Y-%m-%d')
    destination = ROOT / '维护记录' / '版本清单' / (args.version + '.json')
    if destination.exists():
        raise FileExistsError('A published snapshot is immutable: ' + str(destination))
    allowed = {'.pdf', '.md', '.tex', '.py', '.json', '.png', '.pptx', '.docx', '.html', '.css', '.js', '.svg', '.txt', '.otf', '.woff', '.woff2'}
    records = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or (path.suffix.lower() not in allowed and path.name != '.nojekyll'):
            continue
        relative = path.relative_to(ROOT)
        if any(part in {'tmp', 'build', '.git', '__pycache__', '版本清单', '.playwright-cli'} for part in relative.parts):
            continue
        if relative.parts[:2] == ('output', 'playwright'):
            continue
        if relative.parts[0] == '按周划分' and path.suffix.lower() == '.pdf':
            category = 'derived_solution' if '中文详解' in path.name else 'source_pdf'
        elif relative.parts[0] == '处理后_md':
            category = 'historical_transcription'
        elif relative.parts[0] in {'知识整合', 'site'} or (path.name.startswith('测量理论_知识整合') and path.suffix.lower()=='.html'):
            category = 'knowledge_reader'
        elif relative.parts[0] == '参考html':
            category = 'design_reference'
        elif relative.parts[0] == 'output':
            category = 'derived_solution_or_source'
        else:
            category = 'maintenance'
        record = {
            'path': relative.as_posix(),
            'category': category,
            'size_bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()
        }
        if path.suffix.lower() == '.pdf':
            record['pdf_pages'] = len(PdfReader(path).pages)
        records.append(record)
    delta = None
    if args.previous:
        previous = json.loads(args.previous.read_text(encoding='utf-8'))
        old = {r['path']: r['sha256'] for r in previous['files']}
        new = {r['path']: r['sha256'] for r in records}
        delta = {
            'previous_version': previous['version'],
            'added': sorted(new.keys() - old.keys()),
            'removed': sorted(old.keys() - new.keys()),
            'modified': sorted(p for p in new.keys() & old.keys() if new[p] != old[p])
        }
    manifest = {
        'version': args.version,
        'release_date': args.date,
        'timezone': 'Asia/Shanghai',
        'recorded_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
        'scope': 'All supported content and maintenance files; excludes tmp, build, .git, caches, output/playwright, and snapshot files.',
        'history_note': 'First formal snapshot. v1.0.0 was retrospectively documented, without a recoverable full snapshot.' if not args.previous else '',
        'comparison': delta,
        'file_count': len(records),
        'files': records
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents replacing a historical snapshot.
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(destination)
    print(f'{len(records)} files recorded')

if __name__ == '__main__':
    main()
