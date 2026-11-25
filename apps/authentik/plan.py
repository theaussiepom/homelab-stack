"""Print or verify the pinned Authentik upgrade path using the selected framework."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

import yaml
from authentik_releases import plugin, select, validate

CATALOGUE = Path(__file__).resolve().parents[2] / 'images.json'
ACCEPT = ', '.join(('application/vnd.oci.image.index.v1+json',
                    'application/vnd.docker.distribution.manifest.list.v2+json'))


def published(upstream):
    output = subprocess.check_output([
        'gh', 'api', '--paginate', f'repos/{upstream}/releases?per_page=100',
        '--jq', '.[] | select(.draft == false and .prerelease == false) | .tag_name',
    ], text=True, timeout=120)
    return [tag.removeprefix('version/') for tag in output.splitlines() if tag.startswith('version/')]


def registry(repository):
    host, name = repository.split('/', 1)
    with urllib.request.urlopen(f'https://{host}/token?service={host}&scope=repository:{name}:pull',
                                timeout=30) as response:
        token = json.load(response)['token']

    def resolve(tag):
        request = urllib.request.Request(f'https://{host}/v2/{name}/manifests/{tag}', headers={
            'Authorization': 'Bearer ' + token, 'Accept': ACCEPT})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            digest = 'sha256:' + hashlib.sha256(raw).hexdigest()
            if response.headers['Docker-Content-Digest'] != digest:
                raise ValueError('Registry image digest mismatch for ' + tag)
        platforms = [row.get('platform', {}) for row in json.loads(raw)['manifests']]
        if not any(p.get('os') == 'linux' and p.get('architecture') == 'amd64' for p in platforms):
            raise ValueError('No Linux amd64 image for ' + tag)
        return digest

    return resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', help='Last successfully deployed tag and digest')
    parser.add_argument('--check-app', type=Path, help='Verify the reviewed declaration against the stack catalogue')
    args = parser.parse_args()
    policy = plugin(yaml.safe_load(Path(__file__).with_name('image-update.yaml').read_text()))
    reviewed = None
    if args.check_app:
        app = yaml.safe_load(args.check_app.read_text())
        if app['profile'] != policy['owner']:
            raise ValueError('The Authentik plugin requires its own profile')
        reviewed = app['properties']['upgrade_path']
        validate(reviewed)
    source = args.source or (reviewed[0] if reviewed else None)
    if source is None:
        parser.error('Supply the accepted image or a declaration to verify')
    image = json.loads(CATALOGUE.read_text())[policy['owner']]
    target = f"{image['repository']}:{image['tag']}@{image['digest']}"
    chain = select(source, published(policy['upstream']), registry(policy['image']),
                   through=target)
    if reviewed is not None and chain != reviewed:
        raise ValueError('The reviewed chain differs from the complete upstream release sequence')
    print(json.dumps(chain, indent=2))


if __name__ == '__main__':
    main()
