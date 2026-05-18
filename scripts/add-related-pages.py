"""
add-related-pages.py
Adds `relatedGuides` to every manifest entry based on category/subcategory overlap.
"""
import json, glob

def main():
    manifest_files = sorted(glob.glob('data/manifests/*.json'))
    
    # Load all manifests, track source file
    all_manifests = []
    for fpath in manifest_files:
        data = json.load(open(fpath))
        for m in data:
            m['_src'] = fpath
            all_manifests.append(m)

    # For each manifest, find related pages
    for m in all_manifests:
        related = []
        cat = m.get('category', '')
        sub = m.get('subcategory', '') or ''

        # 1: same subcategory roundup + comparison
        for other in all_manifests:
            if other['slug'] == m['slug']:
                continue
            if other.get('category') == cat and (other.get('subcategory') or '') == sub:
                if other['type'] in ('roundup', 'comparison'):
                    related.append({
                        'title': other['title'],
                        'slug': other['slug'],
                        'description': other.get('description', ''),
                    })

        # 2: sibling subcategory roundups
        if len(related) < 4:
            for other in all_manifests:
                if other['slug'] == m['slug']:
                    continue
                if other.get('category') == cat and (other.get('subcategory') or '') != sub:
                    if other['type'] == 'roundup':
                        if not any(r['slug'] == other['slug'] for r in related):
                            related.append({
                                'title': other['title'],
                                'slug': other['slug'],
                                'description': other.get('description', ''),
                            })

        # 3: cross-category roundups
        if len(related) < 4:
            for other in all_manifests:
                if other['slug'] == m['slug']:
                    continue
                if other.get('category') != cat and other['type'] == 'roundup':
                    if not any(r['slug'] == other['slug'] for r in related):
                        related.append({
                            'title': other['title'],
                            'slug': other['slug'],
                            'description': other.get('description', ''),
                        })

        m['relatedGuides'] = related[:4]

    # Group back by source file
    file_map = {}
    for m in all_manifests:
        f = m.pop('_src')
        file_map.setdefault(f, []).append(m)

    for fpath, manifests in file_map.items():
        json.dump(manifests, open(fpath, 'w'), indent=2)
        print(f"Wrote {len(manifests)} manifests to {fpath}")

    total_links = sum(len(m.get('relatedGuides', [])) for m in all_manifests)
    print(f"\nTotal relatedGuides links: {total_links}")

if __name__ == '__main__':
    main()
