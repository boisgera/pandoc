Update pandoc type registry
================================================================================

The `pandoc-types.js` file of the source tree stores:
  - the version dependencies between `pandoc` and `pandoc-types`,
  - the Haskell definitions of the pandoc types for each version.

To update this file when new pandoc releases appear, 
install [pixi](https://pixi.sh) if needed, then run

```
$ pixi run build
```

It will generate an updated version of `pandoc-types.js` in the local directory. 

Examine/modify it, then when you are satisfied, copy it in `../src/pandoc/`.

