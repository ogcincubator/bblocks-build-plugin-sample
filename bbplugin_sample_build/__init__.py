"""
Sample bblocks build (postprocessing lifecycle) plugin.

SampleBuildHooks implements every event in the build-plugin contract
(docs/build-lifecycle-hooks.md in bblocks-postprocess-action) purely to
demonstrate the mechanism end to end:

  - before_run / after_uplift / after_run / on_error: log what they see -
    pure observers, no return value.
  - before_bblock / after_bblock: log stage + bblock identifier for all five
    per-bblock stages (ANNOTATE, JSONLD, FINALIZE, TRANSFORMS, DOC) - also
    observers; the contract does not let them mutate metadata mid-pipeline.
  - after_register: the *only* mutation point in the contract. Stamps an
    'x-sampleBuildPlugin' extension field on the top-level register and on
    every bblock entry, recording when this plugin ran and how many bblocks
    it saw. This is the mechanism to use for rewriting register.json / a
    bblock's published metadata from a build plugin - see the design doc's
    "Proposed events" section.

Declare in bblocks-config.yaml:

    plugins:
      build:
        - classes: [bbplugin_sample_build.SampleBuildHooks]
          pip: git+https://github.com/ogcincubator/bblocks-build-plugin-sample.git
"""
from datetime import datetime, timezone


class SampleBuildHooks:

    def before_run(self, register, context):
        print(f"[sample-build] before_run: {len(register.get('bblocks', []))} bblock(s) queued, "
              f"steps={context.get('steps')}")

    def before_bblock(self, stage, bblock, register, context):
        print(f"[sample-build] before_bblock: stage={stage} id={bblock.get('identifier')} "
              f"urlsResolved={bblock.get('urlsResolved')}")

    def after_bblock(self, stage, bblock, register, context):
        print(f"[sample-build] after_bblock: stage={stage} id={bblock.get('identifier')} "
              f"urlsResolved={bblock.get('urlsResolved')}")

    def after_register(self, register, context):
        """The one mutation point in the contract: stamp an 'x-sampleBuildPlugin'
        extension field on the register and on every bblock entry."""
        timestamp = datetime.now(timezone.utc).isoformat()
        result = dict(register)
        bblocks = [dict(b) for b in result.get('bblocks', [])]
        for b in bblocks:
            b['x-sampleBuildPlugin'] = {
                'processedAt': timestamp,
                'note': 'stamped by bbplugin-sample-build.SampleBuildHooks.after_register',
            }
        result['bblocks'] = bblocks
        result['x-sampleBuildPlugin'] = {
            'processedAt': timestamp,
            'bblockCount': len(bblocks),
        }
        print(f"[sample-build] after_register: stamped {len(bblocks)} bblock(s)")
        return result

    def after_uplift(self, register, context):
        print("[sample-build] after_uplift")

    def after_run(self, register, context):
        print("[sample-build] after_run: run completed successfully")

    def on_error(self, error, register, context):
        print(f"[sample-build] on_error: phase={error.get('phase')} "
              f"type={error.get('type')} message={error.get('message')}")
