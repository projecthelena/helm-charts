#!/usr/bin/env python3
import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

import yaml


class WardenChartTests(unittest.TestCase):
    def render(self, values=None, error=None):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'values.json'
            path.write_text(json.dumps(values or {}))
            result = subprocess.run(['helm', 'template', 'warden', 'charts/warden', '-f', str(path)],
                                    text=True, capture_output=True)
        if error:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(error, result.stderr)
            return []
        self.assertEqual(result.returncode, 0, result.stderr)
        return [item for item in yaml.safe_load_all(result.stdout) if item]

    def test_defaults_use_one_scheduler_and_pinned_image(self):
        docs = self.render()
        deployment = next(d for d in docs if d['kind'] == 'Deployment')
        self.assertEqual(deployment['spec']['replicas'], 1)
        self.assertEqual(deployment['spec']['strategy']['type'], 'Recreate')
        self.assertNotIn('app.kubernetes.io/component', deployment['spec']['selector']['matchLabels'])
        version = yaml.safe_load(Path('charts/warden/Chart.yaml').read_text())['appVersion']
        self.assertEqual(deployment['spec']['template']['spec']['containers'][0]['image'],
                         f'ghcr.io/projecthelena/warden:v{version}')

    def test_service_selects_warden_and_not_postgres(self):
        docs = self.render({'database': {'type': 'postgres', 'postgres': {'enabled': True}},
                            'podLabels': {'app.kubernetes.io/component': 'custom'}})
        service = next(d for d in docs if d['kind'] == 'Service' and d['metadata']['name'] == 'warden')
        selected = []
        for pod in [d for d in docs if d['kind'] in ['Deployment', 'StatefulSet']]:
            labels = pod['spec']['template']['metadata']['labels']
            if all(labels.get(k) == v for k, v in service['spec']['selector'].items()):
                selected.append(pod['kind'])
        self.assertEqual(selected, ['Deployment'])
        deployment = next(d for d in docs if d['kind'] == 'Deployment')
        self.assertEqual(deployment['spec']['strategy']['type'], 'Recreate')

    def test_service_port_does_not_change_http_listener(self):
        docs = self.render({'service': {'port': 80}})
        deployment = next(d for d in docs if d['kind'] == 'Deployment')
        service = next(d for d in docs if d['kind'] == 'Service')
        self.assertEqual(service['spec']['ports'][0]['port'], 80)
        self.assertEqual(deployment['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort'], 9090)
        docs = self.render({'config': {'listenAddr': ':8080'}})
        deployment = next(d for d in docs if d['kind'] == 'Deployment')
        self.assertEqual(deployment['spec']['template']['spec']['containers'][0]['ports'][0]['containerPort'], 8080)

    def test_postgres_credentials_are_encoded(self):
        password = 'example @:/?#%+ password'
        docs = self.render({'database': {'type': 'postgres', 'postgres': {
            'enabled': True, 'auth': {'password': password}}}})
        secret = next(d for d in docs if d['kind'] == 'Secret')
        self.assertEqual(base64.b64decode(secret['data']['password']).decode(), password)
        url = base64.b64decode(secret['data']['db-url']).decode()
        self.assertEqual(unquote(urlsplit(url).password), password)

    def test_external_postgres_uses_existing_secret(self):
        docs = self.render({'database': {'type': 'postgres', 'external': {
            'enabled': True, 'existingSecret': 'example-db'}}})
        self.assertFalse(any(d['kind'] in ['StatefulSet', 'Secret'] for d in docs))
        deployment = next(d for d in docs if d['kind'] == 'Deployment')
        env = deployment['spec']['template']['spec']['containers'][0]['env']
        db = next(e for e in env if e['name'] == 'DB_URL')
        self.assertEqual(db['valueFrom']['secretKeyRef']['name'], 'example-db')

    def test_invalid_database_combinations_are_rejected(self):
        for db, error in [
            ({'type': 'postgres'}, 'exactly one'),
            ({'type': 'postgres', 'postgres': {'enabled': True}, 'external': {'enabled': True}}, 'exactly one'),
            ({'type': 'postgres', 'external': {'enabled': True}}, 'External PostgreSQL requires'),
            ({'postgres': {'enabled': True}}, 'database.type=postgres'),
        ]:
            with self.subTest(db=db):
                self.render({'database': db}, error=error)

    def test_multiple_schedulers_are_rejected(self):
        self.render({'replicaCount': 2}, error='replicaCount')

    def test_observability_cannot_be_exposed_by_service(self):
        for service_type in ['LoadBalancer', 'NodePort']:
            with self.subTest(service_type=service_type):
                self.render({'observability': {'enabled': True}, 'service': {'type': service_type}},
                            error='ClusterIP')
        self.render({'observability': {'enabled': True, 'port': 9090}}, error='must differ')
        self.render({'observability': {'enabled': True}})

    def test_invalid_listener_ports_are_rejected(self):
        for address in [':0', ':65536', ':invalid']:
            with self.subTest(address=address):
                self.render({'config': {'listenAddr': address}}, error='listenAddr')


if __name__ == '__main__':
    unittest.main()
