// Exercise Renovate itself; derive dependencies from the authoritative catalogue.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import RE2 from './node_modules/re2/re2.js';
import {fileURLToPath} from 'node:url';
import {extractPackageFile} from './node_modules/renovate/dist/modules/manager/custom/regex/index.js';
import {doAutoReplace} from './node_modules/renovate/dist/workers/repository/update/branch/auto-replace.js';
import {GlobalConfig} from './node_modules/renovate/dist/config/global.js';
import {init} from './node_modules/renovate/dist/logger/index.js';
await init();
const root=fileURLToPath(new URL('../../', import.meta.url));
const config=JSON.parse(fs.readFileSync(path.join(root,'renovate.json')));
assert.deepEqual(config.enabledManagers,['custom.regex']);
assert.equal(config.automerge,false);
assert.equal(config.platformAutomerge,false);
assert.equal(config.platformCommit,'enabled');
assert.equal(config.pinDigests,true);
const manager=config.customManagers[0];
for(const pattern of manager.matchStrings) new RE2(pattern);
const raw=fs.readFileSync(path.join(root,'images.json'),'utf8');
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'renovate-catalogue-'));
GlobalConfig.set({localDir:scratch});
async function check(text, tagChange=false) {
  const catalogue=JSON.parse(text);
  const registry=Object.entries(catalogue).filter(([,value])=>value.repository);
  const actual=extractPackageFile(text,'images.json',manager);
  assert.deepEqual(actual.deps.map(x=>x.depName),registry.map(([,x])=>x.repository));
  for(const [depIndex,dep]of actual.deps.entries()) {
    const [key,before]=registry[depIndex];
    assert.equal(dep.currentValue,before.tag??undefined);
    assert.equal(dep.currentDigest,before.digest??undefined);
    const newDigest='sha256:'+'a'.repeat(64);
    const newValue=tagChange?'2.0.0':dep.currentValue;
    const changed=await doAutoReplace({...manager,...actual,...dep,manager:'regex',
      packageFile:'images.json',depIndex,newDigest,newValue,
      updateType:tagChange?'major':dep.currentDigest?'digest':'pinDigest'},text,false);
    const expected=structuredClone(catalogue);
    expected[key].digest=newDigest;
    if(tagChange)expected[key].tag=newValue;
    assert.deepEqual(JSON.parse(changed),expected);
  }
  return registry.length;
}
try {
  const count=await check(raw);
  // New entries are discovered automatically; tags and digest pins replace one record only.
  const future=JSON.parse(raw);
  future.future_image={repository:'registry.example.invalid/owner/new-image',tag:'1.0.0',digest:null};
  await check(JSON.stringify(future,null,2));
  await check(JSON.stringify({future_image:future.future_image,private_archive:{
    local_id:'sha256:'+'b'.repeat(64),archive:'/example/private.tar',archive_sha256:'c'.repeat(64)}},null,2),true);
  console.log(`Actual Renovate extraction and replacements passed for ${count} registry images, new records, tag changes and archive preservation.`);
} finally {
  fs.rmSync(scratch,{recursive:true,force:true});
}
