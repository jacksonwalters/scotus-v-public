"""Small inline SVG; no plotting globals, filenames, or server-side image writes."""
from html import escape


def chart(court, public):
    years = sorted(set(court) | set(public))
    if not years:
        return ''
    lo, hi = min(years) - 1, max(years) + 1
    x = lambda year: 85 + 670 * (year - lo) / (hi - lo)
    y = lambda value: 170 - 125 * value
    parts = ['<svg viewBox="0 0 800 345" role="img" aria-label="Ideological polarity by year">']
    for value, label in [(-1, 'Conservative'), (0, 'Neutral'), (1, 'Liberal')]:
        parts.append(f'<path d="M85 {y(value)} H755" stroke="#d8dde6"/><text x="78" y="{y(value)+4}" text-anchor="end" font-size="11">{label}</text>')
    for year in sorted(set([min(years), (min(years)+max(years))//2, max(years)])):
        parts.append(f'<text x="{x(year)}" y="322" text-anchor="middle" font-size="12">{year}</text>')
    for data, color, name in [(court, '#bd493d', 'Court'), (public, '#2467ad', 'Public')]:
        for year, value in data.items():
            parts.append(f'<circle cx="{x(year):.2f}" cy="{y(value):.2f}" r="4" fill="{color}"><title>{escape(name)} {year}: {value:.3f}</title></circle>')
        if len(data) >= 2:
            mx, my = sum(data)/len(data), sum(data.values())/len(data)
            slope = sum((a-mx)*(b-my) for a,b in data.items()) / sum((a-mx)**2 for a in data)
            a, b = min(data), max(data)
            parts.append(f'<path d="M{x(a):.2f} {y(my+slope*(a-mx)):.2f} L{x(b):.2f} {y(my+slope*(b-mx)):.2f}" stroke="{color}" stroke-width="2"/>')
    return ''.join(parts) + '</svg>'
