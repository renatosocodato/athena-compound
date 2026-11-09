"""Fetch pinned official fixture files and an official Vina v1.2.7 executable.

Third-party inputs/engine remain in a user-selected directory, not in the
software distribution. The upstream licence is Apache-2.0; retain it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import urllib.request

COMMIT='8eb40404f4f45608acb3b01427587ac049f27c1f'
EXPECTED={'1iep_receptor.pdbqt':'f13cf3b36f61d87c3b58983e0b8ecf1c3456a685eb86dfe9ccfb139c7bdc2586',
          '1iep_ligand.pdbqt':'15fb35648d8c18c70317842f3a0631b73a19429c710a037ab07310084d579bb8',
          'LICENSE':'cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30',
          'vina_1.2.7_mac_aarch64':'823c2bbacf26d72183861322345f0a89736aca66c8e81054c66f93af5ad623f1',
          'vina_1.2.7_linux_x86_64':'f31f774f723bba7bbe6e9d1c47577020eea9a8da16424284c043d22593570644',
          'vina_1.2.7_linux_aarch64':'d30c18a7d5f6f8ea9146e1cbc0aa7ade0bbb105b54ece08b4e5a7fa53edb6c62',
          }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('Output directory must be new')
    args.output.mkdir(parents=True)
    operating={'Darwin':'mac','Linux':'linux'}.get(platform.system())
    arch={'arm64':'aarch64','aarch64':'aarch64','x86_64':'x86_64','AMD64':'x86_64'}.get(platform.machine())
    if operating is None or arch is None:parser.error('Unsupported platform')
    binary=f'vina_1.2.7_{operating}_{arch}'
    base=f'https://raw.githubusercontent.com/forlilab/AutoDock-Vina/{COMMIT}/'
    sources={binary:f'https://github.com/forlilab/AutoDock-Vina/releases/download/v1.2.7/{binary}',
             '1iep_receptor.pdbqt':base+'example/basic_docking/solution/1iep_receptor.pdbqt',
             '1iep_ligand.pdbqt':base+'example/basic_docking/solution/1iep_ligand.pdbqt',
             'LICENSE':base+'LICENSE'}
    rows=[]
    for filename,url in sources.items():
        with urllib.request.urlopen(url,timeout=90) as response:data=response.read()
        digest=hashlib.sha256(data).hexdigest()
        if filename in EXPECTED and digest!=EXPECTED[filename]:raise RuntimeError('Pinned fixture/engine checksum mismatch')
        (args.output/filename).write_bytes(data)
        rows.append({'file':filename,'url':url,'sha256':digest,'matches_pinned_digest':filename in EXPECTED})
    (args.output/binary).chmod(0o755)
    (args.output/'DOWNLOADS.json').write_text(json.dumps({'upstream_commit':COMMIT,'files':rows,
        'licence':'Apache-2.0','binary_digest_note':'Official releases publish no independent digest for this asset; locally observed hashes do not constitute a signature guarantee.'},indent=2)+'\n')
    print(binary)


if __name__=='__main__':main()
