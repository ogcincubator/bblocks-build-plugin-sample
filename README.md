# bblocks-build-plugin-sample

A sample [build (postprocessing lifecycle) plugin](https://github.com/opengeospatial/bblocks-postprocess-action/blob/develop/docs/build-lifecycle-hooks.md)
for [bblocks-postprocess-action](https://github.com/opengeospatial/bblocks-postprocess-action).

`bbplugin_sample_build.SampleBuildHooks` implements every event in the
contract — `before_run`, `before_bblock`/`after_bblock` (all five per-bblock
stages), `after_register`, `after_uplift`, `after_run`, `on_error` — logging
each one. `after_register` also demonstrates the contract's one mutation
point: it stamps an `x-sampleBuildPlugin` extension field onto the register
and onto every bblock entry.

## Usage

Declare it under `plugins.build` in a register's `bblocks-config.yaml`:

```yaml
plugins:
  build:
    - classes: [bbplugin_sample_build.SampleBuildHooks]
      pip: git+https://github.com/ogcincubator/bblocks-build-plugin-sample.git
```
