"""The optional proxy recipe uses existing authenticated HTTPS, without a new port."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
spec = importlib.util.spec_from_file_location('proxy_recipe_compiler', FRAMEWORK/'blueprints/compile.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
sys.path.insert(0,str(FRAMEWORK/'proxmox/applications'))
import discovery
import foundation


class ProxyDashboardTests(unittest.TestCase):
    def configured(self):
        site = c.read(ROOT/'site.example.json')
        site['values']['domains.proxy'] = 'proxy.example.invalid'
        site['guests']['ingress'] = {'stack':{'routing':{'middlewares':{
            'authentik-forward':{'forwardAuth':{
                'address':'http://${addresses.identity_backend}:9000/outpost.goauthentik.io/auth/traefik',
                'trustForwardHeader':True}}}}}}
        return c.merge(site,c.read(ROOT/'recipes/proxy-dashboard.json'))

    def test_recipe_is_explicit_optin_and_preserves_unrelated_routes_and_runtime(self):
        base = c.compile_stack(ROOT,c.read(ROOT/'site.example.json'),[])
        self.assertNotIn('proxy',json.loads(base['ingress']['files']['stack.json'])['routing']['routes'])
        self.assertNotIn('dashboard',json.loads(base['ingress']['files']['stack.json'])['foundation'])
        selected = c.compile_stack(ROOT,self.configured(),[])
        for guest in set(base)-{'ingress','dns'}:
            self.assertEqual(selected[guest]['files'],base[guest]['files'])
        stack = json.loads(selected['ingress']['files']['stack.json'])
        before = json.loads(base['ingress']['files']['stack.json'])
        self.assertTrue(stack['foundation']['dashboard'])
        for key,route in before['routing']['routes'].items():
            self.assertEqual(stack['routing']['routes'][key],route)
        route=stack['routing']['routes']['proxy']
        self.assertEqual(route['service'],'api@internal')
        self.assertNotIn('url',route)
        http=discovery.shared(stack['routing'])['http']
        router=http['routers']['proxy']
        self.assertEqual(router['entryPoints'],['websecure'])
        self.assertEqual(router['tls'],{'certResolver':'letsencrypt'})
        self.assertEqual(router['middlewares'],['security-headers@file','authentik-forward@file','proxy-dashboard-root@file'])
        self.assertNotIn('proxy',http['services'])
        self.assertFalse(any('ipAllowList' in http['middlewares'][key.removesuffix('@file')]
                             for key in router['middlewares']))
        callback=http['routers']['proxy-authentik-callback']
        self.assertNotIn('authentik-forward@file',callback['middlewares'])
        self.assertIn('PathPrefix(`/outpost.goauthentik.io/`)',callback['rule'])
        self.assertEqual(http['middlewares']['proxy-dashboard-root']['redirectRegex']['replacement'],'https://${1}/dashboard/')
        self.assertNotIn('insecure',json.dumps(stack['foundation']))

    def test_recipe_refuses_disabled_dashboard_missing_auth_or_unknown_internal_service(self):
        for case in ('disabled','auth','undefined-auth','foreign-service'):
            site=self.configured()
            if case=='disabled':site['guests']['ingress']['stack']['foundation']['dashboard']=False
            elif case=='auth':site['routes']['proxy'].pop('authentik_forward_auth')
            elif case=='undefined-auth':site['guests']['ingress']['stack']['routing']['middlewares'].pop('authentik-forward')
            else:site['routes']['proxy']['target']['internal']='other'
            with self.subTest(case=case),self.assertRaises(ValueError):c.compile_stack(ROOT,site,[])


if __name__ == '__main__':
    unittest.main()
