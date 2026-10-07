"""
Sample bblocks build (postprocessing lifecycle) plugin.

SampleBuildHooks implements every event in the build-plugin contract exposed by
bblocks-postprocess-action's `plugins.build` mechanism, purely to demonstrate the
mechanism end to end:

  - before_run / after_uplift / after_run / on_error: log what they see -
    pure observers, no return value.
  - before_bblock / after_bblock: log stage + bblock identifier for all five
    per-bblock stages (ANNOTATE, JSONLD, FINALIZE, TRANSFORMS, DOC) - also
    observers; the contract does not let them mutate metadata mid-pipeline.
  - after_register: the *only* mutation point in the contract. Stamps an
    'x-sampleBuildPlugin' extension field on the top-level register and on
    every bblock entry, recording when this plugin ran and how many bblocks
    it saw. This is the mechanism to use for rewriting register.json / a
    bblock's published metadata from a build plugin - it is the only event
    whose return value feeds back into the pipeline.

Declare in bblocks-config.yaml:

    plugins:
      build:
        - id: sample                # optional; reaches the plugin as context['pluginId']
          classes: [bbplugin_sample_build.SampleBuildHooks]
          pip: git+https://github.com/ogcincubator/bblocks-build-plugin-sample.git
          config:                   # optional; passed to the constructor as a dict
            greeting: hello

`config` (a JSON-serializable mapping) is handed to the constructor as a single
positional dict - this sample just prints it - and every event's `context` carries
`rootDir` (the directory the run's other paths are relative to) and `pluginId`.
"""
from datetime import datetime, timezone


class SampleBuildHooks:

    def __init__(self, config=None):
        # Only called with an argument when the declaring entry has a non-empty
        # `config`; with none, the postprocessor calls SampleBuildHooks().
        self.config = config or {}

    def before_run(self, register, context):
        print(f"[sample-build] before_run: pluginId={context.get('pluginId')} "
              f"rootDir={context.get('rootDir')} config={self.config!r}")
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
