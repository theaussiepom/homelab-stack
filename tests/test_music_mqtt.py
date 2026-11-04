"""The additional guest boundaries keep one broker and preserve radio identities."""
import copy
import ipaddress
import json
import os
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
import yaml
from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = Path(os.environ.get('HOMELAB_FRAMEWORK', ROOT.parent/'homelab')).resolve()
sys.path.insert(0, str(FRAMEWORK/'blueprints'))
sys.path.insert(0, str(FRAMEWORK/'proxmox/applications'))
import compile as compiler
import connections
import discovery
import render
import workflows


class MusicMQTTTests(unittest.TestCase):
    def packets(self, overlay=None):
        return compiler.compile_stack(ROOT, overlay or compiler.read(ROOT/'site.example.yaml'), [])

    def cfgs(self):
        return {name: json.loads(packet['files']['site.json']) for name,packet in self.packets().items()}

    def test_default_guests_add_music_and_one_broker_without_optional_exclusions(self):
        packets=self.packets()
        self.assertEqual(len(packets),13)
        self.assertTrue(all(p['enabled'] for p in packets.values()))
        self.assertEqual(set(packets),set(compiler.CATALOGUE)-{'monitoring'})
        cfg=self.cfgs()
        self.assertEqual(cfg['music']['guest']['vmid'],207)
        self.assertEqual(cfg['mqtt']['guest']['vmid'],217)
        self.assertEqual(cfg['music']['guest']['interfaces'][2]['bridge'],'vmbr1')
        self.assertEqual(cfg['music']['guest']['interfaces'][2]['vlan'],100)
        self.assertEqual(cfg['mqtt']['guest']['interfaces'][2]['bridge'],'vmbr1')
        self.assertEqual(cfg['mqtt']['guest']['interfaces'][2]['vlan'],41)
        for guest in ['music','mqtt']:
            self.assertEqual(sum(bool(n.get('gateway'))for n in cfg[guest]['guest']['interfaces']),1)
        self.assertEqual(set(json.loads(packets['automation']['files']['stack.json'])['services']),
                         {'homeassistant','node_red'})
        self.assertNotIn('mqtt',cfg['automation']['app']['service_health_checks'])
        self.assertNotIn('published_services',cfg['automation']['app'])
        self.assertEqual(cfg['mqtt']['app']['published_services']['mqtt']['hostname'],'broker.mqtt')
        for guest in ['music','mqtt']:
            self.assertFalse(cfg[guest]['app']['exclusive_writer_confirmed'])
            self.assertNotIn('capture',cfg[guest]['app'])
        with self.assertRaisesRegex(ValueError,'prerequisite'):
            compiler.compile_stack(ROOT,compiler.read(ROOT/'site.example.yaml'),['mqtt'])
        excluded=compiler.compile_stack(ROOT,compiler.read(ROOT/'site.example.yaml'),['music'])
        self.assertFalse(excluded['music']['enabled'])
        self.assertTrue(excluded['mqtt']['enabled'])
        no_automation=compiler.compile_stack(ROOT,compiler.read(ROOT/'site.example.yaml'),['automation','music'])
        self.assertTrue(no_automation['zigbee2mqtt']['enabled'])
        self.assertEqual(workflows.models(ROOT)['deploy.yml']['jobs']['zigbee2mqtt']['needs'],['selection','mqtt'])

    def test_music_can_deploy_without_automation_but_still_requires_dns_and_ingress(self):
        overlay=compiler.read(ROOT/'site.example.yaml')
        baseline=self.packets(overlay)
        without=compiler.compile_stack(ROOT,overlay,['automation'])
        self.assertFalse(without['automation']['enabled'])
        self.assertTrue(without['music']['enabled'])
        self.assertEqual(without['music']['files'],baseline['music']['files'])
        declared=compiler.manifest(ROOT)['guests']
        self.assertEqual(declared['music']['depends_on'],['dns','ingress'])
        deploy=workflows.models(ROOT)['deploy.yml']
        self.assertEqual(deploy['jobs']['music']['needs'],['selection','dns','ingress'])
        for required in ('dns','ingress'):
            enabled={'music'} | ({'dns'} if required=='ingress' else set())
            disabled=sorted(set(declared)-enabled)
            with self.subTest(required=required),self.assertRaisesRegex(ValueError,'prerequisite'):
                compiler.compile_stack(ROOT,overlay,disabled)

    def test_radios_label_preserves_the_radio_and_winet_runtime_identity(self):
        packet=self.packets()['zigbee2mqtt'];cfg=json.loads(packet['files']['site.json'])
        self.assertEqual(cfg['guest']['hostname'], 'radios')
        self.assertEqual(cfg['app']['hostname'], 'radios')
        self.assertEqual(cfg['guest']['vmid'],209)
        self.assertEqual(cfg['app']['kind'],'zigbee2mqtt')
        self.assertEqual([n['ipv4']for n in cfg['guest']['interfaces']],
                         ['198.18.25.22/24','198.18.30.22/24','198.19.107.246/24'])
        stack=json.loads(packet['files']['stack.json']);compose=render.compose(stack)
        self.assertEqual(set(compose['services']),{'zigbee2mqtt','winet'})
        self.assertEqual(compose['services']['zigbee2mqtt']['volumes'][0]['source'],
                         '/srv/homelab/data/zigbee2mqtt')
        self.assertEqual(compose['services']['zigbee2mqtt']['volumes'][1]['target'],'/dev/ttyACM0')
        self.assertEqual(compose['services']['zigbee2mqtt']['image'],
                         'koenkk/zigbee2mqtt@sha256:fef0de769dcd04c27b3a6d277b61046eb96284bdd4198dcb1687c3a01b3020f3')
        self.assertEqual(workflows.models(ROOT)['deploy.yml']['jobs']['zigbee2mqtt']['name'],'Radios')

    def test_music_uses_upstream_latest_and_prepared_data_without_added_privileges(self):
        packet=self.packets()['music'];cfg=json.loads(packet['files']['site.json'])
        stack=json.loads(packet['files']['stack.json']);service=render.compose(stack)['services']['music_assistant']
        self.assertEqual(service['image'],'ghcr.io/music-assistant/server:latest')
        self.assertEqual(service['network_mode'],'host')
        self.assertEqual(service['restart'],'always')
        self.assertEqual(stack['music_bind_address'],'198.19.100.241')
        self.assertEqual(service['volumes'][0],{'type':'bind','source':'/srv/homelab/data/music-assistant/data',
                         'target':'/data','bind':{'create_host_path':False}})
        self.assertFalse(service['volumes'][0].get('read_only',False))
        self.assertFalse({'privileged','devices','cap_add','security_opt','user','entrypoint'}&service.keys())
        self.assertEqual(cfg['app']['endpoints']['music_assistant']['web'],'http://198.19.100.241:8095')
        self.assertEqual(cfg['routes']['music']['host'],'music.example.invalid')
        self.assertEqual(cfg['routes']['music']['middlewares'],['security-headers','music-clients'])
        self.assertNotIn('new_target',cfg['app'])

    def test_music_requires_the_real_https_info_route_after_local_service_health(self):
        overlay=compiler.read(ROOT/'site.example.yaml')
        overlay['values'].update({'domains.music':'music-override.example.invalid',
                                  'addresses.ingress_frontend':'198.18.40.133',
                                  'addresses.music_home':'198.19.100.240'})
        packets=self.packets(overlay)
        cfg=json.loads(packets['music']['files']['site.json'])
        checks=cfg['app']['service_health_checks']['music_assistant']
        self.assertEqual(checks,cfg['app']['health_checks'])
        self.assertEqual(len(checks),2)
        self.assertEqual(checks[0]['expect'],'core service only: passed')
        route=checks[1]
        self.assertEqual(route['expect'],'server_version')
        self.assertEqual(route['argv'][0],'curl')
        self.assertEqual(route['argv'][-1],'https://music-override.example.invalid/info')
        self.assertEqual(route['argv'][route['argv'].index('--resolve')+1],
                         'music-override.example.invalid:443:198.18.40.133')
        self.assertEqual(route['argv'][route['argv'].index('--interface')+1],'198.19.100.240')
        self.assertIn('198.19.100.240/24',[nic['ipv4']for nic in cfg['guest']['interfaces']])
        ingress=json.loads(packets['ingress']['files']['stack.json'])
        self.assertEqual(ingress['routing']['middlewares']['music-clients'],
                         {'ipAllowList':{'sourceRange':['198.18.10.0/28','198.19.100.0/24']}})
        self.assertIn('--fail',route['argv'])
        self.assertFalse({'--insecure','-k','--location','-L'}&set(route['argv']))
        play=yaml.safe_load((FRAMEWORK/'proxmox/applications/ansible/reconcile.yml').read_text())[0]
        health=next(task for task in play['tasks'] if task.get('loop')=='{{ app.health_checks }}')
        failed=Environment(autoescape=True).compile_expression(health['failed_when'])
        for result,expected in [
            ({'rc':0,'stdout':'{"server_version":"fixture-version"}'},False),
            ({'rc':60,'stdout':'{"server_version":"fixture-version"}'},True),
            ({'rc':22,'stdout':'missing router'},True),
            ({'rc':0,'stdout':'<html>Other application</html>'},True),
        ]:
            with self.subTest(result=result):
                self.assertEqual(failed(ordinary_health=result,item=route),expected)

    def test_music_https_probe_has_only_the_exact_home_egress(self):
        overlay=compiler.read(ROOT/'site.example.yaml')
        overlay['values'].update({'addresses.ingress_frontend':'198.18.40.133',
                                  'addresses.music_home':'198.19.100.240'})
        packets=self.packets(overlay)
        cfg=json.loads(packets['music']['files']['site.json'])
        rules=cfg['guest']['rules']
        expected={'direction':'out','proto':'tcp','port':'443',
                  'source':'198.19.100.240/32','destination':'198.18.40.133/32',
                  'interface':'net2','comment':'Music HTTPS route health from its allowed Home address'}
        self.assertEqual([rule for rule in rules if rule.get('comment')==expected['comment']],[expected])
        self.assertEqual(cfg['app']['frontend_routing']['address'],'198.19.100.240/24')
        flow=connections.Connection('music','ingress','198.19.100.240','198.18.40.133','tcp',443)
        self.assertTrue(connections.permits(rules,'out',flow,interface='net2'))
        self.assertFalse(connections.permits(rules,'out',flow,interface='net0'))
        ingress=json.loads(packets['ingress']['files']['site.json'])
        self.assertTrue(connections.permits(ingress['guest']['rules'],'in',flow,
                        interface=connections.network_endpoints.firewall_interface(ingress['guest'],flow.target_address)))
        for changed in ({'source_address':'198.19.100.239'},
                        {'target_address':'198.18.40.134'},
                        {'port':80},{'protocol':'udp'}):
            with self.subTest(changed=changed):
                other=connections.Connection(**(flow.__dict__|changed))
                self.assertFalse(connections.permits(rules,'out',other,interface='net2'))

    def test_music_route_uses_only_selected_lan_vpn_and_exact_tablet_clients(self):
        packets=self.packets();cfg=json.loads(packets['music']['files']['site.json'])
        ingress=json.loads(packets['ingress']['files']['stack.json'])
        policy=ingress['routing']['middlewares']['music-clients']
        self.assertEqual(policy,{'ipAllowList':{'sourceRange':['198.18.10.0/28','198.19.100.0/24']}})
        self.assertEqual(discovery.labels(cfg)['traefik.http.routers.music.middlewares'],
                         'security-headers@file,music-clients@file')
        overlay=compiler.read(ROOT/'site.example.yaml')
        ranges=['198.18.10.0/28','198.18.11.0/28','198.19.100.0/24',
                '198.19.101.0/24','198.19.102.0/24','198.19.150.0/24',
                '198.19.107.15/32','198.19.107.27/32','198.19.107.28/32']
        overlay['guests']['ingress']={'stack':{'routing':{'middlewares':{
            'music-clients':{'ipAllowList':{'sourceRange':ranges}}}}}}
        packets=self.packets(overlay)
        ingress=json.loads(packets['ingress']['files']['stack.json'])
        actual=ingress['routing']['middlewares']['music-clients']['ipAllowList']['sourceRange']
        self.assertEqual(actual,ranges)
        networks=[ipaddress.ip_network(value)for value in actual]
        for address,permitted in [('198.18.10.14',True),('198.18.11.15',True),
                                  ('198.19.100.30',True),('198.19.101.30',True),
                                  ('198.19.102.30',True),('198.19.150.30',True),
                                  ('198.19.107.15',True),('198.19.107.27',True),
                                  ('198.19.107.28',True),('198.18.10.16',False),
                                  ('198.18.11.16',False),('198.19.107.14',False),
                                  ('198.19.107.26',False),('198.19.107.29',False),
                                  ('198.18.25.11',False),('198.18.40.99',False),('8.8.8.8',False)]:
            with self.subTest(address=address):
                self.assertEqual(any(ipaddress.ip_address(address)in network for network in networks),permitted)
        labels=discovery.labels(json.loads(packets['music']['files']['site.json']))
        self.assertEqual(labels['traefik.http.routers.music.priority'],'10')
        self.assertEqual(labels['traefik.http.routers.music.rule'],'Host(`music.example.invalid`)')
        self.assertFalse(any('tablets' in key or 'bypass' in key for key in labels))

    def test_only_new_broker_owns_dns_and_all_declared_consumers_follow_its_address(self):
        overlay=compiler.read(ROOT/'site.example.yaml')
        overlay['values'].update({'addresses.mqtt_backend':'198.18.30.137',
                                  'addresses.mqtt_frontend':'198.18.41.121'})
        packets=self.packets(overlay)
        dns=json.loads(packets['dns']['files']['stack.json'])
        self.assertEqual(dns['dns_records']['broker.mqtt'],'198.18.41.121')
        for name,applications in [('automation',['homeassistant','node_red']),
                                  ('zigbee2mqtt',['zigbee2mqtt','winet'])]:
            cfg=json.loads(packets[name]['files']['site.json'])
            stack=json.loads(packets[name]['files']['stack.json'])
            for application in applications:
                self.assertEqual(cfg['app']['service_connections'][application],
                                 {'service':'mqtt.mqtt','address':'backend'})
                self.assertEqual(stack['services'][application]['extra_hosts']['broker.mqtt'],'198.18.30.137')
        mqtt=json.loads(packets['mqtt']['files']['stack.json'])
        self.assertEqual(mqtt['mqtt']['credential_file'],'/var/lib/homelab-inputs/mqtt-probe.json')
        self.assertEqual(mqtt['services']['mqtt']['image'],
                         'eclipse-mosquitto@sha256:077fe4ff4c49df1e860c98335c77dda08360629e0e2a718147027e4db3eace9d')
        probe=json.loads(packets['mqtt']['files']['site.json'])['app']['service_health_checks']['mqtt'][0]
        self.assertEqual(probe['argv'][-1],'mqtt-broker')
        self.assertEqual(probe['expect'],'"read_only_probe": "passed"')

    def test_broker_rules_admit_only_named_backend_clients_and_preserve_current_client_ports(self):
        cfg=self.cfgs();rules=cfg['mqtt']['guest']['rules']
        for source,target,interface,port,expected in [
            ('198.18.30.21','198.18.30.37','net1',1883,True),
            ('198.18.30.22','198.18.30.37','net1',1883,True),
            ('198.18.30.99','198.18.30.37','net1',1883,False),
            ('198.18.30.21','198.18.30.37','net1',8000,False),
            ('198.19.100.10','198.18.41.21','net2',1883,True),
            ('198.19.107.10','198.18.41.21','net2',8000,True),
            ('198.18.40.4','198.18.41.21','net2',1883,True),
            ('198.18.40.6','198.18.41.21','net2',1883,True),
            ('198.18.40.99','198.18.41.21','net2',1883,False),
            ('198.19.100.10','198.18.41.21','net2',22,False),
        ]:
            with self.subTest(source=source,target=target,port=port):
                flow=connections.Connection('client','mqtt',source,target,'tcp',port)
                self.assertEqual(connections.permits(rules,'in',flow,interface),expected)
        self.assertEqual([n['bridge']for n in cfg['automation']['guest']['interfaces']],
                         ['vmbr0','vmbr30','vmbr1','vmbr1','vmbr32','vmbr33'])
        self.assertEqual(cfg['automation']['guest']['interfaces'][2]['ipv4'],'198.18.40.21/24')
        self.assertFalse(any(r['direction']=='in'and r.get('port') in {'1883','1883,8000'}
                             for r in cfg['automation']['guest']['rules']))

    def test_duplicate_broker_or_missing_music_proxy_rule_refuses_before_admission(self):
        overlay=compiler.read(ROOT/'site.example.yaml')
        mqtt=compiler.read(ROOT/'guests/mqtt/profile.yaml')
        with tempfile.TemporaryDirectory() as directory:
            fixture=Path(directory)/'stack'
            shutil.copytree(ROOT,fixture,ignore=shutil.ignore_patterns('.git','__pycache__','.work'))
            path=fixture/'guests/automation/profile.yaml';shared=compiler.read(path)
            shared['config']['app']['service_health_checks']['mqtt']=mqtt['config']['app']['service_health_checks']['mqtt']
            shared['config']['app']['published_services']={'mqtt':dict(mqtt['config']['app']['published_services']['mqtt'],
                addresses={'frontend':'${addresses.automation_frontend}','backend':'${addresses.automation_backend}'})}
            shared['stack']['services']['mqtt']=mqtt['stack']['services']['mqtt']
            path.write_text(json.dumps(shared))
            with self.assertRaisesRegex(ValueError,'unique hostname'):
                compiler.compile_stack(fixture,overlay,[])
        for name,direction in [('music','in'),('ingress','out')]:
            overlay=compiler.read(ROOT/'site.example.yaml')
            rules=compiler.read(ROOT/'guests'/name/'profile.yaml')['config']['guest']['rules']
            overlay['guests'][name]={'config':{'guest':{'rules':[
                r for r in rules if not(r['direction']==direction and r.get('port')=='8095'
                    and (r.get('source')=='${addresses.ingress_management}/32'if direction=='in'else True))]}}}
            with self.subTest(guest=name),self.assertRaisesRegex(ValueError,name+' '+direction+' firewall'):
                self.packets(overlay)


if __name__=='__main__':unittest.main()
